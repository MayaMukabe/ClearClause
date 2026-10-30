from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.config import SUPPORTED_EXTENSIONS


class DropZone(QWidget):
    file_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        icon = QLabel("📄")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 28px;")

        title = QLabel("Upload Your Document")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hint = QLabel("Drag and drop your file here or click to browse")
        self.hint.setObjectName("muted")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        support = QLabel("Supports PDF, Word, and other document types")
        support.setObjectName("muted")
        support.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support.setStyleSheet("color: #A18470; font-size: 12px;")

        self.choose = QPushButton("  Choose File")
        self.choose.setObjectName("primaryButton")
        self.choose.setCursor(Qt.CursorShape.PointingHandCursor)
        self.choose.setFixedWidth(160)

        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("color: #C45C26; font-weight: 600;")

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(self.hint)
        layout.addWidget(support)
        layout.addSpacing(6)
        layout.addWidget(self.choose, alignment=Qt.AlignmentFlag.AlignCenter)
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
            self.hint.setText("Please drop a PDF, Word, or text document.")
            return
        self.file_selected.emit(path)
