from pathlib import Path
from summarizer.text_extractor import extract_txt_text


def test_txt_extraction(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("This is a test document.", encoding="utf-8")
    assert extract_txt_text(str(file_path)) == "This is a test document."
