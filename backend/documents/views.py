# documents/views.py
"""
REST API for Document model. Uses DRF ModelViewSet to provide:
 - list()  -> GET /api/documents/
 - retrieve() -> GET /api/documents/<id>/
 - create() -> POST /api/documents/  (multipart form with 'file')
 - destroy() -> DELETE /api/documents/<id>/
Additionally:
 - search -> GET /api/documents/search/?q=keyword
 - keyword-stats -> GET /api/documents/<id>/keyword-stats/
 - debug -> GET /api/documents/<id>/debug/ (diagnostic)
 - download -> GET /api/documents/<id>/download/
"""

import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.db.models import Q

from .models import Document
from .serializers import DocumentSerializer
from .utils.extractors import extract_text_from_file
from .utils.keywords import extract_keywords_with_scores, detect_language

# small epsilon to prevent division by zero when converting scores to weights
_EPS = 1e-12


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Document viewset: handles all CRUD plus search and stats.
    """
    queryset = Document.objects.all().order_by('-creationDate')
    serializer_class = DocumentSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        """
        Handle file upload (multipart/form-data with key 'file'):
         - save the uploaded file (Document.file)
         - extract text from file (PDF selectable text or image OCR)
         - detect language, extract keywords using YAKE
         - store data, keywords, keyword_scores, language
         - return created DocumentSerializer JSON
        """
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # create instance and save file
        doc = Document()
        doc.file = upload
        doc.fileName = upload.name
        doc.fileSize = upload.size
        doc.contentType = upload.content_type if hasattr(upload, 'content_type') else ''
        doc.save()  # ensure file is written to disk

        # read file bytes (useful for extractor)
        file_path = getattr(doc.file, 'path', None)
        file_bytes = None
        try:
            if file_path:
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
        except Exception:
            file_bytes = None

        # Use unified extractor (PDF selectable text + image OCR)
        extracted_text = extract_text_from_file(file_path=file_path, file_bytes=file_bytes, content_type=doc.contentType) or ''

        # detect language (optional) and extract keywords with YAKE
        lang = detect_language(extracted_text) if extracted_text else None
        kw_with_scores = extract_keywords_with_scores(extracted_text, max_ngram=3, top_k=40, lang_hint=lang)

        # Build unique keywords list and scores mapping
        keywords = []
        keyword_scores = {}
        for kw, score in kw_with_scores:
            if kw not in keyword_scores:
                keyword_scores[kw] = score
                keywords.append(kw)

        # Save fields back to DB
        doc.data = extracted_text
        doc.keywords = keywords
        doc.keyword_scores = keyword_scores
        doc.language = lang or ''
        doc.save(update_fields=['data', 'keywords', 'keyword_scores', 'language'])

        serializer = self.get_serializer(doc, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search endpoint: searches fileName, data (extracted text), and keywords list.
        Example: GET /api/documents/search/?q=invoice
        """
        q = request.GET.get('q', '').strip()
        if not q:
            return Response({'detail': 'Query param q is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Simple icontains search across fields
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

    @action(detail=True, methods=['get'], url_path='keyword-stats')
    def keyword_stats(self, request, id=None):
        """
        Return keywords with score and normalized percent.
        Conversion uses inverse-score normalization:
            weight_i = (1 / (score_i + eps)) / sum_j (1 / (score_j + eps))
            percent = round(weight_i * 100, 1)
        This treats lower YAKE scores as more relevant.
        """
        try:
            doc = self.get_object()
        except Exception:
            raise Http404("Document not found")

        keyword_scores = doc.keyword_scores or {}
        if not keyword_scores:
            return Response([])

        invs = []
        for kw, score in keyword_scores.items():
            sc = float(score) if score is not None else 0.0
            inv = 1.0 / (sc + _EPS)
            invs.append((kw, sc, inv))

        total_inv = sum(inv for (_, _, inv) in invs) or 1.0
        result = []
        for kw, sc, inv in invs:
            percent = round((inv / total_inv) * 100.0, 1)
            result.append({'word': kw, 'score': sc, 'percent': percent})

        # sort by percent desc so UI can show strongest keywords first
        result.sort(key=lambda x: x['percent'], reverse=True)
        return Response(result)

    @action(detail=True, methods=['get'], url_path='debug')
    def debug(self, request, id=None):
        """
        Diagnostic endpoint to inspect extractor output:
        Returns:
         - extracted_text_length
         - sample_text (first N chars)
         - stored keywords and their tokenized form (helps debug matches)
        Useful to see whether OCR / extraction produced text.
        """
        try:
            doc = self.get_object()
        except Exception:
            raise Http404("Document not found")

        file_path = getattr(doc.file, 'path', None)
        if not file_path or not os.path.exists(file_path):
            return Response({'detail': 'File missing on server.'}, status=status.HTTP_404_NOT_FOUND)

        extracted = extract_text_from_file(file_path=file_path, content_type=doc.contentType) or ''
        sample = extracted[:2000]
        token_sample = []
        try:
            import re
            tokens = re.findall(r"[^\W_]+", (extracted or '').lower(), flags=re.UNICODE)
            token_sample = tokens[:200]
        except Exception:
            token_sample = []

        stored_keywords = doc.keywords or []
        keyword_details = []
        for kw in stored_keywords:
            # show keyword tokens and an attempt count (re-counting here is optional)
            kw_tokens = []
            try:
                import re
                kw_tokens = re.findall(r"[^\W_]+", kw.lower(), flags=re.UNICODE)
            except Exception:
                kw_tokens = []
            keyword_details.append({'word': kw, 'tokens': kw_tokens})

        return Response({
            'extracted_text_length': len(extracted),
            'sample_text': sample,
            'token_count': len(token_sample),
            'tokens_sample': token_sample,
            'stored_keywords': stored_keywords,
            'keyword_details': keyword_details,
        })

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, id=None):
        """
        Serve the uploaded file as an attachment (download).
        """
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
