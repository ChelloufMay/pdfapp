from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .utils.extractors import extract_text_from_pdf

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-creationDate')
    serializer_class = DocumentSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        # expects multipart/form-data with 'file'
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        doc = Document()
        doc.file = upload
        doc.fileName = upload.name
        doc.fileSize = upload.size
        doc.contentType = upload.content_type if hasattr(upload, 'content_type') else ''
        doc.save()  # save to get file path

        # read bytes for extractor
        file_path = doc.file.path
        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
        except Exception:
            file_bytes = None

        extracted_text = extract_text_from_pdf(file_path=file_path, file_bytes=file_bytes)
        doc.data = extracted_text
        doc.save()

        serializer = self.get_serializer(doc, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        /api/documents/search/?q=keyword
        returns list of documents where keyword is in data (case-insensitive)
        """
        q = request.GET.get('q', '').strip()
        if not q:
            return Response({'detail': 'Query param q is required.'}, status=status.HTTP_400_BAD_REQUEST)
        qs = Document.objects.filter(data__icontains=q).order_by('-creationDate')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
