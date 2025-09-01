# documents/serializers.py
from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    fileUrl = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'fileName', 'creationDate', 'data', 'keywords', 'keyword_scores', 'language', 'fileUrl', 'fileSize', 'contentType']

    def get_fileUrl(self, obj):
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
