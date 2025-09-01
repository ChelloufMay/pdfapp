# documents/utils/keywords.py
from typing import List, Tuple, Optional
from langdetect import detect, DetectorFactory
import yake

# Make langdetect deterministic
DetectorFactory.seed = 0

# Supported languages (you can extend)
SUPPORTED_LANGS = {'en', 'fr', 'ar'}

def detect_language(text: str) -> Optional[str]:
    try:
        return detect(text)
    except Exception:
        return None

def extract_keywords_with_scores(text: str, max_ngram: int = 3, top_k: int = 40, lang_hint: Optional[str] = None) -> List[Tuple[str, float]]:
    """
    Extract keywords with YAKE and return list of (keyword_string, score).
    Lowercase keywords before returning.
    - score: YAKE score (lower means more relevant).
    """
    if not text:
        return []

    lang = lang_hint or detect_language(text) or 'en'
    if lang not in SUPPORTED_LANGS:
        lang = 'en'

    try:
        kw_extractor = yake.KeywordExtractor(lan=lang, n=max_ngram, top=top_k)
        kw_with_scores = kw_extractor.extract_keywords(text)  # returns list of (kw, score)
        # Clean and lowercase keywords
        cleaned = [(kw.strip().lower(), float(score)) for kw, score in kw_with_scores if kw and kw.strip()]
        return cleaned
    except Exception:
        # On failure, return empty list (caller can fallback to another strategy)
        return []
