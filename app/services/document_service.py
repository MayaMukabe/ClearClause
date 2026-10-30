"""Application logic that coordinates storage, extraction, and analysis."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.ai.analyzer import analyze_contract
from app.ai.assistant import answer_question
from app.config import documents_dir
from app.database.db import Database
from app.document_processing.extractor import extract_document
from app.models.types import AnalysisResult, DocumentRecord


class DocumentService:
    def __init__(self, db: Database | None = None) -> None:
        self.db = db or Database()

    def import_file(self, source: str | Path, category: str = "legal") -> DocumentRecord:
        source_path = Path(source)
        extracted = extract_document(source_path)
        stored = documents_dir() / f"{source_path.stem}_{_safe_stamp()}{source_path.suffix.lower()}"
        stored.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, stored)
        notes = "\n".join(extracted.notes)
        doc_id = self.db.insert_document(
            name=source_path.name,
            original_path=str(source_path),
            stored_path=str(stored),
            file_type=extracted.file_type,
            category=category,
            extracted_text=extracted.full_text,
            page_count=extracted.page_count,
            extraction_notes=notes,
        )
        record = self.db.get_document(doc_id)
        if record is None:
            raise RuntimeError("Document was saved but could not be reloaded.")
        return record

    def analyze(self, document_id: int) -> AnalysisResult:
        record = self.db.get_document(document_id)
        if record is None:
            raise ValueError("Document not found.")
        text = self.db.get_extracted_text(document_id)
        if not text.strip():
            raise ValueError("No text could be extracted from this document.")
        self.db.update_status(document_id, "analyzing")
        try:
            from app.config import get_model

            result = analyze_contract(text, category=record.category)
            notes = record.extraction_notes.strip()
            if notes:
                extra = [n for n in notes.splitlines() if n]
                result.processing_notes = extra + result.processing_notes
            self.db.save_analysis(document_id, result, get_model())
            return result
        except Exception:
            self.db.update_status(document_id, "error")
            raise

    def ask(self, document_id: int, question: str) -> str:
        record = self.db.get_document(document_id)
        if record is None:
            raise ValueError("Select a document before asking a question.")
        text = self.db.get_extracted_text(document_id)
        history = self.db.get_chat_history(document_id)
        self.db.add_chat_message(document_id, "user", question)
        answer = answer_question(
            document_text=text,
            question=question,
            history=history,
            document_name=record.name,
            category=record.category,
        )
        self.db.add_chat_message(document_id, "assistant", answer)
        return answer

    def delete(self, document_id: int) -> None:
        stored = self.db.delete_document(document_id)
        if stored:
            path = Path(stored)
            if path.exists():
                path.unlink()


def _safe_stamp() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d%H%M%S")
