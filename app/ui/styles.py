"""Warm cream / terracotta theme matching the ClearClause mockup."""

APP_STYLESHEET = """
QMainWindow, QWidget {
    background: transparent;
    color: #4A2C1A;
    font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px;
}
QScrollBar::handle:vertical {
    background: #D9C4B0;
    border-radius: 5px;
    min-height: 32px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QLabel { background: transparent; }

QLineEdit, QTextEdit, QPlainTextEdit {
    background: #FFFCFA;
    border: 1px solid #E8D9C8;
    border-radius: 12px;
    padding: 10px 14px;
    color: #4A2C1A;
    selection-background-color: #E8C4A8;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #C45C26;
}

QComboBox {
    background: #FFFCFA;
    border: 1px solid #E8D9C8;
    border-radius: 10px;
    padding: 8px 12px;
    min-height: 22px;
}
QComboBox::drop-down { border: none; width: 24px; }

QPushButton {
    border: none;
    border-radius: 18px;
    padding: 10px 22px;
    font-weight: 600;
}

QPushButton#primaryButton {
    background: #C45C26;
    color: #FFF8F2;
}
QPushButton#primaryButton:hover { background: #A94B1C; }
QPushButton#primaryButton:disabled { background: #D9B49A; color: #FFF8F2; }

QPushButton#accentButton {
    background: #D4894A;
    color: #FFF8F2;
    padding: 12px 28px;
}
QPushButton#accentButton:hover { background: #C77838; }
QPushButton#accentButton:disabled { background: #E2C2A4; }

QPushButton#ghostButton {
    background: #F6EDE3;
    color: #6B3E24;
    border: 1px solid #E8D9C8;
}
QPushButton#ghostButton:hover { background: #EFE2D4; }

QPushButton#navButton {
    background: transparent;
    color: #6B3E24;
    text-align: left;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton#navButton:hover { background: rgba(196, 92, 38, 0.08); }
QPushButton#navButton[active="true"] {
    background: #C45C26;
    color: #FFF8F2;
    font-weight: 600;
}

QPushButton#chipButton {
    background: #F4EBE1;
    color: #6B3E24;
    border-radius: 14px;
    padding: 8px 14px;
    font-weight: 500;
}
QPushButton#chipButton:hover { background: #EADBCB; }

QListWidget, QTableWidget {
    background: #FFFCFA;
    border: 1px solid #E8D9C8;
    border-radius: 14px;
    padding: 6px;
    outline: none;
}
QListWidget::item, QTableWidget::item {
    padding: 10px;
    border-radius: 8px;
}
QListWidget::item:selected, QTableWidget::item:selected {
    background: #F3E0D2;
    color: #4A2C1A;
}

QHeaderView::section {
    background: #F6EDE3;
    color: #6B3E24;
    padding: 8px;
    border: none;
    font-weight: 600;
}

QProgressBar {
    border: none;
    background: #F0E4D6;
    border-radius: 8px;
    height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background: #C45C26;
    border-radius: 8px;
}

QCheckBox, QRadioButton { spacing: 8px; }

QFrame#card {
    background: #FFFCFA;
    border: 1px solid rgba(196, 146, 110, 0.18);
    border-radius: 22px;
}

QFrame#sidebar {
    background: rgba(255, 250, 245, 0.88);
    border-right: 1px solid rgba(196, 146, 110, 0.22);
}

QLabel#heroTitle {
    font-family: Palatino, "Palatino Linotype", "Times New Roman", serif;
    font-size: 42px;
    font-weight: 700;
    color: #5C2E18;
}
QLabel#heroTagline {
    font-family: Palatino, "Palatino Linotype", "Times New Roman", serif;
    font-size: 22px;
    color: #C45C26;
}
QLabel#sectionTitle {
    font-family: Palatino, "Palatino Linotype", "Times New Roman", serif;
    font-size: 20px;
    font-weight: 700;
    color: #5C2E18;
}
QLabel#muted {
    color: #8A6A55;
}
QLabel#disclaimer {
    color: #8A6A55;
    font-size: 11px;
}
"""
