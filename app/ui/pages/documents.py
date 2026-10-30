from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.types import DocumentRecord
from app.ui.widgets.cards import Card


class DocumentsPage(QWidget):
    open_document = Signal(int)
    delete_document = Signal(int)
    search_changed = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 36, 28)

        title = QLabel("My Documents")
        title.setObjectName("heroTitle")
        title.setStyleSheet("font-size: 32px;")
        layout.addWidget(title)

        card = Card()
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by file name...")
        self.status = QComboBox()
        self.status.addItems(["All statuses", "uploaded", "analyzing", "analyzed", "error"])
        self.search.textChanged.connect(self._emit_search)
        self.status.currentTextChanged.connect(self._emit_search)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.status, 1)
        card.body.addLayout(filters)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Uploaded", "Type", "Status", "Risk"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._open_row)
        card.body.addWidget(self.table)

        actions = QHBoxLayout()
        open_btn = QPushButton("Open analysis")
        open_btn.setObjectName("primaryButton")
        open_btn.clicked.connect(self._open_selected)
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("ghostButton")
        delete_btn.clicked.connect(self._delete_selected)
        actions.addWidget(open_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        card.body.addLayout(actions)
        layout.addWidget(card, 1)

        self._ids: list[int] = []

    def _emit_search(self) -> None:
        status = self.status.currentText()
        self.search_changed.emit(self.search.text(), "" if status == "All statuses" else status)

    def set_documents(self, records: list[DocumentRecord]) -> None:
        self.table.setRowCount(0)
        self._ids = []
        for rec in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            risk = "—"
            if rec.analysis:
                counts = rec.analysis.risk_counts
                risk = f"H{counts.get('high', 0)} / M{counts.get('medium', 0)} / L{counts.get('low', 0)}"
            values = [rec.name, rec.uploaded_at, rec.file_type.upper(), rec.status, risk]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if rec.id is not None:
                    item.setData(Qt.ItemDataRole.UserRole, rec.id)
                self.table.setItem(row, col, item)
            if rec.id is not None:
                self._ids.append(rec.id)

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._ids):
            return None
        return self._ids[row]

    def _open_row(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._ids):
            self.open_document.emit(self._ids[row])

    def _open_selected(self) -> None:
        doc_id = self._selected_id()
        if doc_id is not None:
            self.open_document.emit(doc_id)

    def _delete_selected(self) -> None:
        doc_id = self._selected_id()
        if doc_id is not None:
            self.delete_document.emit(doc_id)
