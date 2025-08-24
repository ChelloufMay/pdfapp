# documents/api/list.py
"""
DocumentListAPIView — returns all documents (most recent first).
Uses the Document model fields in camelCase (creationDate).
"""

from rest_framework.generics import ListAPIView
from ..models import Document
from ..serializers import DocumentSerializer
from rest_framework.permissions import AllowAny

class DocumentListAPIView(ListAPIView):
    # Use the actual field name that exists on your model: creationDate
    queryset = Document.objects.all().order_by('-creationDate')
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]

