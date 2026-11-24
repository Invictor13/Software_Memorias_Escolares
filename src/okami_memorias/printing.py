"""Dados dos PDFs concluídos para preparar a impressão."""

from dataclasses import dataclass
from pathlib import Path

from .layouts import page_count


@dataclass(frozen=True)
class PrintDocument:
    path: Path
    pages: int

    @classmethod
    def from_photos(cls, path: Path, photos: int) -> "PrintDocument":
        return cls(path, page_count(photos))
