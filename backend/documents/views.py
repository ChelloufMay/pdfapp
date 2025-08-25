# documents/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .utils.extractors import extract_text_from_pdf
from .utils.keywords import extract_keywords
from django.http import FileResponse, Http404
import os
from django.db.models import Q

class DocumentViewSet(viewsets.ModelViewSet):
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

        # IMPORTANT: set a non-null placeholder for `data` BEFORE the initial save.
        # This prevents IntegrityError if the DB column is currently NOT NULL.
        doc.data = []  # empty keywords list until we compute them

        # Save the instance (file will be written to disk)
        doc.save()

        # read bytes for extractor (best-effort)
        file_path = getattr(doc.file, 'path', None)
        try:
            file_bytes = None
            if file_path:
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
        except Exception:
            file_bytes = None

        # extract text and compute keywords
        extracted_text = extract_text_from_pdf(file_path=file_path, file_bytes=file_bytes) or ''
        keywords = extract_keywords(extracted_text, top_n=40)

        # store keywords array in data JSONField (replace placeholder)
        doc.data = keywords
        doc.save(update_fields=['data'])

        serializer = self.get_serializer(doc, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        q = request.GET.get('q', '').strip()
        if not q:
            return Response({'detail': 'Query param q is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # simple search: fileName OR keyword word in data (JSON) - for JSONField lookup we use string match on data
        qs = Document.objects.filter(Q(fileName__icontains=q) | Q(data__icontains=q)).order_by('-creationDate')
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
