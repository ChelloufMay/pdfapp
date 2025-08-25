# documents/models.py
import os
import uuid
import mimetypes
from django.db import models


def upload_to_uploads(instance, filename):
    return os.path.join('uploads', filename)


class Document(models.Model):
    """
    Document model. NOTE: `data` stores the extracted keywords JSON array:
      data = [
        {"word": "invoice", "count": 8, "percent": 4.0},
        ...
      ]
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    file = models.FileField(upload_to=upload_to_uploads, null=True, blank=True)
    fileName = models.CharField(max_length=512, blank=True)
    creationDate = models.DateTimeField(auto_now_add=True)

    # data is JSONField containing keywords array (replaces raw extracted text)
    data = models.JSONField(null=True, blank=True, help_text="List of keywords and their stats")

    # file metadata
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
    def file_url(self):
        try:
            return self.file.url
        except Exception:
            return ''

    def save(self, *args, **kwargs):
        # set filename if missing
        if self.file and not self.fileName:
            self.fileName = os.path.basename(self.file.name)

        # call parent to ensure file is written to disk first
        super().save(*args, **kwargs)

        changed = False
        # fill fileSize if missing
        if self.file and (self.fileSize is None):
            try:
                self.fileSize = self.file.size
                changed = True
            except Exception:
                pass

        # fill contentType if missing
        if self.file and not self.contentType:
            guessed_type = None
            try:
                if hasattr(self.file, 'path'):
                    guessed_type, _ = mimetypes.guess_type(self.file.path)
                if not guessed_type:
                    if hasattr(self.file, 'file') and hasattr(self.file.file, 'content_type'):
                        guessed_type = getattr(self.file.file, 'content_type', None)
                if guessed_type:
                    self.contentType = guessed_type
                    changed = True
            except Exception:
                pass

        if changed:
            try:
                super().save(update_fields=['fileSize', 'contentType'])
            except Exception:
                super().save()
