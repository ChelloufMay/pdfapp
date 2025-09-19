# documents/utils/extractors.py
"""
Unified extractor for:
 - selectable PDFs (uses PyPDF2 to extract text)
 - image files (JPG/PNG/TIFF/etc) using pytesseract OCR (Pillow)
"""
import os
import re
import traceback
from typing import Optional
import io

#Extract text from a PDF using PyPDF2. --> Returns empty string on errors or when no text is found.
def _try_pdf_text(file_path: Optional[str], file_bytes: Optional[bytes]) -> str:
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return ''  # PyPDF2 not available

    try:
        reader = None
        if file_bytes:
            stream = io.BytesIO(file_bytes)
            reader = PdfReader(stream)
        elif file_path:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
        else:
            return ''

        text_parts = []
        for page in reader.pages:
            try:
                t = page.extract_text() or ''
            except Exception:
                t = ''
            if t:
                text_parts.append(t)
        return "\n".join(text_parts)
    except Exception:
        return ''


#OCR an image from bytes using pytesseract + Pillow. --> If `lang` provided and tesseract has the language data installed, pass it to pytesseract.
def _image_bytes_to_text_pytesseract(img_bytes: bytes, lang: Optional[str] = None) -> str:
    try:
        from PIL import Image
        import pytesseract
    except Exception:
        return ''

    try:
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    except Exception:
        return ''

    try:
        if lang:
            return pytesseract.image_to_string(img, lang=lang)
        return pytesseract.image_to_string(img)

    except Exception:
        traceback.print_exc()
        return ''


def extract_text_from_file(file_path: Optional[str] = None,
                           file_bytes: Optional[bytes] = None,
                           content_type: Optional[str] = None,
                           use_ocr_for_images: bool = True) -> str:
    """
    Unified extractor entrypoint used by views:
    - If file is a PDF, attempt PyPDF2 extraction.
    - If file is an image, use pytesseract OCR on the image bytes.
    - If unknown, try PDF text extraction as a last resort.
    Returns '' if no text could be extracted.
    """
    ct = (content_type or '').lower()
    path_lower = (file_path or '').lower()

    is_pdf = ct.endswith('pdf') or path_lower.endswith('.pdf')
    is_image = ct.startswith('image/') or any(path_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'])

    if is_pdf:
        # Try fast selectable-text extraction
        text = _try_pdf_text(file_path=file_path, file_bytes=file_bytes)
        return text or ''

    if is_image and use_ocr_for_images:
        # Prefer bytes if available (upload flow reads them)
        if file_bytes:
            return _image_bytes_to_text_pytesseract(file_bytes)
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    bytes_ = f.read()
                return _image_bytes_to_text_pytesseract(bytes_)
            except Exception:
                traceback.print_exc()
                return ''

    # Last resort: try PDF text extraction
    text = _try_pdf_text(file_path=file_path, file_bytes=file_bytes)
    return text or ''
def _extract_title_from_pdf_metadata(file_path: Optional[str], file_bytes: Optional[bytes]) -> str:
    """
    Try to read PDF Title metadata via PyPDF2. Returns '' when not found.
    This is fast and preferred.
    """
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return ''
    try:
        if file_bytes:
            reader = PdfReader(io.BytesIO(file_bytes))
        elif file_path:
            reader = PdfReader(file_path)
        else:
            return ''
        meta = getattr(reader, 'metadata', None) or {}
        title = ''
        # common metadata keys
        for k in ('/Title', 'Title', 'title'):
            if k in meta and meta[k]:
                title = str(meta[k]).strip()
                break
        # some PdfReader implementations expose attributes
        if not title and hasattr(meta, 'title') and meta.title:
            title = str(meta.title).strip()
        return title or ''
    except Exception:
        return ''



# Backwards-compatible wrapper that returns the extracted text (string) for a PDF. Calls the canonical extract_text_from_file. Kept for legacy imports.

def extract_text_from_pdf(file_path: Optional[str] = None, file_bytes: Optional[bytes] = None, content_type: Optional[str] = None) -> str:
    return extract_text_from_file(file_path=file_path, file_bytes=file_bytes, content_type=content_type)


