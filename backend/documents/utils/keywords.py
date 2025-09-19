# documents/utils/keywords.py
"""
Wrapper around YAKE and langdetect.
"""

from typing import List, Tuple, Optional
from langdetect import detect, DetectorFactory

# Make langdetect deterministic for reproducible results
DetectorFactory.seed = 0

# YAKE supports many languages--> we default to english if detection is uncertain
DEFAULT_LANG = 'en'


#Use langdetect to guess the language. Returns None on error.
def detect_language(text: str) -> Optional[str]:
    try:
        return detect(text)
    except Exception:
        return None


def extract_keywords_with_scores(text: str, max_ngram: int = 3, top_k: int = 40, lang_hint: Optional[str] = None) -> List[Tuple[str, float]]:
    """
    Use YAKE to extract keywords with scores. YAKE returns (keyword, score) tuples.
    - text: input text
    - max_ngram: maximum words in an extracted phrase (1..3 recommended)
    - top_k: how many keywords to return at most
    - lang_hint: optional language code (en, fr, ar); if None we attempt detection
    Returns a list of (keyword_lowercased, score) ordered by YAKE's ranking.
    """
    if not text:
        return []

    try:
        import yake
    except Exception:
        return []

    lang = lang_hint or detect_language(text) or DEFAULT_LANG

    try:
        # Create a YAKE extractor with chosen language and n-gram size
        kw_extractor = yake.KeywordExtractor(lan=lang, n=max_ngram, top=top_k)
        raw = kw_extractor.extract_keywords(text)  # list of (kw, score)
        # Lowercase and strip keywords for consistency
        cleaned = [(kw.strip().lower(), float(score)) for kw, score in raw if kw and kw.strip()]
        return cleaned
    except Exception:
        return []
