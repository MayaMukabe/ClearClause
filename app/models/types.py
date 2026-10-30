"""Shared data models used across UI, AI, and database layers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Overview:
    document_type: str = "—"
    parties: str = "—"
    effective_date: str = "—"
    expiration_date: str = "—"
    key_financial_terms: str = "—"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Overview":
        data = data or {}
        parties = data.get("parties", "—")
        if isinstance(parties, list):
            parties = ", ".join(str(p) for p in parties) or "—"
        return cls(
            document_type=str(data.get("document_type") or "—"),
            parties=str(parties or "—"),
            effective_date=str(data.get("effective_date") or "—"),
            expiration_date=str(data.get("expiration_date") or "—"),
            key_financial_terms=str(data.get("key_financial_terms") or "—"),
        )


@dataclass
class Clause:
    name: str
    original_text: str
    location: str
    risk_level: str
    simple_explanation: str
    why_it_matters: str
    consequences: str
    questions: list[str] = field(default_factory=list)
    category: str = "terms"
    stated_in_contract: bool = True
    interpretation_note: str = ""
    what_to_watch_for: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Clause":
        questions = data.get("questions") or []
        if isinstance(questions, str):
            questions = [questions]
        risk = str(data.get("risk_level") or "medium").lower()
        if risk not in {"high", "medium", "low"}:
            risk = "medium"
        return cls(
            name=str(data.get("name") or "Unnamed clause"),
            original_text=str(data.get("original_text") or ""),
            location=str(data.get("location") or data.get("page") or "Unknown"),
            risk_level=risk,
            simple_explanation=str(data.get("simple_explanation") or ""),
            why_it_matters=str(data.get("why_it_matters") or ""),
            consequences=str(data.get("consequences") or ""),
            questions=[str(q) for q in questions],
            category=str(data.get("category") or "terms"),
            stated_in_contract=bool(data.get("stated_in_contract", True)),
            interpretation_note=str(data.get("interpretation_note") or ""),
            what_to_watch_for=str(
                data.get("what_to_watch_for") or data.get("consequences") or ""
            ),
        )


@dataclass
class AnalysisResult:
    overview: Overview = field(default_factory=Overview)
    summary: dict[str, Any] = field(default_factory=dict)
    before_you_sign: dict[str, Any] = field(default_factory=dict)
    clauses: list[Clause] = field(default_factory=list)
    risk_counts: dict[str, int] = field(default_factory=dict)
    processing_notes: list[str] = field(default_factory=list)
    model: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "overview": asdict(self.overview),
            "summary": self.summary,
            "before_you_sign": self.before_you_sign,
            "clauses": [asdict(c) for c in self.clauses],
            "risk_counts": self.risk_counts,
            "processing_notes": self.processing_notes,
            "model": self.model,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AnalysisResult":
        data = data or {}
        clauses = [Clause.from_dict(c) for c in data.get("clauses") or []]
        counts = data.get("risk_counts") or {}
        if not counts and clauses:
            counts = {
                "high": sum(1 for c in clauses if c.risk_level == "high"),
                "medium": sum(1 for c in clauses if c.risk_level == "medium"),
                "low": sum(1 for c in clauses if c.risk_level == "low"),
            }
        return cls(
            overview=Overview.from_dict(data.get("overview")),
            summary=data.get("summary") or {},
            before_you_sign=data.get("before_you_sign") or {},
            clauses=clauses,
            risk_counts={
                "high": int(counts.get("high") or 0),
                "medium": int(counts.get("medium") or 0),
                "low": int(counts.get("low") or 0),
            },
            processing_notes=list(data.get("processing_notes") or []),
            model=str(data.get("model") or ""),
            created_at=str(data.get("created_at") or ""),
        )


@dataclass
class DocumentRecord:
    id: int | None
    name: str
    original_path: str
    stored_path: str
    file_type: str
    category: str
    uploaded_at: str
    status: str
    page_count: int
    extraction_notes: str = ""
    analysis: AnalysisResult | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "DocumentRecord":
        return cls(
            id=row.get("id"),
            name=row.get("name") or "",
            original_path=row.get("original_path") or "",
            stored_path=row.get("stored_path") or "",
            file_type=row.get("file_type") or "",
            category=row.get("category") or "legal",
            uploaded_at=row.get("uploaded_at") or datetime.now().isoformat(timespec="seconds"),
            status=row.get("status") or "uploaded",
            page_count=int(row.get("page_count") or 0),
            extraction_notes=row.get("extraction_notes") or "",
        )
