# documents/utils/extractors.py
from typing import Optional
import io
import os

def _try_pdf_text(file_path: Optional[str], file_bytes: Optional[bytes]) -> str:
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return ''
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

def _try_ocr(file_path: Optional[str], file_bytes: Optional[bytes]) -> str:
    """
    OCR fallback: convert PDF pages to images (pdf2image) and run pytesseract.
    This is slower and requires external binaries (poppler for pdf2image and Tesseract).
    """
    try:
        from pdf2image import convert_from_bytes, convert_from_path
        import pytesseract
        from PIL import Image
    except Exception:
        return ''

    images = []
    try:
        if file_bytes:
            images = convert_from_bytes(file_bytes, dpi=200)
        elif file_path:
            # convert_from_path needs poppler installed
            images = convert_from_path(file_path, dpi=200)
    except Exception:
        images = []

    text_parts = []
    for img in images:
        try:
            # pytesseract can accept PIL Image
            t = pytesseract.image_to_string(img, lang='eng+fra+ara')  # include languages you want
        except Exception:
            t = ''
        if t:
            text_parts.append(t)
    return "\n".join(text_parts)

def extract_text_from_pdf(file_path: Optional[str] = None, file_bytes: Optional[bytes] = None, use_ocr_if_empty: bool = True) -> str:
    """
    Try fast PDF text extraction first; if result empty and use_ocr_if_empty True then try OCR.
    """
    text = _try_pdf_text(file_path=file_path, file_bytes=file_bytes)
    if text and text.strip():
        return text
    if use_ocr_if_empty:
        ocr_text = _try_ocr(file_path=file_path, file_bytes=file_bytes)
        return ocr_text or ''
    return ''
