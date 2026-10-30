"""Single-page health insurance workspace matching the mockup."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import LEGAL_DISCLAIMER
from app.models.types import AnalysisResult, DocumentRecord
from app.ui.widgets.cards import ActionCard, Card, RiskTile, labeled_row
from app.ui.widgets.drop_zone import DropZone


class HomePage(QWidget):
    choose_file_requested = Signal()
    file_dropped = Signal(str)
    paste_requested = Signal()
    claim_requested = Signal()
    appeal_requested = Signal()
    settings_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.overview_rows: dict[str, QLabel] = {}
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        hero = QVBoxLayout()
        hero.setSpacing(6)
        title = QLabel("ClearClause AI")
        title.setStyleSheet(
            'font-family: Palatino, "Times New Roman", serif; font-size: 42px; font-weight: 700; color: #5C2E18;'
        )
        tag = QLabel("Understand Your Health Insurance.")
        tag.setStyleSheet(
            'font-family: Palatino, "Times New Roman", serif; font-size: 22px; color: #C45C26;'
        )
        blurb = QLabel(
            "Upload your health insurance documents, get clear explanations,\n"
            "and create claims or appeals—all in one place."
        )
        blurb.setStyleSheet("color: #8A6A55;")
        hero.addWidget(title)
        hero.addWidget(tag)
        hero.addWidget(blurb)
        header.addLayout(hero, 1)
        settings = QPushButton("API key")
        settings.setObjectName("ghostButton")
        settings.setCursor(Qt.CursorShape.PointingHandCursor)
        settings.clicked.connect(self.settings_requested.emit)
        header.addWidget(settings, alignment=Qt.AlignmentFlag.AlignTop)
        root.addLayout(header)

        top = Card()
        top.body.setContentsMargins(18, 18, 18, 18)
        row = QHBoxLayout()
        row.setSpacing(16)
        self.drop_zone = DropZone()
        self.drop_zone.choose.clicked.connect(self.choose_file_requested.emit)
        self.drop_zone.file_selected.connect(self.file_dropped.emit)
        self.drop_zone.paste_requested.connect(self.paste_requested.emit)
        row.addWidget(self.drop_zone, 3)

        actions = QVBoxLayout()
        actions.setSpacing(12)
        self.claim_card = ActionCard(
            "📄",
            "Create a Claim",
            "Generate a clear, professional claim to submit to your insurer.",
        )
        self.appeal_card = ActionCard(
            "📝",
            "Create an Appeal",
            "Request a review for a denied or underpaid claim.",
        )
        self.claim_card.clicked.connect(self.claim_requested.emit)
        self.appeal_card.clicked.connect(self.appeal_requested.emit)
        actions.addWidget(self.claim_card, 1)
        actions.addWidget(self.appeal_card, 1)
        row.addLayout(actions, 2)
        top.body.addLayout(row)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8A6A55;")
        top.body.addWidget(self.status_label)
        root.addWidget(top)

        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        summary = Card()
        heading = QLabel("Document Summary")
        heading.setObjectName("sectionTitle")
        summary.body.addWidget(heading)
        mapping = [
            ("provider", "🛡️", "Insurance Provider"),
            ("member", "👤", "Member Name"),
            ("dates", "📅", "Service Date(s)"),
            ("claim", "💵", "Claim Number"),
            ("type", "📄", "Document Type"),
        ]
        for key, icon, label in mapping:
            widget = labeled_row(icon, label)
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("color: #EADBCB; background: #EADBCB; max-height: 1px;")
            self.overview_rows[key] = widget.value_label
            summary.body.addWidget(widget)
            summary.body.addWidget(line)
        summary.body.addStretch()
        bottom.addWidget(summary, 2)

        analysis = Card()
        a_title = QLabel("AI Analysis")
        a_title.setObjectName("sectionTitle")
        analysis.body.addWidget(a_title)
        self.analysis_intro = QLabel(
            "Your key information, risks, and explanations will appear here after upload."
        )
        self.analysis_intro.setStyleSheet("color: #8A6A55;")
        self.analysis_intro.setWordWrap(True)
        analysis.body.addWidget(self.analysis_intro)

        tiles = QHBoxLayout()
        tiles.setSpacing(10)
        self.high_tile = RiskTile(
            "❗", "High Risk", "Items that may need immediate attention.", "#B42318", "#F8D4D0"
        )
        self.med_tile = RiskTile(
            "⚠", "Medium Risk", "Items to review or clarify.", "#B54708", "#F8E8C8"
        )
        self.low_tile = RiskTile(
            "✓", "Low Risk", "Standard information with minimal concern.", "#067647", "#D8E8D0"
        )
        tiles.addWidget(self.high_tile)
        tiles.addWidget(self.med_tile)
        tiles.addWidget(self.low_tile)
        analysis.body.addLayout(tiles)

        explain = QFrame()
        explain.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        explain.setStyleSheet("QFrame { background: #FBF6F0; border-radius: 14px; }")
        expl_layout = QVBoxLayout(explain)
        expl_title = QLabel("🔍   Plain-Language Explanation")
        expl_title.setStyleSheet("font-weight: 700; color: #5C2E18;")
        self.plain_language = QLabel("A clear explanation of your document will appear here.")
        self.plain_language.setWordWrap(True)
        self.plain_language.setStyleSheet("color: #8A6A55;")
        expl_layout.addWidget(expl_title)
        expl_layout.addWidget(self.plain_language)
        analysis.body.addWidget(explain)
        bottom.addWidget(analysis, 3)
        root.addLayout(bottom)

        disclaimer = QLabel(LEGAL_DISCLAIMER)
        disclaimer.setObjectName("disclaimer")
        disclaimer.setWordWrap(True)
        root.addWidget(disclaimer)
        root.addStretch()

    def set_selected_file(self, path: str) -> None:
        self.drop_zone.set_file_name(Path(path).name)
        self.status_label.setText(f"Selected {Path(path).name}. Analyzing…")

    def set_pasted(self) -> None:
        self.drop_zone.set_file_name("Pasted text")
        self.status_label.setText("Pasted text ready. Analyzing…")

    def set_busy(self, busy: bool, message: str = "") -> None:
        self.status_label.setText(message)
        self.drop_zone.choose.setEnabled(not busy)
        self.drop_zone.paste.setEnabled(not busy)

    def show_analysis(self, record: DocumentRecord, result: AnalysisResult) -> None:
        ov = result.overview
        self.overview_rows["provider"].setText(ov.insurance_provider)
        self.overview_rows["member"].setText(ov.member_name)
        self.overview_rows["dates"].setText(ov.service_dates)
        self.overview_rows["claim"].setText(ov.claim_number)
        self.overview_rows["type"].setText(ov.document_type)
        high = result.risk_counts.get("high", 0)
        medium = result.risk_counts.get("medium", 0)
        low = result.risk_counts.get("low", 0)
        self.high_tile.caption.setText(
            f"{high} item(s)\nItems that may need immediate attention."
        )
        self.med_tile.caption.setText(f"{medium} item(s)\nItems to review or clarify.")
        self.low_tile.caption.setText(f"{low} item(s)\nStandard information with minimal concern.")
        if result.findings:
            preview = "  ·  ".join(f"{item.name} ({item.risk_level})" for item in result.findings[:4])
            self.analysis_intro.setText(preview)
        else:
            self.analysis_intro.setText(f"Analysis complete for {record.name}.")
        explanation = result.plain_language or "No additional explanation was generated."
        if result.processing_notes:
            explanation += "\n\nNotes: " + " ".join(result.processing_notes)
        self.plain_language.setText(explanation)
        self.plain_language.setStyleSheet("color: #4A2C1A;")
        self.status_label.setText(f"Analysis complete for {record.name}.")
