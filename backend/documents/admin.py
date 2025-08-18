# documents/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('fileName', 'id', 'creationDate', 'fileSize', 'contentType', 'file_link')
    list_filter = ('creationDate', 'contentType')
    search_fields = ('fileName', 'data')
    readonly_fields = ('id', 'creationDate', 'fileSize', 'contentType', 'file_link')

    def file_link(self, obj):
        if obj.file:
            try:
                return format_html('<a href="{}" target="_blank" rel="noopener">Download/View</a>', obj.file.url)
            except Exception:
                return "File (unavailable)"
        return "No file"
    file_link.short_description = "File"

