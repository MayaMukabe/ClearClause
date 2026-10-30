from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import PRIVACY_NOTICE
from app.ui.widgets.cards import Card
from app.ui.widgets.drop_zone import DropZone
from app.utils.preview import preview_text


class UploadPage(QWidget):
    choose_file_requested = Signal()
    file_dropped = Signal(str)
    analyze_requested = Signal()
    remove_file = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 36, 28)
        layout.setSpacing(16)

        title = QLabel("Upload Contract")
        title.setObjectName("heroTitle")
        title.setStyleSheet("font-size: 32px;")
        subtitle = QLabel("Add a PDF or Word document. Text is extracted locally before any AI analysis.")
        subtitle.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = Card()
        self.drop_zone = DropZone()
        self.drop_zone.choose.clicked.connect(self.choose_file_requested.emit)
        self.drop_zone.file_selected.connect(self.file_dropped.emit)
        card.body.addWidget(self.drop_zone)

        actions = QHBoxLayout()
        self.remove_btn = QPushButton("Remove file")
        self.remove_btn.setObjectName("ghostButton")
        self.remove_btn.clicked.connect(self.remove_file.emit)
        self.analyze_btn = QPushButton("Analyze Document")
        self.analyze_btn.setObjectName("primaryButton")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.analyze_requested.emit)
        actions.addWidget(self.remove_btn)
        actions.addStretch()
        actions.addWidget(self.analyze_btn)
        card.body.addLayout(actions)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        card.body.addWidget(self.progress)
        self.status = QLabel("")
        self.status.setObjectName("muted")
        card.body.addWidget(self.status)
        layout.addWidget(card)

        preview_card = Card()
        preview_card.body.addWidget(self._h("Document preview"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Extracted text will appear here after you choose a file.")
        self.preview.setMinimumHeight(280)
        preview_card.body.addWidget(self.preview)
        layout.addWidget(preview_card, 1)

        notice = QLabel(PRIVACY_NOTICE)
        notice.setWordWrap(True)
        notice.setObjectName("disclaimer")
        layout.addWidget(notice)

    def _h(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def set_file(self, path: str, extracted: str, notes: str) -> None:
        self.drop_zone.set_file_name(Path(path).name)
        body = extracted
        if notes:
            body = f"Extraction notes:\n{notes}\n\n{extracted}"
        self.preview.setPlainText(preview_text(body))
        self.analyze_btn.setEnabled(True)
        self.status.setText(f"{Path(path).name} ready.")

    def clear_file(self) -> None:
        self.drop_zone.set_file_name("")
        self.preview.clear()
        self.analyze_btn.setEnabled(False)
        self.status.setText("")

    def set_busy(self, busy: bool, message: str = "") -> None:
        self.progress.setVisible(busy)
        self.analyze_btn.setEnabled(not busy and bool(self.drop_zone.file_label.text()))
        self.status.setText(message)
