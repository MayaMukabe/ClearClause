from pathlib import Path

from app.database.db import Database
from app.models.types import AnalysisResult, Clause, Overview


def test_document_roundtrip(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    doc_id = db.insert_document(
        name="lease.pdf",
        original_path="/tmp/lease.pdf",
        stored_path="/tmp/stored.pdf",
        file_type="pdf",
        category="legal",
        extracted_text="Rent is $1,200 per month.",
        page_count=2,
        extraction_notes="",
    )
    rec = db.get_document(doc_id)
    assert rec is not None
    assert rec.name == "lease.pdf"
    result = AnalysisResult(
        overview=Overview(document_type="Lease"),
        clauses=[
            Clause(
                name="Rent",
                original_text="Rent is $1,200 per month.",
                location="Page 1",
                risk_level="low",
                simple_explanation="You pay monthly rent.",
                why_it_matters="This is the main payment.",
                consequences="Missing rent may lead to fees.",
            )
        ],
        risk_counts={"high": 0, "medium": 0, "low": 1},
    )
    db.save_analysis(doc_id, result, "gpt-4o-mini")
    saved = db.get_latest_analysis(doc_id)
    assert saved is not None
    assert saved.overview.document_type == "Lease"
    stats = db.stats()
    assert stats["total_documents"] == 1
    assert stats["analyzed"] == 1
    db.delete_document(doc_id)
    assert db.get_document(doc_id) is None
