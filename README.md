# PDF Extractor
- What this project is

PDF Extractor is a simple web application that automatically extract information from uploaded documents (PDFs and images). It extracts the main text, detects or extracts a human-friendly title, and identifies concise keywords for quick searching and inspection. The backend is built with Django + Django REST Framework and the frontend is a single-page Angular app. The project is intended for private or internal use.
## Main features
- Upload PDF and image files through an API or the web UI.
- Automatic extraction of text from each file.
- Automatic keyword extraction (language-aware) from the extracted text.
- Persistent storage of documents and metadata in a SQL database.
- Search for files by word (searches the extracted text).
- View per-document keyword statistics (percentages computed server-side).
- Download original files immediately from the UI.
## Project layout
backend/ (Django project):
- pdfapp/ (project settings and URL configuration)
- documents/ (Django app that manages Document model, serializers, views, URLs)
- models.py — Document model (file reference, filename, creation date, data, keywords, language, size, content type, title)
- serializers.py — converts model instances to JSON for the API
- views.py — API endpoints (upload, list, retrieve, delete, search, keyword-stats, download)
- utils/ — extraction utilities
- extractors.py — text extraction and title heuristics (PyPDF2, optional OCR path)
- keywords.py — keyword extraction wrapper (YAKE-based)
- media/ — user-uploaded files stored on disk during development
- manage.py and Django config files

frontend/ (Angular application):
- src/app/core/services — DocumentService: talks to the backend API
- src/app/shared/components — reusable UI pieces (file cards, upload dialog, document viewer, etc.)
- src/app/features — page-level features (home/list, document view)
- styles and assets for UI
## Data model
Each uploaded document stores:
- a unique identifier
- a reference to the uploaded file (a file path / URL)
- original filename
- creation/upload date
- extracted text (the raw text extracted from the file)
- keywords (clean list of unique keywords)
- keyword scores (score data produced by the keyword extractor)
- language (detected language code)
- file size and MIME content type
## Main API endpoints (what they do)
- Add document (POST): accepts a file upload and returns document metadata. Extraction happens immediately after upload.
- Delete document (DELETE): removes a document by id (removes DB entry; original file deletion depends on settings).
- Get document by id (GET): returns the stored metadata for a single doc (including title, keywords, file URL).
- Get all documents (GET): returns a paginated list of documents.
- Search (GET): query parameter q used to search the extracted text and other searchable fields; returns matching files.
- Keyword statistics (GET per-document): returns keyword list with computed percentages for display.
- Download (GET per-document): returns the original file as an attachment for immediate download.

--> All endpoints are available under the API base path. The Angular frontend is configured to use these endpoints.
## How it works (flow)
1.User uploads a file through the frontend or sends it to the upload API.

2.Backend stores the file on disk (media/uploads) and creates a database record.

3.The extractor runs:
- For PDFs: attempt selectable text extraction. If the text is insufficient and OCR fallback is enabled, OCR is attempted.
- For images: OCR via pytesseract.

4.The extractor also tries to determine a short title (PDF metadata, layout heuristics, or first meaningful line of text).

5.Extracted text is sent to the keyword extractor (YAKE) to produce a list of keywords and their scores.

6.Backend persists extracted text, the list of keywords, scores, language, and title in the database.

7.Frontend lists the documents, allows viewing keyword statistics, downloading the original file, and searching.
## Tools and libraries used
Backend:
- Python and Django (Django REST Framework)
- MySQL (or SQLite for quick local testing)
- PyPDF2 and/or pdfplumber for selectable PDF text extraction
- pytesseract and Pillow for OCR (images)
- pdf2image (optional) for OCR of scanned PDFs (requires Poppler)
- YAKE for keyword extraction
- Other Python utilities and supporting libraries
Frontend:
- Angular (standalone components)
- Angular HttpClient for API communication
- Basic CSS/SCSS for layout and styling
- WebStorm recommended for frontend development
Development environment:
- PyCharm for backend development (recommended)
- WebStorm for frontend development (recommended)
- Postman or similar for API testing
