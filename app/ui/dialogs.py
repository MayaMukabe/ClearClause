from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.config import LEGAL_DISCLAIMER, SUPPORTED_MODELS, get_api_key, get_model


class PasteTextDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paste health document text")
        self.resize(640, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Paste an EOB, denial letter, bill, or coverage notice."))
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Paste the document text here…")
        layout.addWidget(self.editor)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def text(self) -> str:
        return self.editor.toPlainText().strip()


class SettingsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(520, 280)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("OpenAI API key (stored locally in .env, never logged)"))
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText(get_api_key())
        self.key_input.setPlaceholderText("sk-...")
        layout.addWidget(self.key_input)
        layout.addWidget(QLabel("Model"))
        self.model = QComboBox()
        self.model.addItems(SUPPORTED_MODELS)
        current = get_model()
        if current not in SUPPORTED_MODELS:
            self.model.addItem(current)
        self.model.setCurrentText(current)
        layout.addWidget(self.model)
        note = QLabel(LEGAL_DISCLAIMER)
        note.setWordWrap(True)
        note.setObjectName("disclaimer")
        layout.addWidget(note)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str]:
        return self.key_input.text().strip(), self.model.currentText()


class LetterDialog(QDialog):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 560)
        layout = QVBoxLayout(self)
        self.status = QLabel("Drafting from your document…")
        layout.addWidget(self.status)
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        row = QHBoxLayout()
        copy_btn = QPushButton("Copy letter")
        copy_btn.setObjectName("primaryButton")
        copy_btn.clicked.connect(self._copy)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghostButton")
        close_btn.clicked.connect(self.accept)
        row.addWidget(copy_btn)
        row.addStretch()
        row.addWidget(close_btn)
        layout.addLayout(row)

    def set_letter(self, text: str) -> None:
        self.status.setText("Review this draft against the original document before sending.")
        self.editor.setReadOnly(False)
        self.editor.setPlainText(text)

    def set_error(self, message: str) -> None:
        self.status.setText(message)

    def _copy(self) -> None:
        self.editor.selectAll()
        self.editor.copy()
        cursor = self.editor.textCursor()
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)
        self.status.setText("Copied to the clipboard.")
