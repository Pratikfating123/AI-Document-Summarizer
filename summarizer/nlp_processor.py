import re
from collections import Counter

DEFAULT_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can", "could", "did",
    "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no",
    "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "why", "will", "with",
    "you", "your", "yours", "yourself", "yourselves"
}


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    clean = normalize_text(text)
    if not clean:
        return []

    try:
        import nltk
        from nltk.tokenize import sent_tokenize

        try:
            return [s.strip() for s in sent_tokenize(clean) if s.strip()]
        except LookupError:
            pass
    except ImportError:
        pass

    # Fallback sentence splitter that needs no downloaded model.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", clean)
    return [p.strip() for p in parts if p.strip()]


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]*\b", text.lower())


def get_stopwords() -> set[str]:
    try:
        from nltk.corpus import stopwords
        try:
            return set(stopwords.words("english"))
        except LookupError:
            return DEFAULT_STOPWORDS
    except ImportError:
        return DEFAULT_STOPWORDS


def get_word_frequencies(text: str) -> Counter:
    stopwords = get_stopwords()
    words = [
        word for word in tokenize_words(text)
        if word not in stopwords and len(word) > 2
    ]
    return Counter(words)
