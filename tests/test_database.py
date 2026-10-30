from pathlib import Path

from app.database.db import Database
from app.models.types import AnalysisResult, Finding, Overview


def test_document_roundtrip(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    doc_id = db.insert_document(
        name="eob.pdf",
        original_path="/tmp/eob.pdf",
        stored_path="/tmp/stored.pdf",
        file_type="pdf",
        category="health",
        extracted_text="Claim 8821 was processed. Patient responsibility $240.",
        page_count=2,
        extraction_notes="",
    )
    rec = db.get_document(doc_id)
    assert rec is not None
    assert rec.name == "eob.pdf"
    result = AnalysisResult(
        overview=Overview(document_type="Explanation of Benefits", claim_number="8821"),
        findings=[
            Finding(
                name="Patient responsibility",
                original_text="Patient responsibility $240.",
                location="Page 1",
                risk_level="medium",
                simple_explanation="You may owe $240.",
            )
        ],
        risk_counts={"high": 0, "medium": 1, "low": 0},
        plain_language="This EOB says a claim was processed and you may owe $240.",
    )
    db.save_analysis(doc_id, result, "gpt-4o-mini")
    saved = db.get_latest_analysis(doc_id)
    assert saved is not None
    assert saved.overview.document_type == "Explanation of Benefits"
    assert saved.overview.claim_number == "8821"
    stats = db.stats()
    assert stats["total_documents"] == 1
    assert stats["analyzed"] == 1
    db.delete_document(doc_id)
    assert db.get_document(doc_id) is None
