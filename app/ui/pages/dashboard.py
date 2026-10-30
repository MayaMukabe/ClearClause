"""Home screen that follows the ClearClause mockup."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.config import LEGAL_DISCLAIMER
from app.models.types import AnalysisResult, DocumentRecord
from app.ui.widgets.cards import Card, RiskTile, labeled_row
from app.ui.widgets.drop_zone import DropZone


class CategoryCard(QFrame):
    selected = Signal(str)

    def __init__(self, key: str, icon: str, title: str, subtitle: str) -> None:
        super().__init__()
        self.key = key
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(16, 18, 16, 18)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 26px;")
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: 700; color: #5C2E18;")
        sub = QLabel(subtitle)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setObjectName("muted")
        sub.setStyleSheet("color: #8A6A55; font-size: 11px;")
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(sub)
        self.set_active(False)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.selected.emit(self.key)
        super().mousePressEvent(event)

    def set_active(self, active: bool) -> None:
        if active:
            self.setStyleSheet(
                "QFrame { background: #F8EDE4; border: 2px solid #C45C26; border-radius: 16px; }"
            )
        else:
            self.setStyleSheet(
                "QFrame { background: #FBF6F0; border: 1px solid #EADBCB; border-radius: 16px; }"
            )


class DashboardPage(QWidget):
    choose_file_requested = Signal()
    file_dropped = Signal(str)
    analyze_requested = Signal()
    question_submitted = Signal(str)
    open_recent = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.category = "legal"
        self.overview_rows: dict[str, QLabel] = {}
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 36, 24)
        root.setSpacing(18)

        hero = QVBoxLayout()
        hero.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title = QLabel("ClearClause AI")
        title.setObjectName("heroTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag = QLabel("Understand Before You Sign.")
        tag.setObjectName("heroTagline")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blurb = QLabel(
            "Upload your documents and let AI identify key information, highlight potential risks,\n"
            "and explain everything in simple terms."
        )
        blurb.setObjectName("muted")
        blurb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero.addWidget(title)
        hero.addWidget(tag)
        hero.addWidget(blurb)
        root.addLayout(hero)

        stats = QHBoxLayout()
        self.stat_docs = self._stat_chip("Documents", "0")
        self.stat_analyzed = self._stat_chip("Analyzed", "0")
        self.stat_high = self._stat_chip("High-risk clauses", "0")
        stats.addStretch()
        stats.addWidget(self.stat_docs)
        stats.addWidget(self.stat_analyzed)
        stats.addWidget(self.stat_high)
        stats.addStretch()
        root.addLayout(stats)

        upload_card = Card()
        row = QHBoxLayout()
        row.setSpacing(20)

        self.drop_zone = DropZone()
        self.drop_zone.choose.clicked.connect(self.choose_file_requested.emit)
        self.drop_zone.file_selected.connect(self.file_dropped.emit)
        row.addWidget(self.drop_zone, 1)

        category_wrap = QVBoxLayout()
        cat_title = QLabel("Select Document Category")
        cat_title.setStyleSheet("font-weight: 700; color: #5C2E18; font-size: 15px;")
        category_wrap.addWidget(cat_title)

        cats = QHBoxLayout()
        self.legal_card = CategoryCard(
            "legal",
            "⚖️",
            "Legal Document",
            "Contracts, agreements, leases, employment, loan documents, etc.",
        )
        self.health_card = CategoryCard(
            "health",
            "🩺",
            "Health Document",
            "Insurance documents, medical records, bills, explanations of benefits, etc.",
        )
        self.legal_card.selected.connect(self._set_category)
        self.health_card.selected.connect(self._set_category)
        self.legal_card.set_active(True)
        cats.addWidget(self.legal_card)
        cats.addWidget(self.health_card)
        category_wrap.addLayout(cats)

        self.analyze_btn = QPushButton("✦  Analyze Document")
        self.analyze_btn.setObjectName("accentButton")
        self.analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.analyze_requested.emit)
        self.analyze_btn.setEnabled(False)
        category_wrap.addSpacing(8)
        category_wrap.addWidget(self.analyze_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.status_label = QLabel("")
        self.status_label.setObjectName("muted")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        category_wrap.addWidget(self.status_label)
        row.addLayout(category_wrap, 1)
        upload_card.body.addLayout(row)
        root.addWidget(upload_card)

        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        overview = Card()
        overview.body.addWidget(self._section("Document Overview"))
        mapping = [
            ("type", "📄", "Document Type"),
            ("parties", "👥", "Parties Involved"),
            ("effective", "📅", "Effective Date"),
            ("expiration", "🗓️", "Expiration Date"),
            ("financial", "💵", "Key Financial Terms"),
        ]
        for key, icon, label in mapping:
            widget = labeled_row(icon, label)
            self.overview_rows[key] = widget.value_label
            overview.body.addWidget(widget)
        overview.body.addStretch()
        bottom.addWidget(overview, 1)

        middle = QVBoxLayout()
        risk_card = Card()
        risk_card.body.addWidget(self._section("Risk Summary"))
        tiles = QHBoxLayout()
        self.high_tile = RiskTile("High Risk", "#B42318", "#F8D4D0")
        self.med_tile = RiskTile("Medium Risk", "#B54708", "#F8E8C8")
        self.low_tile = RiskTile("Low Risk", "#067647", "#D8E8D0")
        tiles.addWidget(self.high_tile)
        tiles.addWidget(self.med_tile)
        tiles.addWidget(self.low_tile)
        risk_card.body.addLayout(tiles)
        middle.addWidget(risk_card)

        findings = Card()
        findings.body.addWidget(self._section("Key Findings"))
        self.findings_label = QLabel(
            "📄  Your key clauses and potential risks will appear here after analysis."
        )
        self.findings_label.setWordWrap(True)
        self.findings_label.setObjectName("muted")
        findings.body.addWidget(self.findings_label)
        middle.addWidget(findings)
        bottom.addLayout(middle, 1)

        ask = Card()
        ask.body.addWidget(self._section("Ask Your Document"))
        sub = QLabel("Get clear answers about your specific document.")
        sub.setObjectName("muted")
        ask.body.addWidget(sub)
        ask_row = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question about your document...")
        send = QPushButton("➤")
        send.setObjectName("primaryButton")
        send.setFixedSize(48, 42)
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.clicked.connect(self._submit_question)
        self.question_input.returnPressed.connect(self._submit_question)
        ask_row.addWidget(self.question_input)
        ask_row.addWidget(send)
        ask.body.addLayout(ask_row)
        try_label = QLabel("Try asking:")
        try_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try_label.setObjectName("muted")
        ask.body.addWidget(try_label)
        for text in [
            "What are the biggest risks in this document?",
            "What does this clause mean?",
            "Are there any hidden fees?",
        ]:
            chip = QPushButton(text)
            chip.setObjectName("chipButton")
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.clicked.connect(lambda _, t=text: self._ask_chip(t))
            ask.body.addWidget(chip)
        self.answer_preview = QLabel("")
        self.answer_preview.setWordWrap(True)
        ask.body.addWidget(self.answer_preview)
        bottom.addWidget(ask, 1)
        root.addLayout(bottom)

        recent_title = self._section("Recent Activity")
        root.addWidget(recent_title)
        self.recent_wrap = QHBoxLayout()
        root.addLayout(self.recent_wrap)

        disclaimer = QLabel(LEGAL_DISCLAIMER)
        disclaimer.setObjectName("disclaimer")
        disclaimer.setWordWrap(True)
        root.addWidget(disclaimer)
        root.addStretch()

    def _section(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def _stat_chip(self, caption: str, value: str) -> QFrame:
        chip = QFrame()
        chip.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        chip.setStyleSheet(
            "QFrame { background: rgba(255,252,250,0.85); border-radius: 14px; padding: 6px 14px; }"
        )
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(12, 6, 12, 6)
        val = QLabel(value)
        val.setStyleSheet("font-weight: 700; color: #C45C26; font-size: 16px;")
        cap = QLabel(caption)
        cap.setObjectName("muted")
        layout.addWidget(val)
        layout.addWidget(cap)
        chip.value_label = val  # type: ignore[attr-defined]
        return chip

    def _set_category(self, key: str) -> None:
        self.category = key
        self.legal_card.set_active(key == "legal")
        self.health_card.set_active(key == "health")

    def set_selected_file(self, path: str) -> None:
        name = Path(path).name
        self.drop_zone.set_file_name(name)
        self.analyze_btn.setEnabled(True)
        self.status_label.setText(f"Ready to analyze {name}")

    def set_busy(self, busy: bool, message: str = "") -> None:
        self.analyze_btn.setEnabled(not busy and bool(self.drop_zone.file_label.text()))
        self.status_label.setText(message)

    def show_analysis(self, record: DocumentRecord, result: AnalysisResult) -> None:
        ov = result.overview
        self.overview_rows["type"].setText(ov.document_type)
        self.overview_rows["parties"].setText(ov.parties)
        self.overview_rows["effective"].setText(ov.effective_date)
        self.overview_rows["expiration"].setText(ov.expiration_date)
        self.overview_rows["financial"].setText(ov.key_financial_terms)
        self.high_tile.set_count(result.risk_counts.get("high", 0))
        self.med_tile.set_count(result.risk_counts.get("medium", 0))
        self.low_tile.set_count(result.risk_counts.get("low", 0))
        if result.clauses:
            top = result.clauses[:3]
            lines = [f"• {c.name} ({c.risk_level.title()}): {c.simple_explanation}" for c in top]
            self.findings_label.setText("\n".join(lines))
        else:
            self.findings_label.setText("Analysis completed. Open Contract Analysis for the full report.")
        self.status_label.setText(f"Analysis complete for {record.name}")
        self.analyze_btn.setEnabled(True)

    def set_stats(self, stats: dict) -> None:
        self.stat_docs.value_label.setText(str(stats.get("total_documents", 0)))
        self.stat_analyzed.value_label.setText(str(stats.get("analyzed", 0)))
        self.stat_high.value_label.setText(str(stats.get("high", 0)))

    def set_recent(self, records: list[DocumentRecord]) -> None:
        while self.recent_wrap.count():
            item = self.recent_wrap.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not records:
            empty = QLabel("No documents analyzed yet.")
            empty.setObjectName("muted")
            self.recent_wrap.addWidget(empty)
            return
        for rec in records[:4]:
            btn = QPushButton(f"{rec.name}\n{rec.uploaded_at}  ·  {rec.status}")
            btn.setObjectName("ghostButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if rec.id is not None:
                btn.clicked.connect(lambda _, i=rec.id: self.open_recent.emit(i))
            self.recent_wrap.addWidget(btn)

    def show_answer(self, answer: str) -> None:
        self.answer_preview.setText(answer)

    def _submit_question(self) -> None:
        text = self.question_input.text().strip()
        if text:
            self.question_submitted.emit(text)
            self.question_input.clear()

    def _ask_chip(self, text: str) -> None:
        self.question_input.setText(text)
        self.question_submitted.emit(text)

    def current_category(self) -> str:
        return self.category
