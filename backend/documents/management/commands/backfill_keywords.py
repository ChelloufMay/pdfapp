# documents/management/commands/backfill_keywords.py
from django.core.management.base import BaseCommand
from documents.models import Document
from documents.utils.extractors import extract_text_from_file
from documents.utils.keywords import extract_keywords_with_scores, detect_language

class Command(BaseCommand):
    help = "Re-extract text and keywords for existing documents (PDF selectable text + image OCR)."

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limit number of documents processed')

    def handle(self, *args, **options):
        limit = options.get('limit') or None
        qs = Document.objects.all().order_by('-creationDate')
        if limit:
            qs = qs[:limit]

        processed = 0
        for doc in qs:
            path = getattr(doc.file, 'path', None)
            if not path:
                self.stdout.write(f"Skipping {doc.id} (no file path)")
                continue

            # Extract text and keywords using the same production code
            text = extract_text_from_file(file_path=path, content_type=doc.contentType) or ''
            lang = detect_language(text) if text else None
            kw_with_scores = extract_keywords_with_scores(text, max_ngram=3, top_k=40, lang_hint=lang)

            keywords = []
            kw_scores = {}
            for kw, score in kw_with_scores:
                if kw not in kw_scores:
                    kw_scores[kw] = score
                    keywords.append(kw)

            doc.data = text
            doc.keywords = keywords
            doc.keyword_scores = kw_scores
            doc.language = lang or ''
            doc.save(update_fields=['data','keywords','keyword_scores','language'])
            processed += 1
            self.stdout.write(f"Processed {doc.id}: {len(keywords)} keywords")

        self.stdout.write(f"Done. Processed {processed} documents.")
