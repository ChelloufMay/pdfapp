# documents/admin.py
"""
Django admin configuration for the `Document` model.

Features:
- List view shows useful metadata (filename, short id, created date, size, MIME type, language).
- A compact "Top keywords" preview column renders up to 6 small badges for quick scanning.
- A "File" column exposes a safe link to view/download the stored file.
- Admin search has been extended to include a substring search on the JSON `data`
  (so you can search for keywords) while still using the standard `search_fields`.
- Read-only fields include metadata that should not be edited manually.
- The preview code is defensive and supports several possible shapes for `data`:
  - list of strings (preferred in the current design)
  - list of dicts (older formats that included counts/percent)
  - JSON string (serialized list)
"""

from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.db.models import Q
from .models import Document
import json
from typing import Any

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    # Columns shown in the list display
    list_display = (
        'fileName',
        'short_id',
        'creationDate',
        'fileSize',
        'contentType',
        'language',
        'keywords_preview',
        'file_link',
    )

    # Filters on the right-hand sidebar
    list_filter = ('creationDate', 'contentType', 'language')

    # Search will use fileName by default; we also override get_search_results()
    search_fields = ('fileName',)

    # Read-only metadata in the admin form
    readonly_fields = ('id', 'creationDate', 'fileSize', 'contentType', 'language', 'file_link', 'keywords_full')

    # How many items per admin page
    list_per_page = 30

    # Optional: make the id column shorter and more readable
    def short_id(self, obj: Document) -> str:
        """Show a truncated ID for readability in list view."""
        return str(obj.id)[:8] if obj and obj.id else ''
    short_id.short_description = 'ID'

    def file_link(self, obj: Document) -> str:
        """
        Return an HTML link to the file (if present). Safe: wrapped via format_html.
        This renders in both list and read-only form view.
        """
        if obj.file:
            try:
                return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">View / Download</a>', obj.file.url)
            except Exception:
                return "File (unavailable)"
        return "No file"
    file_link.short_description = "File"

    def keywords_preview(self, obj: Document) -> str:
        """
        Render a compact preview of keywords stored in obj.data.
        Accepts:
          - a Python list of strings: ['invoice', 'due date']
          - a Python list of dicts: [{'word':'invoice','count':4,'percent':1.2}, ...]
          - a JSON string representing one of the above
        Shows up to 6 badges; if there's no data, shows a muted hint.
        """
        raw = getattr(obj, 'data', None)
        if not raw:
            return format_html('<span style="color:#888;">No keywords</span>')

        # Defensive: parse JSON string if necessary
        parsed = None
        try:
            if isinstance(raw, str):
                # attempt to parse JSON string
                parsed = json.loads(raw)
            else:
                parsed = raw
        except Exception:
            parsed = None

        if not parsed or not isinstance(parsed, (list, tuple)):
            return format_html('<span style="color:#888;">Invalid data</span>')

        # Build labels for up to 6 items. Support both dict and string item shapes.
        labels = []
        for item in parsed[:6]:
            if isinstance(item, dict):
                # dict may be {word:..., count:..., percent:...} or other
                word = item.get('word') or item.get('keyword') or item.get('k') or ''
                pct = item.get('percent')
                if pct is not None:
                    label = f"{word} ({pct}%)"
                else:
                    label = f"{word}"
            else:
                # fallback: treat item as plain string
                label = str(item)
            labels.append(label)

        if not labels:
            return format_html('<span style="color:#888;">No keywords</span>')

        # Render as small inline badges
        html = format_html_join(
            ' ',
            '<span style="display:inline-block;padding:3px 8px;border-radius:999px;background:#eef6ff;color:#25406a;font-size:11px;margin-right:6px;">{}</span>',
            ((lbl,) for lbl in labels)
        )
        return html
    keywords_preview.short_description = "Top keywords"
    keywords_preview.allow_tags = True

    def keywords_full(self, obj: Document) -> str:
        """
        Read-only field to show the full JSON of keywords in the detail view.
        This is helpful for inspection when you click into a Document.
        """
        raw = getattr(obj, 'data', None)
        if not raw:
            return "(empty)"
        try:
            # Pretty-print JSON when possible
            if isinstance(raw, str):
                parsed = json.loads(raw)
            else:
                parsed = raw
            pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
            # wrap in <pre> with small styling
            return format_html('<pre style="max-width:900px; white-space:pre-wrap; font-size:12px;">{}</pre>', pretty)
        except Exception:
            # last resort: show str()
            return format_html('<pre style="font-size:12px;">{}</pre>', str(raw))
    keywords_full.short_description = "Keywords (full)"

    def get_search_results(self, request, queryset, search_term):
        """
        Extend admin search:
          - keep default behavior for fileName (and other search_fields)
          - also include documents whose JSON `data` contains the substring `search_term`
        This allows searching for keywords (simple substring match) without indexing.
        """
        qs, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            try:
                # data__icontains works for JSON/text backends where Django supports it.
                extra_qs = queryset.filter(Q(data__icontains=search_term) | Q(fileName__icontains=search_term))
                qs = (qs | extra_qs).distinct()
            except Exception:
                # If the DB backend does not support data__icontains, ignore gracefully.
                pass

        return qs, use_distinct
