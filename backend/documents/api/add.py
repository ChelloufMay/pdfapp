# documents/api/add.py
"""
AddDocumentAPIView (POST /api/documents/)
Saves uploaded file, then extracts text and updates the Document record.
"""

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from ..models import Document
from ..serializers import DocumentSerializer
from ..utils.extractors import extract_text_from_pdf


class AddDocumentAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        upload = request.FILES.get('file')
        if not upload:
            return Response({"detail": "No file provided. Provide a file field in form-data."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create document using camelCase model fields
        doc = Document()
        doc.file = upload
        doc.fileName = upload.name
        try:
            doc.fileSize = upload.size
        except Exception:
            doc.fileSize = None
        try:
            doc.contentType = getattr(upload, 'content_type', '') or ''
        except Exception:
            doc.contentType = ''

        # Save once to write file to storage so path/size are available
        doc.save()

        # Try to read bytes for extraction
        file_bytes = None
        file_path = None
        try:
            if hasattr(doc.file, 'path'):
                file_path = doc.file.path
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
            else:
                # fallback to uploaded file object
                uploaded_file = doc.file
                uploaded_file.open(mode='rb')
                file_bytes = uploaded_file.read()
                uploaded_file.close()
        except Exception:
            file_bytes = None

        # Extract text and save it
        extracted = extract_text_from_pdf(file_path=file_path, file_bytes=file_bytes)
        doc.data = extracted or ''
        doc.save()

        serializer = DocumentSerializer(doc, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
