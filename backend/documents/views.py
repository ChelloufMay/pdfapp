# documents/views.py
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .utils.extractors import extract_text_from_pdf   # your extractor (with OCR fallback if enabled)
from .utils.keywords import extract_keywords_with_scores, detect_language
from django.http import FileResponse, Http404
from django.db.models import Q
from typing import Dict

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-creationDate')
    serializer_class = DocumentSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        """
        Accepts multipart/form-data with 'file'.
        - extracts text
        - detects language
        - extracts keywords with YAKE along with scores
        - stores:
          - data: extracted text (string)
          - keywords: clean unique list of keywords (lowercased)
          - keyword_scores: mapping keyword -> score (float)
        """
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        doc = Document()
        doc.file = upload
        doc.fileName = upload.name
        doc.fileSize = upload.size
        doc.contentType = upload.content_type if hasattr(upload, 'content_type') else ''
        doc.save()  # persist file to disk

        file_path = getattr(doc.file, 'path', None)
        try:
            file_bytes = None
            if file_path:
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
        except Exception:
            file_bytes = None

        # Extract text (you may have OCR fallback in extractor)
        extracted_text = extract_text_from_pdf(file_path=file_path, file_bytes=file_bytes) or ''
        # Detect language
        lang = detect_language(extracted_text) if extracted_text else None

        # Extract keywords with scores using YAKE
        kw_with_scores = extract_keywords_with_scores(extracted_text, max_ngram=3, top_k=40, lang_hint=lang)

        # Build unique keyword list and mapping {kw:score}
        keywords = []
        keyword_scores: Dict[str, float] = {}
        for kw, score in kw_with_scores:
            if kw not in keyword_scores:  # keep first occurrence
                keyword_scores[kw] = score
                keywords.append(kw)

        # Save fields
        doc.data = extracted_text
        doc.keywords = keywords
        doc.keyword_scores = keyword_scores
        doc.language = lang or ''
        doc.save(update_fields=['data', 'keywords', 'keyword_scores', 'language'])

        serializer = self.get_serializer(doc, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'], url_path='keyword-stats')
    def keyword_stats(self, request, id=None):
        """
        Return for a document a list of:
          { word, score, percent }
        where 'percent' is computed by converting YAKE scores into a normalized percentage.
        Conversion method:
          weight_i = (1 / (score_i + eps)) / sum_j (1 / (score_j + eps))
          percent = round(weight_i * 100, 1)
        (YAKE score: lower = more relevant; we use inverse to get weights.)
        """
        try:
            doc = self.get_object()
        except Exception:
            raise Http404("Document not found")

        keyword_scores = doc.keyword_scores or {}
        if not keyword_scores:
            # No keywords extracted
            return Response([])

        # Convert mapping to list and compute normalized percentages
        eps = 1e-12
        invs = []
        for kw, score in keyword_scores.items():
            sc = float(score) if score is not None else 0.0
            inv = 1.0 / (sc + eps)
            invs.append((kw, sc, inv))

        total_inv = sum(inv for (_, _, inv) in invs) or 1.0
        result = []
        for kw, sc, inv in invs:
            percent = round((inv / total_inv) * 100.0, 1)
            result.append({'word': kw, 'score': sc, 'percent': percent})

        # Optionally sort by percent descending
        result.sort(key=lambda x: x['percent'], reverse=True)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search will look in `fileName`, `data` (the extracted text), and `keywords`.
        Query param: q
        """
        q = request.GET.get('q', '').strip()
        if not q:
            return Response({'detail': 'Query param q is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Uses icontains for text fields and JSON contains for keywords in some DBs.
        # For MySQL JSON, Django will do data lookup using __icontains on JSON rendered text.
        qs = Document.objects.filter(
            Q(fileName__icontains=q) |
            Q(data__icontains=q) |
            Q(keywords__icontains=q)
        ).order_by('-creationDate')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, id=None):
        try:
            doc = self.get_object()
        except Exception:
            raise Http404("Document not found")
        if not doc.file:
            return Response({'detail': 'No file present.'}, status=status.HTTP_404_NOT_FOUND)
        file_path = doc.file.path
        if not os.path.exists(file_path):
            return Response({'detail': 'File missing on server.'}, status=status.HTTP_404_NOT_FOUND)
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=doc.fileName)
        if doc.contentType:
            response['Content-Type'] = doc.contentType
        response['Content-Length'] = str(doc.fileSize or '')
        return response
