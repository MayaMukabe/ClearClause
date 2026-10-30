"""Shared data models for health-document analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


def _dash(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "—"


@dataclass
class Overview:
    insurance_provider: str = "—"
    member_name: str = "—"
    service_dates: str = "—"
    claim_number: str = "—"
    document_type: str = "—"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Overview":
        data = data or {}
        return cls(
            insurance_provider=_dash(data.get("insurance_provider")),
            member_name=_dash(data.get("member_name") or data.get("parties")),
            service_dates=_dash(
                data.get("service_dates")
                or data.get("effective_date")
                or data.get("service_date")
            ),
            claim_number=_dash(data.get("claim_number") or data.get("key_financial_terms")),
            document_type=_dash(data.get("document_type")),
        )


@dataclass
class Finding:
    name: str
    original_text: str
    location: str
    risk_level: str
    simple_explanation: str
    why_it_matters: str = ""
    stated_in_document: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        risk = str(data.get("risk_level") or "medium").lower()
        if risk not in {"high", "medium", "low"}:
            risk = "medium"
        return cls(
            name=str(data.get("name") or "Item"),
            original_text=str(data.get("original_text") or ""),
            location=str(data.get("location") or "Unknown"),
            risk_level=risk,
            simple_explanation=str(data.get("simple_explanation") or ""),
            why_it_matters=str(data.get("why_it_matters") or ""),
            stated_in_document=bool(data.get("stated_in_document", data.get("stated_in_contract", True))),
        )


@dataclass
class AnalysisResult:
    overview: Overview = field(default_factory=Overview)
    plain_language: str = ""
    findings: list[Finding] = field(default_factory=list)
    risk_counts: dict[str, int] = field(default_factory=dict)
    processing_notes: list[str] = field(default_factory=list)
    model: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "overview": asdict(self.overview),
            "plain_language": self.plain_language,
            "findings": [asdict(item) for item in self.findings],
            "risk_counts": self.risk_counts,
            "processing_notes": self.processing_notes,
            "model": self.model,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AnalysisResult":
        data = data or {}
        raw_findings = data.get("findings") or data.get("clauses") or []
        findings = [Finding.from_dict(item) for item in raw_findings]
        counts = data.get("risk_counts") or {}
        if not counts and findings:
            counts = {
                "high": sum(1 for item in findings if item.risk_level == "high"),
                "medium": sum(1 for item in findings if item.risk_level == "medium"),
                "low": sum(1 for item in findings if item.risk_level == "low"),
            }
        return cls(
            overview=Overview.from_dict(data.get("overview")),
            plain_language=str(
                data.get("plain_language")
                or data.get("plain_language_explanation")
                or (data.get("summary") or {}).get("potential_risks")
                or ""
            ),
            findings=findings,
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
            category=row.get("category") or "health",
            uploaded_at=row.get("uploaded_at") or datetime.now().isoformat(timespec="seconds"),
            status=row.get("status") or "uploaded",
            page_count=int(row.get("page_count") or 0),
            extraction_notes=row.get("extraction_notes") or "",
        )
