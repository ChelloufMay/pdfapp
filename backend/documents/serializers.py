# documents/serializers.py
"""
DRF serializer for Document model.
Exposes the key metadata and a helper fileUrl built from the request context.
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    # fileUrl is a convenience computed field that returns absolute URL when request present
    fileUrl = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'fileName', 'creationDate', 'data',
            'keywords', 'keyword_scores', 'language',
            'fileUrl', 'fileSize', 'contentType'
        ]

    def get_fileUrl(self, obj):
        """
        Build absolute file URL if possible.
        """
        request = self.context.get('request')
        if obj.file:
            try:
                url = obj.file.url
                if request:
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return ''
        return ''
