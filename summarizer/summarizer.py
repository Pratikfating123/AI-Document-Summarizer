import math
import re
from collections import defaultdict

from .nlp_processor import (
    get_word_frequencies,
    split_sentences,
    tokenize_words,
)


def _target_sentence_count(total: int, length: str) -> int:
    ratios = {"short": 0.15, "medium": 0.30, "long": 0.50}
    ratio = ratios.get(length, ratios["medium"])

    if total <= 3:
        return max(1, total)

    target = max(1, round(total * ratio))

    if length == "short":
        target = min(target, 8)
    elif length == "medium":
        target = min(target, 15)
    else:
        target = min(target, 25)

    return min(target, total)


def summarize_text(text: str, length: str = "medium") -> str:
    sentences = split_sentences(text)

    if not sentences:
        return ""

    if len(sentences) <= 3:
        return " ".join(sentences)

    frequencies = get_word_frequencies(text)
    if not frequencies:
        target = _target_sentence_count(len(sentences), length)
        return " ".join(sentences[:target])

    max_frequency = max(frequencies.values())
    normalized = {
        word: count / max_frequency
        for word, count in frequencies.items()
    }

    sentence_scores = []
    total_sentences = len(sentences)

    for index, sentence in enumerate(sentences):
        words = tokenize_words(sentence)
        if not words:
            continue

        content_words = [w for w in words if w in normalized]
        if not content_words:
            continue

        frequency_score = sum(normalized[w] for w in content_words) / len(content_words)

        # Slightly reward sentences near the beginning, where introductions
        # and thesis statements often occur.
        position_score = 1.0 - (index / total_sentences) * 0.20

        # Reward moderate sentence lengths and avoid one-line fragments.
        length_score = 1.0
        if len(words) < 5:
            length_score = 0.55
        elif len(words) > 70:
            length_score = 0.75

        # Reward sentences containing numbers, which often carry useful facts.
        number_bonus = 1.0
        if re.search(r"\b\d+(?:\.\d+)?%?\b", sentence):
            number_bonus = 1.08

        score = frequency_score * position_score * length_score * number_bonus
        sentence_scores.append((index, sentence, score))

    if not sentence_scores:
        target = _target_sentence_count(len(sentences), length)
        return " ".join(sentences[:target])

    target = _target_sentence_count(len(sentences), length)

    # Select top sentences while avoiding near-duplicate sentences.
    ranked = sorted(sentence_scores, key=lambda item: item[2], reverse=True)
    selected = []
    selected_word_sets = []

    for index, sentence, score in ranked:
        current_words = set(tokenize_words(sentence))
        too_similar = False

        for existing in selected_word_sets:
            union = current_words | existing
            if union:
                similarity = len(current_words & existing) / len(union)
                if similarity >= 0.65:
                    too_similar = True
                    break

        if too_similar:
            continue

        selected.append((index, sentence))
        selected_word_sets.append(current_words)

        if len(selected) >= target:
            break

    if not selected:
        selected = [(i, s) for i, s, _ in ranked[:target]]

    selected.sort(key=lambda item: item[0])
    return " ".join(sentence for _, sentence in selected).strip()
