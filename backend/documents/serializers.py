# documents/serializers.py
"""
Serializer for Document model.
This version expects the model to use camelCase field names:
 - fileName, creationDate, fileSize, contentType, data, file, id
It exposes those same camelCase attribute names in the JSON API.
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    # fileUrl is not a model field; compute it from the FileField
    fileUrl = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Document
        # Include the model's camelCase field names
        fields = [
            'id',
            'fileName',
            'creationDate',
            'data',
            'fileUrl',
            'fileSize',
            'contentType',
            'file',  # write-only for uploads
        ]
        read_only_fields = ['id', 'fileName', 'creationDate', 'data', 'fileUrl', 'fileSize', 'contentType']
        extra_kwargs = {
            'file': {'write_only': True, 'required': False},
        }

    def get_fileUrl(self, obj):
        """
        Return absolute URL when request is available, else relative.
        """
        request = self.context.get('request')
        try:
            if obj.file:
                if request:
                    return request.build_absolute_uri(obj.file.url)
                return obj.file.url
        except Exception:
            return ''
        return ''
