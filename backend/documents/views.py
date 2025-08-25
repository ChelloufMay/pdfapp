# documents/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .utils.extractors import extract_text_from_pdf
from .utils.keywords import extract_keywords
from django.db.models import Q
from django.http import FileResponse, Http404
import os

class DocumentViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for documents.
    - create(): accepts multipart file upload, extracts text, computes keywords,
                stores keywords in data (JSONField).
    - search: searches filename OR keywords_text (simple text search).
    - download: optional endpoint to serve file as attachment.
    """
    queryset = Document.objects.all().order_by('-creationDate')
    serializer_class = DocumentSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        doc = Document()
        doc.file = upload
        doc.fileName = upload.name
        doc.fileSize = upload.size
        doc.contentType = upload.content_type if hasattr(upload, 'content_type') else ''
        doc.save()  # saves file to disk and creates record

        # read bytes for extractor (best-effort)
        file_path = getattr(doc.file, 'path', None)
        try:
            file_bytes = None
            if file_path:
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
        except Exception:
            file_bytes = None

        # extract text (PyPDF2)
        extracted_text = extract_text_from_pdf(file_path=file_path, file_bytes=file_bytes) or ''

        # compute keywords (list of dicts) and store them in data JSONField
        keywords = extract_keywords(extracted_text, top_n=40)
        doc.data = keywords

        # store keywords_text for simple icontains searching (space-separated words)
        doc.keywords_text = " ".join([k['word'] for k in keywords])

        # save updated fields
        doc.save(update_fields=['data', 'keywords_text'])

        serializer = self.get_serializer(doc, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        /api/documents/search/?q=keyword
        returns list of documents where keyword is in keywords_text or filename (case-insensitive)
        """
        q = request.GET.get('q', '').strip()
        if not q:
            return Response({'detail': 'Query param q is required.'}, status=status.HTTP_400_BAD_REQUEST)
        qs = Document.objects.filter(Q(keywords_text__icontains=q) | Q(fileName__icontains=q)).order_by('-creationDate')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, id=None):
        """
        Optional: GET /api/documents/<id>/download/ -> returns the file as attachment
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
