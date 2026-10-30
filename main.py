#!/usr/bin/env python3
"""Launch ClearClause AI."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import QApplication

from app.config import load_environment
from app.ui.main_window import MainWindow


def main() -> int:
    load_environment()
    app = QApplication(sys.argv)
    app.setApplicationName("ClearClause AI")
    app.setOrganizationName("ClearClause")
    font = QFont("Avenir Next")
    if not font.exactMatch():
        font = QFont("Segoe UI")
    app.setFont(font)

    window = MainWindow()
    screen = QGuiApplication.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        window.resize(min(1480, geo.width() - 40), min(940, geo.height() - 40))
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
