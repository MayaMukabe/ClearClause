"""SQLite persistence for documents, analyses, and chat history."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import database_path
from app.models.types import AnalysisResult, DocumentRecord


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or database_path())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    original_path TEXT,
                    stored_path TEXT,
                    file_type TEXT,
                    category TEXT DEFAULT 'health',
                    uploaded_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'uploaded',
                    page_count INTEGER DEFAULT 0,
                    extracted_text TEXT,
                    extraction_notes TEXT
                );

                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    model TEXT,
                    payload TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                """
            )

    def insert_document(
        self,
        *,
        name: str,
        original_path: str,
        stored_path: str,
        file_type: str,
        category: str,
        extracted_text: str,
        page_count: int,
        extraction_notes: str,
    ) -> int:
        uploaded_at = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO documents (
                    name, original_path, stored_path, file_type, category,
                    uploaded_at, status, page_count, extracted_text, extraction_notes
                ) VALUES (?, ?, ?, ?, ?, ?, 'uploaded', ?, ?, ?)
                """,
                (
                    name,
                    original_path,
                    stored_path,
                    file_type,
                    category,
                    uploaded_at,
                    page_count,
                    extracted_text,
                    extraction_notes,
                ),
            )
            return int(cur.lastrowid)

    def list_documents(self, search: str = "", status: str = "") -> list[DocumentRecord]:
        query = "SELECT * FROM documents WHERE 1=1"
        params: list[Any] = []
        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY uploaded_at DESC"
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        records = [DocumentRecord.from_row(dict(r)) for r in rows]
        for rec in records:
            rec.analysis = self.get_latest_analysis(rec.id) if rec.id else None
        return records

    def get_document(self, document_id: int) -> DocumentRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
        if not row:
            return None
        rec = DocumentRecord.from_row(dict(row))
        rec.analysis = self.get_latest_analysis(document_id)
        return rec

    def get_extracted_text(self, document_id: int) -> str:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT extracted_text FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
        return str(row["extracted_text"] or "") if row else ""

    def update_status(self, document_id: int, status: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE documents SET status = ? WHERE id = ?", (status, document_id)
            )

    def save_analysis(
        self, document_id: int, result: AnalysisResult, model: str
    ) -> None:
        created_at = datetime.now().isoformat(timespec="seconds")
        result.created_at = created_at
        result.model = model
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO analyses (document_id, created_at, model, payload)
                VALUES (?, ?, ?, ?)
                """,
                (document_id, created_at, model, json.dumps(result.to_dict())),
            )
            conn.execute(
                "UPDATE documents SET status = ? WHERE id = ?",
                ("analyzed", document_id),
            )

    def get_latest_analysis(self, document_id: int | None) -> AnalysisResult | None:
        if not document_id:
            return None
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT payload FROM analyses
                WHERE document_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (document_id,),
            ).fetchone()
        if not row:
            return None
        return AnalysisResult.from_dict(json.loads(row["payload"]))

    def delete_document(self, document_id: int) -> str | None:
        rec = self.get_document(document_id)
        with self.connect() as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return rec.stored_path if rec else None

    def add_chat_message(self, document_id: int, role: str, content: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (document_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    document_id,
                    role,
                    content,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def get_chat_history(self, document_id: int, limit: int = 40) -> list[dict[str, str]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content FROM chat_messages
                WHERE document_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (document_id, limit),
            ).fetchall()
        messages = [{"role": r["role"], "content": r["content"]} for r in rows]
        messages.reverse()
        return messages

    def clear_chat(self, document_id: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM chat_messages WHERE document_id = ?", (document_id,)
            )

    def get_setting(self, key: str, default: str = "") -> str:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        return str(row["value"]) if row and row["value"] is not None else default

    def set_setting(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )

    def stats(self) -> dict[str, int]:
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            analyzed = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE status = 'analyzed'"
            ).fetchone()[0]
        high = medium = low = 0
        for rec in self.list_documents():
            if rec.analysis:
                high += rec.analysis.risk_counts.get("high", 0)
                medium += rec.analysis.risk_counts.get("medium", 0)
                low += rec.analysis.risk_counts.get("low", 0)
        return {
            "total_documents": int(total),
            "analyzed": int(analyzed),
            "high": high,
            "medium": medium,
            "low": low,
        }
