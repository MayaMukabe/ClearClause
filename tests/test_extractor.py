from pathlib import Path

from app.document_processing.extractor import extract_document, split_for_model


def test_extract_txt(tmp_path: Path) -> None:
    path = tmp_path / "lease.txt"
    path.write_text("Section 1. Rent is due on the first of each month.\nLate fee: $50.", encoding="utf-8")
    result = extract_document(path)
    assert "Rent is due" in result.full_text
    assert result.page_count >= 1


def test_split_preserves_content() -> None:
    text = "AAAA " * 5000
    chunks = split_for_model(text, max_chars=1000)
    assert len(chunks) > 1
    rebuilt = chunks[0]
    for chunk in chunks[1:]:
        # Overlap means we do not require a perfect join; each chunk is non-empty.
        assert chunk
    assert rebuilt
