"""Geometria do mosaico, em milímetros e com origem no canto inferior esquerdo."""

from dataclasses import dataclass
from math import isfinite

A4_WIDTH = 210
A4_HEIGHT = 297
PHOTOS_PER_PAGE = 4


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    def contain(self, width: int, height: int) -> "Rect":
        scale = min(self.width / width, self.height / height)
        fitted_width = width * scale
        fitted_height = height * scale
        return Rect(
            self.x + (self.width - fitted_width) / 2,
            self.y + (self.height - fitted_height) / 2,
            fitted_width,
            fitted_height,
        )


@dataclass(frozen=True)
class Mosaic:
    left: float = 20
    right: float = 10
    top: float = 10
    bottom: float = 10
    gap: float = 5

    def slots(self) -> tuple[Rect, ...]:
        if any(not isfinite(value) or value < 0 for value in (
            self.left, self.right, self.top, self.bottom, self.gap
        )):
            raise ValueError("Margens e espaçamento devem ser finitos e não negativos.")
        width = (A4_WIDTH - self.left - self.right - self.gap) / 2
        height = (A4_HEIGHT - self.top - self.bottom - self.gap) / 2
        if width <= 0 or height <= 0:
            raise ValueError("As margens e o espaçamento devem deixar espaço para a grade A4.")
        return tuple(
            Rect(self.left + column * (width + self.gap),
                 self.bottom + row * (height + self.gap), width, height)
            for row in (1, 0) for column in (0, 1)
        )
