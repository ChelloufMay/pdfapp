# documents/models.py
import os
import uuid
import mimetypes
from django.db import models


def upload_to_uploads(instance, filename):
    """
    Place uploads in MEDIA_ROOT/uploads/<filename>
    """
    return os.path.join('uploads', filename)


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # UUID primary key
    file = models.FileField(upload_to=upload_to_uploads, null=True, blank=True) # uploaded file (FileField)
    fileName = models.CharField(max_length=512, blank=True)# original filename (for display)
    creationDate = models.DateTimeField(auto_now_add=True)# timestamp of creation


    # store the raw extracted text; default '' avoids migration prompts
    data = models.TextField(blank=True, default='', help_text="Extracted raw text")

    # keywords: JSON list (default empty list)
    keywords = models.JSONField(blank=True, default=list, help_text="List of unique keywords")

    # mapping keyword -> score (default empty dict)
    keyword_scores = models.JSONField(blank=True, default=dict, help_text="Mapping keyword -> extractor score")

    # detected language code
    language = models.CharField(max_length=8, blank=True, help_text="Language code detected (e.g. en, fr, ar)")

    fileSize = models.BigIntegerField(null=True, blank=True)
    contentType = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['-creationDate']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        name = self.fileName or (self.file.name if self.file else 'unnamed')
        return f"{name} ({self.id})"

    @property

    #Return file URL if available (useful for serializers/frontends).
    def file_url(self):
        try:
            return self.file.url
        except Exception:
            return ''

    # ensure fileName is set from the file if missing + persist, then fill fileSize and contentType metadata if possible
    def save(self, *args, **kwargs):
        if self.file and not self.fileName:
            self.fileName = os.path.basename(self.file.name)

        # initial save/write of file if new
        super().save(*args, **kwargs)

        changed = False

        # fileSize from the stored file
        if self.file and (self.fileSize is None):
            try:
                self.fileSize = self.file.size
                changed = True
            except Exception:
                pass

        # guess MIME type from file path if missing
        if self.file and not self.contentType:
            guessed_type = None
            try:
                if hasattr(self.file, 'path'):
                    guessed_type, _ = mimetypes.guess_type(self.file.path)
                # uploaded file objects sometimes carry content_type
                if not guessed_type and hasattr(self.file, 'file') and hasattr(self.file.file, 'content_type'):
                    guessed_type = getattr(self.file.file, 'content_type', None)
                if guessed_type:
                    self.contentType = guessed_type
                    changed = True
            except Exception:
                pass

        if changed:
            try:
                # persist only changed metadata fields
                super().save(update_fields=['fileSize', 'contentType'])
            except Exception:
                super().save()
