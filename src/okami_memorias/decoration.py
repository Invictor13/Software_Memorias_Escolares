"""Composição vetorial para a prévia e o PDF, em milímetros."""

from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from unicodedata import normalize

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .layouts import A4_HEIGHT, A4_WIDTH, Mosaic, Rect

TITLE_FONT_FILE = Path(reportlab.__file__).with_name("fonts") / "VeraBd.ttf"
TITLE_FONT_NAME = "OKAMI-Vera-Bold"
TITLE_LIMIT = 100


@dataclass(frozen=True)
class Palette:
    paper: str
    frame: str
    ink: str
    accent: str


@dataclass(frozen=True)
class Theme:
    name: str
    palette: Palette | None = None
    accent_spans: tuple[tuple[float, float], ...] = ()


WHITE = Theme("Branco")
THEMES = (
    WHITE,
    Theme("Caderno azul", Palette("#e7f0fb", "#829cbb", "#18395c", "#ecb948"), ((0, 0.25),)),
    Theme("Jardim da turma", Palette("#eef3e1", "#86a184", "#264c3f", "#c27564"),
          ((0, 0.06), (0.08, 0.06), (0.16, 0.06))),
)


@dataclass(frozen=True)
class Fill:
    rect: Rect
    color: str


@dataclass(frozen=True)
class Heading:
    text: str
    x: float
    baseline: float
    size: float
    color: str


@dataclass(frozen=True)
class PageDesign:
    slots: tuple[Rect, ...]
    background: tuple[Fill, ...]
    frames: tuple[tuple[Fill, ...], ...] = ()
    heading: Heading | None = None

    def fills(self, count: int) -> tuple[Fill, ...]:
        return self.background + tuple(fill for frame in self.frames[:count] for fill in frame)


@cache
def title_font() -> TTFont:
    font = TTFont(TITLE_FONT_NAME, str(TITLE_FONT_FILE))
    pdfmetrics.registerFont(font)
    return font


def _heading(title: str, x: float, top: float, width: float, color: str) -> Heading:
    font = title_font()
    if len(title) > TITLE_LIMIT or not title.isprintable():
        raise ValueError(f"O título deve ter até {TITLE_LIMIT} caracteres em uma linha.")
    if any(ord(char) not in font.face.charWidths for char in title):
        raise ValueError("O título contém caracteres que a fonte do modelo não suporta.")
    em_width = font.stringWidth(title, 1)
    size = min(6, width / em_width)
    if size < 3:
        raise ValueError("Reduza o título ou as margens laterais para caber na página.")
    return Heading(title, x + (width - size * em_width) / 2, top - 9, size, color)


def compose_page(layout: Mosaic, theme: Theme = WHITE, title: str = "") -> PageDesign:
    slots = layout.slots()
    title = normalize("NFC", title.strip())
    paper = Fill(Rect(0, 0, A4_WIDTH, A4_HEIGHT), "#ffffff")
    palette = theme.palette
    if not palette and not title:
        return PageDesign(slots, (paper,))

    width = A4_WIDTH - layout.left - layout.right
    top = A4_HEIGHT - layout.top
    inset = 3 if palette else 0
    header = 15 if title else 0
    if palette:
        header += 7
    try:
        grid = replace(layout, left=layout.left + inset, right=layout.right + inset,
                       top=layout.top + header, bottom=layout.bottom + inset).slots()
    except ValueError as exc:
        raise ValueError("As margens e o espaçamento deixam pouco espaço para este modelo.") from exc

    inner_left = layout.left + inset
    inner_width = width - 2 * inset
    heading = None
    if title:
        heading = _heading(title, inner_left, top - inset, inner_width,
                           palette.ink if palette else "#222222")
    if not palette:
        return PageDesign(grid, (paper,), heading=heading)

    accent_y = top - header + 2
    background = (
        paper,
        Fill(Rect(layout.left, layout.bottom, width, top - layout.bottom), palette.paper),
        Fill(Rect(inner_left, accent_y, inner_width, 0.9), palette.ink),
        *(Fill(Rect(inner_left + start * inner_width, accent_y, span * inner_width, 0.9),
               palette.accent) for start, span in theme.accent_spans),
    )
    areas = []
    frames = []
    for cell in grid:
        border = min(0.65, cell.width / 8, cell.height / 8)
        padding = min(2, cell.width / 4, cell.height / 4)
        mat = Rect(cell.x + border, cell.y + border,
                   cell.width - 2 * border, cell.height - 2 * border)
        frames.append((Fill(cell, palette.frame), Fill(mat, "#ffffff")))
        areas.append(Rect(cell.x + padding, cell.y + padding,
                          cell.width - 2 * padding, cell.height - 2 * padding))
    return PageDesign(tuple(areas), background, tuple(frames), heading)
