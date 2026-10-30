"""Background workers so the UI stays responsive during AI calls."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from app.services.document_service import DocumentService


class AnalysisWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, service: DocumentService, document_id: int) -> None:
        super().__init__()
        self.service = service
        self.document_id = document_id

    @Slot()
    def run(self) -> None:
        try:
            result = self.service.analyze(self.document_id)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class ChatWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, service: DocumentService, document_id: int, question: str) -> None:
        super().__init__()
        self.service = service
        self.document_id = document_id
        self.question = question

    @Slot()
    def run(self) -> None:
        try:
            answer = self.service.ask(self.document_id, self.question)
            self.finished.emit(answer)
        except Exception as exc:
            self.failed.emit(str(exc))
