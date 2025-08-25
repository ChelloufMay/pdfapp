# documents/utils/extractors.py
from typing import Optional
import io

def extract_text_from_pdf(file_path: Optional[str] = None, file_bytes: Optional[bytes] = None) -> str:
    """
    Basic PDF text extraction using PyPDF2.
    Returns extracted text as a string (may be empty for scanned PDFs).
    """
    try:
        from PyPDF2 import PdfReader
    except Exception:
        # PyPDF2 not installed
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
                text = page.extract_text() or ''
            except Exception:
                text = ''
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)
    except Exception:
        # Extraction failed — return empty string (caller should handle)
        return ''
