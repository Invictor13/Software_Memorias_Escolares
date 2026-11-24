"""Orquestração do fluxo de geração de álbuns."""

from pathlib import Path

from .errors import ExportError
from .export import export_pdf
from .imaging import discover, load_photo
from .layouts import Mosaic
from .operation import Operation


def generate_album(directory: Path, destination: Path, layout: Mosaic = Mosaic(),
                   *, operation: Operation | None = None) -> int:
    slots = layout.slots()
    if destination.suffix.lower() != ".pdf":
        raise ExportError("O destino deve usar a extensão .pdf.")
    photos = discover(directory)
    if operation:
        operation.progress("Validando fotos", 0, len(photos))
    for index, path in enumerate(photos, start=1):
        load_photo(path).close()
        if operation:
            operation.progress("Validando fotos", index, len(photos))
    export_pdf(destination, photos, slots, operation)
    return len(photos)
