from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.types import DocumentRecord
from app.ui.widgets.cards import Card


class AssistantPage(QWidget):
    send_question = Signal(str)
    document_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 36, 28)

        title = QLabel("AI Assistant")
        title.setObjectName("heroTitle")
        title.setStyleSheet("font-size: 32px;")
        layout.addWidget(title)

        picker_row = QHBoxLayout()
        picker_row.addWidget(QLabel("Current document"))
        self.picker = QComboBox()
        self.picker.currentIndexChanged.connect(self._emit_doc)
        picker_row.addWidget(self.picker, 1)
        layout.addLayout(picker_row)

        card = Card()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_host = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_host)
        self.chat_layout.addStretch()
        self.scroll.setWidget(self.chat_host)
        self.scroll.setMinimumHeight(360)
        card.body.addWidget(self.scroll)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask about this contract…")
        self.input.returnPressed.connect(self._send)
        send = QPushButton("Send")
        send.setObjectName("primaryButton")
        send.clicked.connect(self._send)
        row.addWidget(self.input)
        row.addWidget(send)
        card.body.addLayout(row)
        layout.addWidget(card, 1)

        self.status = QLabel("Answers stay grounded in the selected document.")
        self.status.setObjectName("muted")
        layout.addWidget(self.status)
        self._docs: list[DocumentRecord] = []

    def set_documents(self, records: list[DocumentRecord], selected_id: int | None) -> None:
        self._docs = records
        self.picker.blockSignals(True)
        self.picker.clear()
        for rec in records:
            self.picker.addItem(rec.name, rec.id)
        if selected_id is not None:
            index = self.picker.findData(selected_id)
            if index >= 0:
                self.picker.setCurrentIndex(index)
        self.picker.blockSignals(False)

    def set_history(self, messages: list[dict[str, str]]) -> None:
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for msg in messages:
            self.add_message(msg.get("role", "assistant"), msg.get("content", ""))

    def add_message(self, role: str, content: str) -> None:
        bubble = QLabel(content)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if role == "user":
            bubble.setStyleSheet(
                "QLabel { background: #C45C26; color: #FFF8F2; border-radius: 14px; padding: 10px 14px; }"
            )
            bubble.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            bubble.setStyleSheet(
                "QLabel { background: #F6EDE3; color: #4A2C1A; border-radius: 14px; padding: 10px 14px; }"
            )
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def set_busy(self, busy: bool) -> None:
        self.status.setText("Thinking…" if busy else "Answers stay grounded in the selected document.")
        self.input.setEnabled(not busy)

    def _send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.add_message("user", text)
        self.send_question.emit(text)

    def _emit_doc(self) -> None:
        value = self.picker.currentData()
        if value is not None:
            self.document_changed.emit(int(value))

    def current_document_id(self) -> int | None:
        value = self.picker.currentData()
        return int(value) if value is not None else None
