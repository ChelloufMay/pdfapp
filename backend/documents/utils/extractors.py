# documents/utils/extractors.py
# documents/utils/extractors.py
"""
Text extraction utility. Tries to extract with PyPDF2 first (works for text PDFs).
If no text or extraction fails and pytesseract is available + tesseract installed,
it will run OCR on each PDF page rendered as an image (requires pdf2image/pillow/pyocr).
This implementation keeps dependencies optional.
"""

from typing import Optional

def extract_text_from_pdf(file_path: Optional[str] = None, file_bytes: Optional[bytes] = None) -> str:
    text = ''
    # prefer file_path when available
    try:
        from PyPDF2 import PdfReader
        reader = None
        if file_path:
            reader = PdfReader(file_path)
        elif file_bytes:
            from io import BytesIO
            reader = PdfReader(BytesIO(file_bytes))
        if reader:
            pages = []
            for p in reader.pages:
                try:
                    pages.append(p.extract_text() or '')
                except Exception:
                    pages.append('')
            text = '\n'.join(pages).strip()
    except Exception:
        # PyPDF2 not available or extraction failed — continue to other methods
        text = ''

    if text:
        return text

    # Optional: try pdfminer
    try:
        from io import BytesIO
        from pdfminer.high_level import extract_text as pdfminer_extract_text
        if file_path:
            text = pdfminer_extract_text(file_path) or ''
        elif file_bytes:
            text = pdfminer_extract_text(BytesIO(file_bytes)) or ''
    except Exception:
        text = ''

    if text:
        return text

    # Optional OCR fallback (slow): requires tesseract & pdf2image & pytesseract
    try:
        import pytesseract
        from pdf2image import convert_from_path, convert_from_bytes
        images = []
        if file_path:
            images = convert_from_path(file_path, dpi=200)
        elif file_bytes:
            images = convert_from_bytes(file_bytes, dpi=200)
        ocr_texts = []
        for img in images:
            ocr_texts.append(pytesseract.image_to_string(img))
        text = '\n'.join(ocr_texts).strip()
    except Exception:
        # OCR failed or libs not installed
        text = ''

    return text or ''
