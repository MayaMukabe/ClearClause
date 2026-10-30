from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.config import LEGAL_DISCLAIMER, PRIVACY_NOTICE, SUPPORTED_MODELS, get_api_key, get_model
from app.ui.widgets.cards import Card


class SettingsPage(QWidget):
    save_api = Signal(str, str)
    privacy_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 36, 28)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("heroTitle")
        title.setStyleSheet("font-size: 32px;")
        layout.addWidget(title)

        api_card = Card()
        api_card.body.addWidget(self._h("OpenAI API configuration"))
        note = QLabel("Your key is stored locally in a .env file and is never written to application logs.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        api_card.body.addWidget(note)
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("sk-...")
        self.key_input.setText(get_api_key())
        api_card.body.addWidget(QLabel("API key"))
        api_card.body.addWidget(self.key_input)
        api_card.body.addWidget(QLabel("Model"))
        self.model = QComboBox()
        self.model.addItems(SUPPORTED_MODELS)
        current = get_model()
        if current not in SUPPORTED_MODELS:
            self.model.addItem(current)
        self.model.setCurrentText(current)
        api_card.body.addWidget(self.model)
        save = QPushButton("Save API settings")
        save.setObjectName("primaryButton")
        save.clicked.connect(self._save)
        api_card.body.addWidget(save, alignment=Qt.AlignmentFlag.AlignLeft)
        self.save_status = QLabel("")
        self.save_status.setObjectName("muted")
        api_card.body.addWidget(self.save_status)
        layout.addWidget(api_card)

        privacy = Card()
        privacy.body.addWidget(self._h("Privacy preferences"))
        privacy.body.addWidget(self._p(PRIVACY_NOTICE))
        self.ack = QCheckBox("I understand that document text is sent to OpenAI when I request analysis.")
        self.ack.setChecked(True)
        self.ack.toggled.connect(self.privacy_changed.emit)
        privacy.body.addWidget(self.ack)
        layout.addWidget(privacy)

        about = Card()
        about.body.addWidget(self._h("Application information"))
        about.body.addWidget(QLabel(f"ClearClause AI  v{__version__}"))
        about.body.addWidget(self._p(LEGAL_DISCLAIMER))
        layout.addWidget(about)
        layout.addStretch()

    def _h(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def _p(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("muted")
        return label

    def _save(self) -> None:
        self.save_api.emit(self.key_input.text().strip(), self.model.currentText())
        self.save_status.setText("API settings saved on this computer.")

    def acknowledged(self) -> bool:
        return self.ack.isChecked()
