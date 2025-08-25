# documents/utils/keywords.py
import re
from collections import Counter
# documents/utils/keywords.py
import re
from collections import Counter
from typing import List, Dict

STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","at","by","for","with","about",
    "against","between","into","through","during","before","after","above","below","to","from",
    "up","down","in","out","on","off","over","under","again","further","here","there","all",
    "any","both","each","few","more","most","other","some","such","no","nor","not","only",
    "own","same","so","than","too","very","can","will","just","should","now","is","are","was",
    "were","be","been","being","have","has","had","do","does","did","of","as","i","you","he",
    "she","it","we","they","this","that","these","those","your","their","its","my","me","our",
}

WORD_RE = re.compile(r"[a-zA-Z0-9']{2,}")

def extract_keywords(text: str, top_n: int = 30) -> List[Dict]:
    if not text:
        return []

    text_low = text.lower()
    words = WORD_RE.findall(text_low)
    filtered = [w for w in words if w not in STOPWORDS]
    total = len(filtered)
    if total == 0:
        return []

    counts = Counter(filtered)
    most = counts.most_common(top_n)

    result = []
    for word, cnt in most:
        pct = round((cnt / total) * 100, 1)
        result.append({"word": word, "count": cnt, "percent": pct})
    return result
