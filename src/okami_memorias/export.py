"""Renderização PDF e publicação atômica em um destino novo."""

import os
from io import BytesIO
from math import ceil
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .decoration import TITLE_FONT_NAME, PageDesign
from .errors import ExportError
from .imaging import load_photo
from .layouts import A4_HEIGHT, A4_WIDTH
from .operation import Operation

PRINT_DPI = 300


def render_pdf(stream, photos: list[Path], design: PageDesign,
               operation: Operation | None = None) -> None:
    pdf = Canvas(stream, pagesize=(A4_WIDTH * mm, A4_HEIGHT * mm),
                 pageCompression=1, invariant=1)
    pdf.setTitle("Álbum de fotografias")
    pdf.setAuthor("OKAMI Memórias Escolares")
    pdf.setSubject("Mosaico fotográfico A4")
    if operation:
        operation.progress("Montando páginas", 0, len(photos))
    for offset in range(0, len(photos), len(design.slots)):
        page_photos = photos[offset:offset + len(design.slots)]
        for fill in design.fills(len(page_photos)):
            pdf.setFillColor(HexColor(fill.color))
            rect = fill.rect
            pdf.rect(rect.x * mm, rect.y * mm, rect.width * mm, rect.height * mm,
                     fill=1, stroke=0)
        if heading := design.heading:
            pdf.setFillColor(HexColor(heading.color))
            pdf.setFont(TITLE_FONT_NAME, heading.size * mm)
            pdf.drawString(heading.x * mm, heading.baseline * mm, heading.text)
        for index, (path, slot) in enumerate(zip(page_photos, design.slots), start=offset + 1):
            if operation:
                operation.checkpoint()
            with load_photo(path) as photo, BytesIO() as encoded:
                area = slot.contain(*photo.size)
                photo.thumbnail(
                    (max(1, ceil(area.width * PRINT_DPI / 25.4)),
                     max(1, ceil(area.height * PRINT_DPI / 25.4))),
                    Image.Resampling.LANCZOS,
                )
                photo.info.clear()
                photo.save(encoded, format="JPEG", quality=92, subsampling=0)
                encoded.seek(0)
                pdf.drawImage(ImageReader(encoded), area.x * mm, area.y * mm,
                              area.width * mm, area.height * mm)
            if operation:
                operation.progress("Montando páginas", index, len(photos))
        pdf.showPage()
    if operation:
        operation.progress("Salvando PDF", 0, 0)
    pdf.save()


def export_pdf(destination: Path, photos: list[Path], design: PageDesign,
               operation: Operation | None = None) -> None:
    temporary = None
    try:
        if os.path.lexists(destination):
            raise FileExistsError("O arquivo de destino já existe.")
        with NamedTemporaryFile(mode="w+b", suffix=".tmp", prefix=".okami-",
                                dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            render_pdf(stream, photos, design, operation)
        if operation:
            operation.checkpoint()
        # No Windows, rename recusa destinos existentes. Em POSIX, link dá a mesma garantia.
        if os.name == "nt":
            temporary.rename(destination)
        else:
            os.link(temporary, destination)
    except OSError as exc:
        raise ExportError(f"Não foi possível salvar {destination}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
