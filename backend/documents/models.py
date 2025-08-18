# documents/models.py
"""
Document model for the `pdfapp` project.
This model represents an uploaded document and stores:
"""

import os
import uuid
import mimetypes
from django.db import models


def upload_to_uploads(instance, filename):
    """
    FileField upload path function.
    Files will be stored in MEDIA_ROOT/uploads/<filename>.
    """
    return os.path.join('uploads', filename)

#Document model that stores uploaded files and extracted text.
class Document(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Actual file stored in MEDIA_ROOT/uploads/ This field holds the uploaded file itself.
    file = models.FileField(upload_to=upload_to_uploads, null=True, blank=True)

    # The original filename (kept for convenience). We store it separately because FileField's name might change or be normalized.
    fileName = models.CharField(max_length=512, blank=True)

    # Automatically set when the model instance is created.
    creationDate = models.DateTimeField(auto_now_add=True)

    # The extracted text from the document .
    data = models.TextField(blank=True)

    # File size in bytes.
    fileSize = models.BigIntegerField(null=True, blank=True)

    # MIME content type. attempt to guess this automatically when the file is saved.
    contentType = models.CharField(max_length=128, blank=True)

    class Meta:
        # Default ordering (newest first) when querying without explicit ordering
        ordering = ['-creationDate']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'



    def __str__(self):
        # Human-readable representation shown in admin and logs
        name = self.fileName or (self.file.name if self.file else 'unnamed')
        return f"{name} ({self.id})"

    @property
    def file_url(self):
        # Return file URL if available (useful for serializers)
        try:
            return self.file.url
        except Exception:
            return ''

    def save(self, *args, **kwargs):
        """
        Override save to:
          - Ensure fileName is set from uploaded file if it's missing.
          - Save first so that the file exists on disk, then try to determine fileSize and MIME type.
          - If fileSize/contentType get determined after initial save, update those fields.
        """
        # If a file is attached and fileName is empty, set fileName from the upload.
        if self.file and not self.fileName:
            self.fileName = os.path.basename(self.file.name)

        # Call the parent's save the first time to ensure the file is written to disk.
        super().save(*args, **kwargs)

        # fill derived metadata if missing.
        changed = False

        # set fileSize if not already set
        if self.file and (self.fileSize is None):
            try:
                # FieldFile.size will return the size in bytes
                self.fileSize = self.file.size
                changed = True
            except Exception:
                # If something fails (rare), we simply skip it
                pass

        # set contentType (MIME) if it's empty
        if self.file and not self.contentType:
            guessed_type = None
            try:
                # Prefer guessing from the stored file path (best-effort)
                if hasattr(self.file, 'path'):
                    guessed_type, _ = mimetypes.guess_type(self.file.path)
                # If guess failed and uploaded file object carries content_type, use it
                if not guessed_type:
                    # UploadedFile sometimes stores content_type on the underlying file object.
                    if hasattr(self.file, 'file') and hasattr(self.file.file, 'content_type'):
                        guessed_type = getattr(self.file.file, 'content_type', None)
                if guessed_type:
                    self.contentType = guessed_type
                    changed = True
            except Exception:
                # If anything goes wrong guessing, continue without setting contentType
                pass

        # If we set either fileSize or contentType, save those fields back to DB.
        # Use update_fields to avoid re-saving the file and to be efficient.
        if changed:
            try:
                super().save(update_fields=['fileSize', 'contentType'])
            except Exception:
                # If update_fields fails for any reason, fall back to a full save.
                super().save()
