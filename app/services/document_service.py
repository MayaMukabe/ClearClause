"""Coordinate storage, extraction, analysis, and letter drafts."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from app.ai.analyzer import analyze_document
from app.ai.letters import draft_letter
from app.config import documents_dir, get_model
from app.database.db import Database
from app.document_processing.extractor import extract_document, extract_from_text
from app.models.types import AnalysisResult, DocumentRecord


class DocumentService:
    def __init__(self, db: Database | None = None) -> None:
        self.db = db or Database()

    def import_file(self, source: str | Path) -> DocumentRecord:
        source_path = Path(source)
        extracted = extract_document(source_path)
        stored = documents_dir() / f"{source_path.stem}_{_stamp()}{source_path.suffix.lower()}"
        stored.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, stored)
        return self._save_extracted(
            name=source_path.name,
            original_path=str(source_path),
            stored_path=str(stored),
            extracted=extracted,
        )

    def import_text(self, text: str, name: str = "pasted-text.txt") -> DocumentRecord:
        extracted = extract_from_text(text, name=name)
        stored = documents_dir() / f"pasted_{_stamp()}.txt"
        stored.write_text(text, encoding="utf-8")
        return self._save_extracted(
            name=name,
            original_path="",
            stored_path=str(stored),
            extracted=extracted,
        )

    def _save_extracted(self, *, name: str, original_path: str, stored_path: str, extracted) -> DocumentRecord:
        doc_id = self.db.insert_document(
            name=name,
            original_path=original_path,
            stored_path=stored_path,
            file_type=extracted.file_type,
            category="health",
            extracted_text=extracted.full_text,
            page_count=extracted.page_count,
            extraction_notes="\n".join(extracted.notes),
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
            result = analyze_document(text)
            notes = [line for line in record.extraction_notes.splitlines() if line]
            result.processing_notes = notes + result.processing_notes
            self.db.save_analysis(document_id, result, get_model())
            return result
        except Exception:
            self.db.update_status(document_id, "error")
            raise

    def draft_letter(self, document_id: int, kind: str) -> str:
        record = self.db.get_document(document_id)
        if record is None:
            raise ValueError("Upload or paste a document first.")
        text = self.db.get_extracted_text(document_id)
        return draft_letter(
            kind=kind,
            document_name=record.name,
            document_text=text,
            analysis=record.analysis,
        )

    def delete(self, document_id: int) -> None:
        stored = self.db.delete_document(document_id)
        if stored:
            path = Path(stored)
            if path.exists():
                path.unlink()


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")
