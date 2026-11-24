"""Prévia da primeira folha usando a mesma geometria que o PDF."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..layouts import A4_HEIGHT, A4_WIDTH, Rect
from .tasks import PreviewPhoto


class PagePreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(290, 340)
        self.setAccessibleName("Prévia da primeira página A4")
        self.slots: tuple[Rect, ...] = ()
        self.photos: tuple[PreviewPhoto, ...] = ()

    def set_page(self, slots: tuple[Rect, ...], photos: tuple[PreviewPhoto, ...]) -> None:
        self.slots = slots
        self.photos = photos
        self.update()

    def paintEvent(self, event) -> None:
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.fillRect(self.rect(), QColor("#e8eeeb"))
            scale = min((self.width() - 44) / A4_WIDTH, (self.height() - 44) / A4_HEIGHT)
            left = (self.width() - A4_WIDTH * scale) / 2
            top = (self.height() - A4_HEIGHT * scale) / 2

            def to_screen(rect: Rect) -> QRectF:
                return QRectF(left + rect.x * scale,
                              top + (A4_HEIGHT - rect.y - rect.height) * scale,
                              rect.width * scale, rect.height * scale)

            paper = to_screen(Rect(0, 0, A4_WIDTH, A4_HEIGHT))
            painter.fillRect(paper.translated(3, 4), QColor("#c7d2cd"))
            painter.fillRect(paper, QColor("white"))
            pen = QPen(QColor("#a7b9af"))
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            # Guias cinza mostram a área de cada foto somente na prévia.
            for slot in self.slots:
                painter.drawRect(to_screen(slot))
            for slot, photo in zip(self.slots, self.photos):
                painter.drawImage(to_screen(slot.contain(*photo.size)), photo.image)
