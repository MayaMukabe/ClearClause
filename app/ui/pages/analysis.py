from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.config import LEGAL_DISCLAIMER
from app.models.types import AnalysisResult, Clause, DocumentRecord
from app.ui.widgets.cards import Card, RiskTile


class AnalysisPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._clauses: list[Clause] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        self.body = QVBoxLayout(inner)
        self.body.setContentsMargins(32, 28, 36, 28)
        self.body.setSpacing(16)

        self.title = QLabel("Contract Analysis")
        self.title.setObjectName("heroTitle")
        self.title.setStyleSheet("font-size: 32px;")
        self.subtitle = QLabel("Upload and analyze a document to see a full report.")
        self.subtitle.setObjectName("muted")
        self.body.addWidget(self.title)
        self.body.addWidget(self.subtitle)

        risk_row = QHBoxLayout()
        self.high_tile = RiskTile("High Risk", "#B42318", "#F8D4D0")
        self.med_tile = RiskTile("Medium Risk", "#B54708", "#F8E8C8")
        self.low_tile = RiskTile("Low Risk", "#067647", "#D8E8D0")
        risk_row.addWidget(self.high_tile)
        risk_row.addWidget(self.med_tile)
        risk_row.addWidget(self.low_tile)
        self.body.addLayout(risk_row)

        summary_card = Card()
        summary_card.body.addWidget(self._h("Contract Summary"))
        self.summary_label = QLabel("No analysis yet.")
        self.summary_label.setWordWrap(True)
        summary_card.body.addWidget(self.summary_label)
        self.body.addWidget(summary_card)

        before = Card()
        before.body.addWidget(self._h("BEFORE YOU SIGN"))
        note = QLabel(
            "These are the issues most worth reviewing. This is not a recommendation to sign or refuse."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        before.body.addWidget(note)
        self.before_label = QLabel("—")
        self.before_label.setWordWrap(True)
        before.body.addWidget(self.before_label)
        self.body.addWidget(before)

        translator = Card()
        translator.body.addWidget(self._h("Legal Language Translator"))
        self.clause_filter = QComboBox()
        self.clause_filter.addItems(["All risk levels", "high", "medium", "low"])
        self.clause_filter.currentTextChanged.connect(self._render_clauses)
        translator.body.addWidget(self.clause_filter)
        self.clauses_host = QVBoxLayout()
        translator.body.addLayout(self.clauses_host)
        self.body.addWidget(translator)

        disclaimer = QLabel(LEGAL_DISCLAIMER)
        disclaimer.setObjectName("disclaimer")
        disclaimer.setWordWrap(True)
        self.body.addWidget(disclaimer)
        self.body.addStretch()

        scroll.setWidget(inner)
        layout.addWidget(scroll)

    def _h(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def show_record(self, record: DocumentRecord) -> None:
        self.title.setText(record.name)
        self.subtitle.setText(
            f"{record.file_type.upper()}  ·  {record.category.title()}  ·  uploaded {record.uploaded_at}"
        )
        result = record.analysis
        if not result:
            self.summary_label.setText("This document has not been analyzed yet.")
            self.before_label.setText("—")
            self._clauses = []
            self._render_clauses()
            return
        self.show_result(result)

    def show_result(self, result: AnalysisResult) -> None:
        self.high_tile.set_count(result.risk_counts.get("high", 0))
        self.med_tile.set_count(result.risk_counts.get("medium", 0))
        self.low_tile.set_count(result.risk_counts.get("low", 0))
        s = result.summary
        blocks = [
            ("Contract type", s.get("contract_type")),
            ("Parties", s.get("parties")),
            ("Important dates", s.get("important_dates")),
            ("Payment obligations", s.get("payment_obligations")),
            ("Financial responsibilities", s.get("financial_responsibilities")),
            ("Cancellation policies", s.get("cancellation_policies")),
            ("Renewal conditions", s.get("renewal_conditions")),
            ("Rights and responsibilities", s.get("rights_and_responsibilities")),
            ("Important restrictions", s.get("important_restrictions")),
            ("Potential risks", s.get("potential_risks")),
            ("Clauses requiring attention", s.get("clauses_requiring_attention")),
        ]
        self.summary_label.setText(
            "\n\n".join(f"{title}\n{value or 'Not specified in the document.'}" for title, value in blocks)
        )
        bys = result.before_you_sign
        highlights = bys.get("highlights") or []
        questions = bys.get("suggested_questions") or []
        parts = []
        if highlights:
            parts.append("Key issues to review:\n" + "\n".join(f"• {h}" for h in highlights))
        if questions:
            parts.append(
                "Questions to consider asking the other party or a qualified attorney:\n"
                + "\n".join(f"• {q}" for q in questions)
            )
        notes = result.processing_notes
        if notes:
            parts.append("Processing notes:\n" + "\n".join(f"• {n}" for n in notes))
        self.before_label.setText("\n\n".join(parts) or "No additional highlights were generated.")
        self._clauses = result.clauses
        self._render_clauses()

    def _render_clauses(self) -> None:
        while self.clauses_host.count():
            item = self.clauses_host.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        wanted = self.clause_filter.currentText()
        clauses = self._clauses
        if wanted in {"high", "medium", "low"}:
            clauses = [c for c in clauses if c.risk_level == wanted]
        if not clauses:
            empty = QLabel("No clauses to display for this filter.")
            empty.setObjectName("muted")
            self.clauses_host.addWidget(empty)
            return
        for clause in clauses:
            self.clauses_host.addWidget(self._clause_card(clause))

    def _clause_card(self, clause: Clause) -> Card:
        card = Card()
        header = QLabel(f"{clause.name}  ·  {clause.risk_level.upper()}  ·  {clause.location}")
        header.setObjectName("sectionTitle")
        header.setStyleSheet("font-size: 16px;")
        card.body.addWidget(header)
        if not clause.stated_in_contract:
            flag = QLabel("This item is an interpretation, not a direct quote from the contract.")
            flag.setStyleSheet("color: #B54708;")
            card.body.addWidget(flag)
        for title, text in [
            ("Original Clause", clause.original_text or "Original wording was not available."),
            ("Simple Explanation", clause.simple_explanation),
            ("Why It Matters", clause.why_it_matters),
            ("What to Watch For", clause.what_to_watch_for or clause.consequences),
        ]:
            heading = QLabel(title)
            heading.setStyleSheet("font-weight: 700; color: #5C2E18;")
            body = QLabel(text or "—")
            body.setWordWrap(True)
            card.body.addWidget(heading)
            card.body.addWidget(body)
        if clause.questions:
            q = QLabel("Questions to consider:\n" + "\n".join(f"• {item}" for item in clause.questions))
            q.setWordWrap(True)
            card.body.addWidget(q)
        if clause.interpretation_note:
            note = QLabel("Interpretation note: " + clause.interpretation_note)
            note.setObjectName("muted")
            note.setWordWrap(True)
            card.body.addWidget(note)
        return card
