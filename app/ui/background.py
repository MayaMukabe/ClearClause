"""Warm interior backdrop with Unsplash photos, matching the mockup."""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from app.config import images_dir


class SceneBackground(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        folder = images_dir()
        self.interior = QPixmap(str(folder / "warm-interior.jpg"))
        self.flowers = QPixmap(str(folder / "dried-flowers.jpg"))
        if self.flowers.isNull():
            self.flowers = QPixmap(str(folder / "autumn-bouquet.jpg"))
        self.books = QPixmap(str(folder / "books.jpg"))
        self.mug = QPixmap(str(folder / "ceramic-mug.jpg"))
        if self.mug.isNull():
            self.mug = QPixmap(str(folder / "coffee-cup.jpg"))

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#F6E9DA"))
        gradient.setColorAt(0.5, QColor("#EEDCC8"))
        gradient.setColorAt(1.0, QColor("#E8D3BC"))
        painter.fillRect(self.rect(), gradient)

        if not self.interior.isNull():
            scaled = self.interior.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.setOpacity(0.32)
            painter.drawPixmap(x, y, scaled)
            painter.setOpacity(1.0)

        wash = QLinearGradient(0, 0, 0, self.height())
        wash.setColorAt(0.0, QColor(246, 233, 218, 80))
        wash.setColorAt(1.0, QColor(232, 211, 188, 90))
        painter.fillRect(self.rect(), wash)

        if not self.flowers.isNull():
            height = int(self.height() * 0.38)
            scaled = self.flowers.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
            painter.setOpacity(0.88)
            painter.drawPixmap(self.width() - scaled.width() - 80, 8, scaled)
            painter.setOpacity(1.0)
        if not self.mug.isNull():
            width = min(200, int(self.width() * 0.14))
            scaled = self.mug.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
            painter.setOpacity(0.9)
            painter.drawPixmap(QRect(self.width() - scaled.width() - 28, int(self.height() * 0.16), scaled.width(), scaled.height()), scaled)
            painter.setOpacity(1.0)
        if not self.books.isNull():
            width = min(210, int(self.width() * 0.14))
            scaled = self.books.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
            painter.setOpacity(0.75)
            painter.drawPixmap(self.width() - scaled.width() - 140, 90, scaled)
            painter.setOpacity(1.0)

        light = QLinearGradient(self.width() * 0.5, 0, self.width(), self.height() * 0.35)
        light.setColorAt(0.0, QColor(255, 248, 235, 0))
        light.setColorAt(1.0, QColor(255, 236, 210, 80))
        painter.fillRect(self.rect(), light)
