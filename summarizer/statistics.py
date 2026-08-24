import math
from .nlp_processor import split_sentences, tokenize_words


def calculate_statistics(original_text: str, summary: str) -> dict:
    original_words = len(tokenize_words(original_text))
    summary_words = len(tokenize_words(summary))
    original_sentences = len(split_sentences(original_text))
    summary_sentences = len(split_sentences(summary))

    if original_words:
        compression_percentage = round(
            max(0, (1 - summary_words / original_words) * 100), 1
        )
    else:
        compression_percentage = 0.0

    reading_time = max(1, math.ceil(summary_words / 200)) if summary_words else 0

    return {
        "original_words": original_words,
        "summary_words": summary_words,
        "original_characters": len(original_text),
        "summary_characters": len(summary),
        "original_sentences": original_sentences,
        "summary_sentences": summary_sentences,
        "compression_percentage": compression_percentage,
        "reading_time": reading_time,
    }
