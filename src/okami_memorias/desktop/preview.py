"""Prévia da primeira folha usando a mesma geometria que o PDF."""

from functools import cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..decoration import TITLE_FONT_FILE, PageDesign
from ..layouts import A4_HEIGHT, A4_WIDTH, Rect
from .tasks import PreviewPhoto


@cache
def preview_heading_font() -> QFont:
    font_id = QFontDatabase.addApplicationFont(str(TITLE_FONT_FILE))
    families = QFontDatabase.applicationFontFamilies(font_id)
    font = QFont(families[0]) if families else QFont()
    font.setBold(True)
    font.setKerning(False)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    font.setPixelSize(1000)
    return font


class PagePreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(290, 340)
        self.setAccessibleName("Prévia da primeira página A4")
        self.design: PageDesign | None = None
        self.photos: tuple[PreviewPhoto, ...] = ()

    @property
    def slots(self) -> tuple[Rect, ...]:
        return self.design.slots if self.design else ()

    def set_page(self, design: PageDesign | None, photos: tuple[PreviewPhoto, ...]) -> None:
        self.design = design
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
            if self.design is None:
                painter.fillRect(paper, QColor("white"))
                return
            for fill in self.design.fills(len(self.photos)):
                painter.fillRect(to_screen(fill.rect), QColor(fill.color))
            if not self.photos or not self.design.frames:
                pen = QPen(QColor("#a7b9af"))
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                for slot in self.slots:
                    painter.drawRect(to_screen(slot))
            for slot, photo in zip(self.slots, self.photos):
                painter.drawImage(to_screen(slot.contain(*photo.size)), photo.image)
            if heading := self.design.heading:
                painter.setFont(preview_heading_font())
                painter.setPen(QColor(heading.color))
                painter.translate(left + heading.x * scale,
                                  top + (A4_HEIGHT - heading.baseline) * scale)
                font_scale = heading.size * scale / 1000
                painter.scale(font_scale, font_scale)
                painter.drawText(QPointF(0, 0), heading.text)
