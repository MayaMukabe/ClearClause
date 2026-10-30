from __future__ import annotations

from PySide6.QtCore import Qt
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


class RiskTile(QFrame):
    def __init__(self, label: str, color: str, bg: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QFrame {{ background: {bg}; border-radius: 16px; }}"
            f"QLabel#count {{ color: {color}; font-size: 22px; font-weight: 700; }}"
            f"QLabel#caption {{ color: {color}; font-size: 12px; font-weight: 600; }}"
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(12, 16, 12, 16)
        self.count_label = QLabel("—")
        self.count_label.setObjectName("count")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption = QLabel(label)
        caption.setObjectName("caption")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_label)
        layout.addWidget(caption)

    def set_count(self, value: int | str) -> None:
        self.count_label.setText(str(value))


def labeled_row(icon: str, label: str, value: str = "—") -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 4, 0, 4)
    icon_label = QLabel(icon)
    icon_label.setFixedWidth(28)
    name = QLabel(label)
    name.setObjectName("muted")
    val = QLabel(value)
    val.setObjectName("valueLabel")
    val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    val.setWordWrap(True)
    layout.addWidget(icon_label)
    layout.addWidget(name)
    layout.addStretch()
    layout.addWidget(val, 1)
    row.value_label = val  # type: ignore[attr-defined]
    return row
