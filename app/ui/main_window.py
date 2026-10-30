"""Main desktop window with sidebar navigation and mockup-inspired home."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
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
from app.document_processing.extractor import extract_document
from app.services.document_service import DocumentService
from app.ui.background import SceneBackground
from app.ui.pages.analysis import AnalysisPage
from app.ui.pages.assistant import AssistantPage
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.documents import DocumentsPage
from app.ui.pages.settings import SettingsPage
from app.ui.pages.upload import UploadPage
from app.ui.styles import APP_STYLESHEET
from app.ui.workers import AnalysisWorker, ChatWorker


NAV_ITEMS = [
    ("dashboard", "🏠  Dashboard"),
    ("upload", "⬆  Upload Contract"),
    ("documents", "📁  My Documents"),
    ("analysis", "🔍  Contract Analysis"),
    ("assistant", "💬  AI Assistant"),
    ("settings", "⚙  Settings"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ClearClause AI — Understand Before You Sign.")
        self.resize(1440, 920)
        self.setMinimumSize(1100, 760)
        self.setStyleSheet(APP_STYLESHEET)

        self.service = DocumentService()
        self.current_document_id: int | None = None
        self.pending_path: str | None = None
        self._thread: QThread | None = None
        self._worker = None

        self.background = SceneBackground()
        self.setCentralWidget(self.background)

        overlay = QWidget(self.background)
        overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        shell = QHBoxLayout(overlay)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        shell.addWidget(self._build_sidebar())
        self.stack = QStackedWidget()
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_host = QWidget()
        content_layout = QVBoxLayout(content_host)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stack)
        content_scroll.setWidget(content_host)
        shell.addWidget(content_scroll, 1)

        self.pages = {
            "dashboard": DashboardPage(),
            "upload": UploadPage(),
            "documents": DocumentsPage(),
            "analysis": AnalysisPage(),
            "assistant": AssistantPage(),
            "settings": SettingsPage(),
        }
        for key in ("dashboard", "upload", "documents", "analysis", "assistant", "settings"):
            self.stack.addWidget(self.pages[key])

        self._wire()
        self._show_page("dashboard")
        self.refresh_lists()
        self.overlay = overlay

        disclaimer = QAction("Legal disclaimer", self)
        disclaimer.triggered.connect(self._show_disclaimer)
        self.menuBar().addAction(disclaimer)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.overlay.setGeometry(self.background.rect())

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.overlay.setGeometry(self.background.rect())

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(6)

        brand = QLabel("ClearClause AI")
        brand.setStyleSheet(
            'font-family: Palatino, "Times New Roman", serif; font-size: 18px; font-weight: 700; color: #5C2E18;'
        )
        tag = QLabel("Understand Before You Sign.")
        tag.setStyleSheet("color: #C45C26; font-size: 11px;")
        layout.addWidget(brand)
        layout.addWidget(tag)
        layout.addSpacing(18)

        self.nav_buttons: dict[str, QPushButton] = {}
        for key, label in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()
        analyze = QPushButton("Analyze a New Contract")
        analyze.setObjectName("primaryButton")
        analyze.setCursor(Qt.CursorShape.PointingHandCursor)
        analyze.clicked.connect(lambda: self._show_page("upload"))
        layout.addWidget(analyze)
        return sidebar

    def _wire(self) -> None:
        dash: DashboardPage = self.pages["dashboard"]
        upload: UploadPage = self.pages["upload"]
        docs: DocumentsPage = self.pages["documents"]
        assistant: AssistantPage = self.pages["assistant"]
        settings: SettingsPage = self.pages["settings"]

        dash.choose_file_requested.connect(self._choose_file)
        dash.file_dropped.connect(self._handle_path)
        dash.analyze_requested.connect(self._analyze_current)
        dash.question_submitted.connect(self._ask_from_dashboard)
        dash.open_recent.connect(self._open_document)

        upload.choose_file_requested.connect(self._choose_file)
        upload.file_dropped.connect(self._handle_path)
        upload.analyze_requested.connect(self._analyze_current)
        upload.remove_file.connect(self._clear_pending)

        docs.search_changed.connect(self._filter_documents)
        docs.open_document.connect(self._open_document)
        docs.delete_document.connect(self._delete_document)

        assistant.send_question.connect(self._ask_from_assistant)
        assistant.document_changed.connect(self._select_document)

        settings.save_api.connect(self._save_api)

    def _show_page(self, key: str) -> None:
        order = ["dashboard", "upload", "documents", "analysis", "assistant", "settings"]
        self.stack.setCurrentIndex(order.index(key))
        for nav_key, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if nav_key == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a contract",
            str(Path.home()),
            "Documents (*.pdf *.docx *.doc *.txt)",
        )
        if path:
            self._handle_path(path)

    def _handle_path(self, path: str) -> None:
        suffix = Path(path).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            QMessageBox.warning(self, "Unsupported file", "Please choose a PDF, Word, or text document.")
            return
        try:
            extracted = extract_document(path)
        except Exception as exc:
            QMessageBox.warning(self, "Could not read file", str(exc))
            return
        self.pending_path = path
        self.pages["dashboard"].set_selected_file(path)
        notes = "\n".join(extracted.notes)
        self.pages["upload"].set_file(path, extracted.full_text, notes)
        if extracted.notes:
            self.pages["dashboard"].status_label.setText(
                "Some pages needed extra processing. Review the upload preview for details."
            )

    def _clear_pending(self) -> None:
        self.pending_path = None
        self.pages["upload"].clear_file()
        self.pages["dashboard"].drop_zone.set_file_name("")
        self.pages["dashboard"].analyze_btn.setEnabled(False)

    def _confirm_privacy(self) -> bool:
        if not self.pages["settings"].acknowledged():
            QMessageBox.information(
                self,
                "Privacy preference",
                "Enable the privacy acknowledgement in Settings before sending a document to OpenAI.",
            )
            self._show_page("settings")
            return False
        box = QMessageBox(self)
        box.setWindowTitle("Before we analyze")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("Document text will be sent to OpenAI for this analysis.")
        box.setInformativeText(PRIVACY_NOTICE + "\n\n" + LEGAL_DISCLAIMER)
        box.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok)
        box.button(QMessageBox.StandardButton.Ok).setText("I understand — analyze")
        return box.exec() == QMessageBox.StandardButton.Ok

    def _analyze_current(self) -> None:
        if not get_api_key():
            QMessageBox.information(
                self,
                "API key needed",
                "Add your OpenAI API key in Settings before analyzing a document.",
            )
            self._show_page("settings")
            return
        if not self._confirm_privacy():
            return
        if self.pending_path:
            category = self.pages["dashboard"].current_category()
            try:
                record = self.service.import_file(self.pending_path, category=category)
            except Exception as exc:
                QMessageBox.warning(self, "Upload failed", str(exc))
                return
            self.current_document_id = record.id
            self.pending_path = None
        if self.current_document_id is None:
            QMessageBox.information(self, "No document", "Choose a file first.")
            return
        self._start_analysis(self.current_document_id)

    def _start_analysis(self, document_id: int) -> None:
        self.pages["dashboard"].set_busy(True, "Analyzing your document… this can take a moment.")
        self.pages["upload"].set_busy(True, "Analyzing your document…")
        self._thread = QThread(self)
        self._worker = AnalysisWorker(self.service, document_id)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_analysis_done)
        self._worker.failed.connect(self._on_analysis_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.start()

    def _on_analysis_done(self, result) -> None:
        self.pages["dashboard"].set_busy(False, "Analysis complete.")
        self.pages["upload"].set_busy(False, "Analysis complete.")
        record = self.service.db.get_document(self.current_document_id or 0)
        if record and result:
            record.analysis = result
            self.pages["dashboard"].show_analysis(record, result)
            self.pages["analysis"].show_record(record)
        self.refresh_lists()
        self._show_page("analysis")

    def _on_analysis_failed(self, message: str) -> None:
        self.pages["dashboard"].set_busy(False, "Analysis could not be completed.")
        self.pages["upload"].set_busy(False, "Analysis could not be completed.")
        QMessageBox.warning(self, "Analysis failed", message)

    def _ask_from_dashboard(self, question: str) -> None:
        self._ask(question, from_dashboard=True)

    def _ask_from_assistant(self, question: str) -> None:
        self._ask(question, from_dashboard=False)

    def _ask(self, question: str, from_dashboard: bool) -> None:
        if self.current_document_id is None:
            QMessageBox.information(self, "Select a document", "Analyze or open a document first.")
            return
        if not get_api_key():
            self._show_page("settings")
            return
        self.pages["assistant"].set_busy(True)
        self.pages["dashboard"].status_label.setText("Asking your document…")
        self._thread = QThread(self)
        self._worker = ChatWorker(self.service, self.current_document_id, question)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(lambda answer: self._on_chat_done(answer, from_dashboard))
        self._worker.failed.connect(self._on_chat_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.start()

    def _on_chat_done(self, answer: str, from_dashboard: bool) -> None:
        self.pages["assistant"].set_busy(False)
        self.pages["assistant"].add_message("assistant", answer)
        self.pages["dashboard"].show_answer(answer)
        self.pages["dashboard"].status_label.setText("")
        if from_dashboard:
            pass

    def _on_chat_failed(self, message: str) -> None:
        self.pages["assistant"].set_busy(False)
        self.pages["dashboard"].status_label.setText("")
        QMessageBox.warning(self, "Assistant unavailable", message)

    def refresh_lists(self, search: str = "", status: str = "") -> None:
        records = self.service.db.list_documents(search=search, status=status)
        self.pages["documents"].set_documents(records)
        self.pages["dashboard"].set_stats(self.service.db.stats())
        analyzed = [r for r in records if r.status == "analyzed"]
        self.pages["dashboard"].set_recent(analyzed or records[:4])
        self.pages["assistant"].set_documents(records, self.current_document_id)

    def _filter_documents(self, search: str, status: str) -> None:
        self.refresh_lists(search, status)

    def _open_document(self, document_id: int) -> None:
        self._select_document(document_id)
        record = self.service.db.get_document(document_id)
        if record:
            self.pages["analysis"].show_record(record)
            if record.analysis:
                self.pages["dashboard"].show_analysis(record, record.analysis)
        self._show_page("analysis")

    def _select_document(self, document_id: int) -> None:
        self.current_document_id = document_id
        history = self.service.db.get_chat_history(document_id)
        self.pages["assistant"].set_history(history)

    def _delete_document(self, document_id: int) -> None:
        confirm = QMessageBox.question(
            self,
            "Delete document",
            "Delete this document, its stored file, analysis, and chat history from this computer?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.service.delete(document_id)
        if self.current_document_id == document_id:
            self.current_document_id = None
        self.refresh_lists()

    def _save_api(self, key: str, model: str) -> None:
        save_api_settings(key, model)

    def _show_disclaimer(self) -> None:
        QMessageBox.information(self, "Legal disclaimer", LEGAL_DISCLAIMER)
