from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 22, 24, 22)
        self._layout.setSpacing(12)

    @property
    def body(self) -> QVBoxLayout:
        return self._layout


class ActionCard(QFrame):
    clicked = Signal()

    def __init__(self, icon: str, title: str, subtitle: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QFrame#actionCard {
                background: #FBF6F0;
                border: 1px solid #EADBCB;
                border-radius: 16px;
            }
            QFrame#actionCard:hover { border: 1px solid #C45C26; }
            """
        )
        self.setObjectName("actionCard")
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 16, 18, 16)
        glyph = QLabel(icon)
        glyph.setStyleSheet("font-size: 22px;")
        texts = QVBoxLayout()
        texts.setSpacing(2)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 700; color: #5C2E18; font-size: 15px;")
        sub = QLabel(subtitle)
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #8A6A55; font-size: 12px;")
        texts.addWidget(title_label)
        texts.addWidget(sub)
        chevron = QLabel("›")
        chevron.setStyleSheet("font-size: 26px; color: #C45C26; font-weight: 400;")
        row.addWidget(glyph)
        row.addLayout(texts, 1)
        row.addWidget(chevron)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit()
        super().mousePressEvent(event)


class RiskTile(QFrame):
    def __init__(self, icon: str, label: str, caption: str, color: str, bg: str) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QFrame {{ background: {bg}; border-radius: 16px; }}"
            f"QLabel#icon {{ font-size: 22px; }}"
            f"QLabel#title {{ color: {color}; font-size: 15px; font-weight: 700; }}"
            f"QLabel#caption {{ color: {color}; font-size: 12px; }}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        icon_label = QLabel(icon)
        icon_label.setObjectName("icon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel(label)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.caption = QLabel(caption)
        self.caption.setObjectName("caption")
        self.caption.setWordWrap(True)
        self.caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(self.caption)

    def set_count(self, value: int) -> None:
        base = self.caption.text().split("\n")[0]
        if "Items" in base or "Standard" in base or "—" in self.caption.text():
            pass
        self.caption.setToolTip(f"{value} item(s)")


def labeled_row(icon: str, label: str, value: str = "—") -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 8, 0, 8)
    icon_label = QLabel(icon)
    icon_label.setFixedWidth(28)
    name = QLabel(label)
    name.setStyleSheet("color: #8A6A55;")
    val = QLabel(value)
    val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    val.setWordWrap(True)
    val.setStyleSheet("color: #5C2E18; font-weight: 500;")
    layout.addWidget(icon_label)
    layout.addWidget(name)
    layout.addStretch()
    layout.addWidget(val, 1)
    row.value_label = val  # type: ignore[attr-defined]
    return row
