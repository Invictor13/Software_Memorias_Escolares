"""Orquestração do fluxo de geração de álbuns."""

from pathlib import Path

from .errors import ExportError
from .export import export_pdf
from .imaging import discover, load_photo
from .layouts import Mosaic


def generate_album(directory: Path, destination: Path, layout: Mosaic = Mosaic()) -> int:
    slots = layout.slots()
    if destination.suffix.lower() != ".pdf":
        raise ExportError("O destino deve usar a extensão .pdf.")
    photos = discover(directory)
    for path in photos:
        load_photo(path).close()
    export_pdf(destination, photos, slots)
    return len(photos)
