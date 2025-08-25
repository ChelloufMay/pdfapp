# documents/admin.py
from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.db.models import Q
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin for Document model.
    - Displays file metadata and a short preview of the extracted keywords stored
      in `data` (JSONField).
    - Provides a custom search implementation that looks in fileName and performs
      a simple substring search against the JSON `data` (so you can search keywords).
    """

    # columns shown in the list view
    list_display = ('fileName', 'id', 'creationDate', 'fileSize', 'contentType', 'keywords_preview', 'file_link')

    # quick filters on the right sidebar
    list_filter = ('creationDate', 'contentType')

    # default search_fields should only include text-like fields that admin can search quickly.
    # We *do not* include 'data' here because it's JSON; instead we override get_search_results()
    # to search in data safely (see below).
    search_fields = ('fileName',)

    # fields that should be read-only in the admin form
    readonly_fields = ('id', 'creationDate', 'fileSize', 'contentType', 'file_link')

    # how many items per page
    list_per_page = 30

    def file_link(self, obj):
        """Return an HTML link to the file (if present)."""
        if obj.file:
            try:
                return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Download / View</a>', obj.file.url)
            except Exception:
                return "File (unavailable)"
        return "No file"
    file_link.short_description = "File"

    def keywords_preview(self, obj):
        """
        Display the top keywords stored in obj.data (which is a list of {word,count,percent} dicts).
        We show up to 5 keywords as small badges. If obj.data is not present or empty, show a hint.
        """
        raw = getattr(obj, 'data', None)
        if not raw:
            return format_html('<span style="color:#888;">No keywords</span>')

        # defensive: raw may be a JSON string or a list
        try:
            if isinstance(raw, str):
                import json
                parsed = json.loads(raw)
            else:
                parsed = raw
        except Exception:
            parsed = None

        if not parsed or not isinstance(parsed, (list, tuple)):
            return format_html('<span style="color:#888;">Invalid data</span>')

        # take first up to 5 keywords
        items = []
        for k in parsed[:5]:
            # k may be dict-like or a fallback shape
            word = k.get('word') if isinstance(k, dict) else str(k)
            pct = k.get('percent') if isinstance(k, dict) else None
            label = f"{word}" if pct is None else f"{word} ({pct}%)"
            items.append(label)

        # render as comma-separated tiny badges
        html = format_html_join(
            ' ',
            '<span style="display:inline-block;padding:2px 6px;border-radius:10px;background:#eef6ff;color:#25406a;font-size:11px;margin-right:4px;">{}</span>',
            ((it,) for it in items)
        )
        return html
    keywords_preview.short_description = "Top keywords"
    keywords_preview.allow_tags = True

    def get_search_results(self, request, queryset, search_term):
        """
        Override admin search to:
         - search fileName (icontains)
         - OR search for the substring inside the data JSON field (data__icontains)
        This lets admins type a keyword (e.g. "invoice") and find documents that include it.
        """
        # First let the default behavior handle simple cases on fileName (and other search_fields)
        qs, use_distinct = super().get_search_results(request, queryset, search_term)

        # If there is a search term, expand to include documents whose JSON `data` contains the term.
        if search_term:
            try:
                # This does a simple substring match against the JSON field.
                extra_qs = queryset.filter(Q(data__icontains=search_term) | Q(fileName__icontains=search_term))
                # Combine with the existing qs results
                qs = (qs | extra_qs).distinct()
            except Exception:
                # Some DB backends/configs may not support data__icontains; ignore in that case.
                pass

        return qs, use_distinct
