# documents/api/detail.py
"""
DocumentDetailAPIView — GET / DELETE for a single document by UUID id.
"""

from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework import status

from ..models import Document
from ..serializers import DocumentSerializer


class DocumentDetailAPIView(RetrieveDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'id'  # model's PK (UUID) is "id"

    def perform_destroy(self, instance):
        # delete file from storage (if any) then delete DB row
        try:
            name = instance.file.name
            if name:
                instance.file.delete(save=False)
        except Exception:
            # swallow errors deleting the file to ensure DB row removal
            pass
        instance.delete()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Document deleted."}, status=status.HTTP_204_NO_CONTENT)

