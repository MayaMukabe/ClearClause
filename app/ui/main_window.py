"""Single-window health insurance workspace."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    LEGAL_DISCLAIMER,
    PRIVACY_NOTICE,
    SUPPORTED_EXTENSIONS,
    get_api_key,
    save_api_settings,
)
from app.services.document_service import DocumentService
from app.ui.background import SceneBackground
from app.ui.dialogs import LetterDialog, PasteTextDialog, SettingsDialog
from app.ui.pages.home import HomePage
from app.ui.styles import APP_STYLESHEET
from app.ui.workers import AnalysisWorker, LetterWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ClearClause AI — Understand Your Health Insurance.")
        self.resize(1440, 920)
        self.setMinimumSize(1080, 740)
        self.setStyleSheet(APP_STYLESHEET)
        self.menuBar().hide()

        self.service = DocumentService()
        self.current_document_id: int | None = None
        self._thread: QThread | None = None
        self._worker = None
        self._letter_dialog: LetterDialog | None = None

        self.background = SceneBackground()
        self.setCentralWidget(self.background)

        self.overlay = QWidget(self.background)
        shell = QVBoxLayout(self.overlay)
        shell.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.home = HomePage()
        scroll.setWidget(self.home)
        shell.addWidget(scroll)

        self.home.choose_file_requested.connect(self._choose_file)
        self.home.file_dropped.connect(self._import_path)
        self.home.paste_requested.connect(self._paste_text)
        self.home.claim_requested.connect(lambda: self._draft_letter("claim"))
        self.home.appeal_requested.connect(lambda: self._draft_letter("appeal"))
        self.home.settings_requested.connect(self._open_settings)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.overlay.setGeometry(self.background.rect())

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.overlay.setGeometry(self.background.rect())

    def _choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a health document",
            str(Path.home()),
            "Health documents (*.pdf *.docx *.txt *.png *.jpg *.jpeg *.webp *.tif *.tiff)",
        )
        if path:
            self._import_path(path)

    def _import_path(self, path: str) -> None:
        suffix = Path(path).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            QMessageBox.warning(
                self,
                "Unsupported file",
                "Please choose a PDF, Word, image, or text file.",
            )
            return
        try:
            record = self.service.import_file(path)
        except Exception as exc:
            QMessageBox.warning(self, "Could not read file", str(exc))
            return
        self.current_document_id = record.id
        self.home.set_selected_file(path)
        self._analyze_current()

    def _paste_text(self) -> None:
        dialog = PasteTextDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        text = dialog.text()
        if not text:
            QMessageBox.information(self, "Nothing pasted", "Paste some document text first.")
            return
        try:
            record = self.service.import_text(text)
        except Exception as exc:
            QMessageBox.warning(self, "Could not save text", str(exc))
            return
        self.current_document_id = record.id
        self.home.set_pasted()
        self._analyze_current()

    def _confirm_privacy(self) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle("Before we analyze")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("Document text will be sent to OpenAI for this analysis.")
        box.setInformativeText(PRIVACY_NOTICE + "\n\n" + LEGAL_DISCLAIMER)
        box.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok)
        box.button(QMessageBox.StandardButton.Ok).setText("I understand — continue")
        return box.exec() == QMessageBox.StandardButton.Ok

    def _analyze_current(self) -> None:
        if not get_api_key():
            QMessageBox.information(
                self,
                "API key needed",
                "Add your OpenAI API key (API key button, top right) before analyzing.",
            )
            self._open_settings()
            return
        if self.current_document_id is None:
            return
        if not self._confirm_privacy():
            self.home.set_busy(False, "Analysis cancelled.")
            return
        self._run_worker(
            AnalysisWorker(self.service, self.current_document_id),
            busy_message="Analyzing your health document… this can take a moment.",
            on_done=self._on_analysis_done,
            on_fail=self._on_analysis_failed,
        )

    def _on_analysis_done(self, result) -> None:
        self.home.set_busy(False, "Analysis complete.")
        record = self.service.db.get_document(self.current_document_id or 0)
        if record and result:
            record.analysis = result
            self.home.show_analysis(record, result)

    def _on_analysis_failed(self, message: str) -> None:
        self.home.set_busy(False, "Analysis could not be completed.")
        QMessageBox.warning(self, "Analysis failed", message)

    def _draft_letter(self, kind: str) -> None:
        if self.current_document_id is None:
            QMessageBox.information(
                self,
                "Upload a document first",
                "Choose a file or paste text so the letter can use your document.",
            )
            return
        if not get_api_key():
            self._open_settings()
            return
        title = "Create a Claim" if kind == "claim" else "Create an Appeal"
        self._letter_dialog = LetterDialog(title, self)
        self._letter_dialog.show()
        self._run_worker(
            LetterWorker(self.service, self.current_document_id, kind),
            busy_message=f"Drafting your {kind}…",
            on_done=self._on_letter_done,
            on_fail=self._on_letter_failed,
        )

    def _on_letter_done(self, letter: str) -> None:
        self.home.set_busy(False, "Draft ready.")
        if self._letter_dialog:
            self._letter_dialog.set_letter(letter)

    def _on_letter_failed(self, message: str) -> None:
        self.home.set_busy(False, "Could not draft the letter.")
        if self._letter_dialog:
            self._letter_dialog.set_error(message)
        else:
            QMessageBox.warning(self, "Draft failed", message)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            key, model = dialog.values()
            save_api_settings(key, model)
            self.home.status_label.setText("API settings saved on this computer.")

    def _run_worker(self, worker, *, busy_message: str, on_done, on_fail) -> None:
        self.home.set_busy(True, busy_message)
        self._thread = QThread(self)
        self._worker = worker
        worker.moveToThread(self._thread)
        self._thread.started.connect(worker.run)
        worker.finished.connect(on_done)
        worker.failed.connect(on_fail)
        worker.finished.connect(self._thread.quit)
        worker.failed.connect(self._thread.quit)
        self._thread.start()
