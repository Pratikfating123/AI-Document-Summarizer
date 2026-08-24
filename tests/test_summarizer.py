from summarizer.nlp_processor import split_sentences, get_word_frequencies
from summarizer.summarizer import summarize_text
from summarizer.statistics import calculate_statistics


TEXT = """
Artificial intelligence is transforming many industries. Machine learning helps organizations identify
patterns in large datasets. Natural language processing allows computers to understand and analyze text.
Document summarization can reduce the time required to review long reports. Extractive summarization selects
important sentences from an original document. Flask can provide a web interface for uploading documents and
displaying generated summaries. Local processing can improve privacy because documents do not need to be sent
to an external service.
"""


def test_sentence_split():
    sentences = split_sentences(TEXT)
    assert len(sentences) >= 6


def test_word_frequencies():
    frequencies = get_word_frequencies(TEXT)
    assert frequencies["document"] >= 1
    assert frequencies["summarization"] >= 1


def test_summary_is_shorter():
    summary = summarize_text(TEXT, "short")
    assert summary
    assert len(summary.split()) < len(TEXT.split())


def test_statistics():
    summary = summarize_text(TEXT, "medium")
    stats = calculate_statistics(TEXT, summary)
    assert stats["original_words"] > 0
    assert stats["summary_words"] > 0
    assert "compression_percentage" in stats
