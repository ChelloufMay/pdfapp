# documents/utils/extractors.py
import io
from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

# Optional OCR imports may not be available — import lazily
try:
    from pdf2image import convert_from_bytes
    import pytesseract
    OCR_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    OCR_AVAILABLE = False


def extract_text_from_pdf(file_path=None, file_bytes=None):
    text = ''

    # 1) pdfminer extraction (works with file-like objects)
    try:
        if file_bytes:
            text = extract_text(io.BytesIO(file_bytes))
        else:
            text = extract_text(file_path)
        if text and text.strip():
            return text
    except (OSError, IOError) as err:
        # File I/O problems
        # You may log the error here: logger.exception("pdfminer I/O error")
        pass
    except Exception:
        # pdfminer can raise library-specific errors; for safety we fallback to PyPDF2
        # We avoid re-raising so extraction can continue to other methods.
        pass

    # 2) PyPDF2 fallback (page-by-page text extraction)
    try:
        if file_bytes:
            reader = PdfReader(io.BytesIO(file_bytes))
        else:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)

        pages_text = []
        for p in reader.pages:
            # PdfReadError can be raised when reading malformed pages
            try:
                pages_text.append(p.extract_text() or '')
            except PdfReadError:
                pages_text.append('')
            except Exception:
                # If extraction for a page fails, skip it
                pages_text.append('')
        text = "\n".join(pages_text).strip()
        if text:
            return text
    except PdfReadError:
        # corrupted PDF structure; fall through to OCR (if available)
        pass
    except (OSError, IOError):
        # file I/O problems, fallthrough
        pass
    except Exception:
        # Unexpected errors — fallback to OCR if available
        pass

    # 3) OCR fallback — only attempt if OCR libs are installed
    if OCR_AVAILABLE:
        try:
            images = convert_from_bytes(file_bytes if file_bytes else open(file_path, 'rb').read())
            text_parts = []
            for img in images:
                # pytesseract can raise TesseractNotFoundError if tesseract is not installed
                try:
                    text_parts.append(pytesseract.image_to_string(img))
                except (RuntimeError, OSError):
                    # OCR failed for this image — skip it
                    text_parts.append('')
                except Exception:
                    text_parts.append('')
            text = "\n".join(text_parts).strip()
            return text
        except (OSError, IOError):
            # problems reading images / poppler missing
            pass
        except Exception:
            # any other exception — give up gracefully
            pass

    # Nothing extracted
    return ''
