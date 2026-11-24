"""Operações executadas fora da thread da janela."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from ..errors import PhotoError
from ..imaging import discover, load_photo
from ..layouts import PHOTOS_PER_PAGE
from ..operation import Operation


@dataclass(frozen=True)
class PreviewPhoto:
    size: tuple[int, int]
    image: QImage


@dataclass(frozen=True)
class FolderScan:
    total: int
    invalid: tuple[str, ...]
    preview: tuple[PreviewPhoto, ...]


def scan_folder(directory: Path, operation: Operation) -> FolderScan:
    paths = discover(directory)
    invalid = []
    preview = []
    operation.progress("Verificando pasta", 0, len(paths))
    for index, path in enumerate(paths, start=1):
        try:
            with load_photo(path) as photo:
                if len(preview) < PHOTOS_PER_PAGE:
                    size = photo.size
                    photo.thumbnail((640, 640), Image.Resampling.LANCZOS)
                    width, height = photo.size
                    image = QImage(photo.tobytes(), width, height, width * 3,
                                   QImage.Format.Format_RGB888).copy()
                    preview.append(PreviewPhoto(size, image))
        except PhotoError:
            invalid.append(path.name)
        operation.progress("Verificando pasta", index, len(paths))
    return FolderScan(len(paths), tuple(invalid), tuple(preview))


class Job(QThread):
    progress = Signal(str, int, int)

    def __init__(self, task: Callable[[Operation], object], parent):
        super().__init__(parent)
        self._task = task
        self.operation = Operation(self.progress.emit)
        self.result = None
        self.error = None

    def run(self) -> None:
        try:
            self.result = self._task(self.operation)
        except Exception as exc:
            self.error = exc
