# documents/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Document
from .serializers import DocumentSerializer
from .utils.extractors import extract_text_from_pdf

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-creationDate')
    serializer_class = DocumentSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]  # allow public access for listing/searching in dev

    def create(self, request, *args, **kwargs):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # create the model, save file so .file.path exists
        doc = Document()
        doc.file = upload
        doc.fileName = upload.name
        doc.fileSize = upload.size
        doc.contentType = getattr(upload, 'content_type', '')
        doc.save()  # must save to populate file.path and file.url

        file_path = ''
        try:
            file_path = doc.file.path
        except Exception:
            file_path = None

        try:
            extracted_text = extract_text_from_pdf(file_path=file_path, file_bytes=None)
        except Exception as e:
            # fallback: save empty string and log (don't crash)
            extracted_text = ''
            # you can log e here: logger.exception(e)

        doc.data = extracted_text or ''
        # store a fileUrl string for convenience (could also leave blank and use serializer)
        try:
            doc.fileUrl = request.build_absolute_uri(doc.file.url)
        except Exception:
            doc.fileUrl = doc.file.url if doc.file else ''
        doc.save()

        serializer = self.get_serializer(doc, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
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
