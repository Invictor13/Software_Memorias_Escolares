"""Descoberta, validação e normalização de fotografias locais."""

import warnings
from pathlib import Path

from PIL import Image, ImageOps

from .errors import PhotoError

FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG"}


def discover(directory: Path) -> list[Path]:
    try:
        paths = [
            path for path in directory.iterdir()
            if path.suffix.lower() in FORMATS and path.is_file()
        ]
    except OSError as exc:
        raise PhotoError(f"Não foi possível ler a pasta {directory}: {exc}") from exc
    if not paths:
        raise PhotoError(f"Nenhuma fotografia JPG, JPEG ou PNG encontrada em {directory}.")
    return sorted(paths, key=lambda path: (path.name.casefold(), path.name))


def load_photo(path: Path) -> Image.Image:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path, formats=[FORMATS[path.suffix.lower()]]) as source:
                source.load()
                with ImageOps.exif_transpose(source) as oriented:
                    if "A" in oriented.getbands() or "transparency" in oriented.info:
                        with oriented.convert("RGBA") as rgba:
                            with Image.new("RGBA", rgba.size, "white") as white:
                                white.alpha_composite(rgba)
                                return white.convert("RGB")
                    return oriented.convert("RGB")
    except (OSError, ValueError, SyntaxError, KeyError, OverflowError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise PhotoError(f"Fotografia inválida ou ilegível: {path}") from exc
