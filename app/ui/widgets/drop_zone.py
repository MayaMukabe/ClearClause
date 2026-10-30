from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.config import SUPPORTED_EXTENSIONS


class DropZone(QWidget):
    file_selected = Signal(str)
    paste_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QWidget#dropZone {
                background: #FBF6F0;
                border: 1.5px dashed #E0C8B0;
                border-radius: 18px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(8)

        icon = QLabel("📄")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 30px;")

        title = QLabel("Upload Your Health Document")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            'font-family: Palatino, "Times New Roman", serif; font-size: 20px; font-weight: 700; color: #5C2E18;'
        )

        self.hint = QLabel("Drag and drop your file here or click to browse")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setStyleSheet("color: #8A6A55;")

        support = QLabel("Supports PDF, Word, and image files")
        support.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support.setStyleSheet("color: #A18470; font-size: 12px;")

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.choose = QPushButton("  Choose File")
        self.choose.setObjectName("primaryButton")
        self.choose.setCursor(Qt.CursorShape.PointingHandCursor)
        self.choose.setFixedWidth(160)
        self.paste = QPushButton("Paste text")
        self.paste.setObjectName("ghostButton")
        self.paste.setCursor(Qt.CursorShape.PointingHandCursor)
        self.paste.clicked.connect(self.paste_requested.emit)
        buttons.addWidget(self.choose)
        buttons.addWidget(self.paste)

        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("color: #C45C26; font-weight: 600;")

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(self.hint)
        layout.addWidget(support)
        layout.addSpacing(8)
        layout.addLayout(buttons)
        layout.addWidget(self.file_label)

    def set_file_name(self, name: str) -> None:
        self.file_label.setText(name)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        suffix = Path(path).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            self.hint.setText("Please drop a PDF, Word, image, or text file.")
            return
        self.file_selected.emit(path)
