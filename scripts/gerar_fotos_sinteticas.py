"""Cria cinco imagens fictícias para demonstração local."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path)
    directory = parser.parse_args().destino
    directory.mkdir(parents=True, exist_ok=True)
    for index, size in enumerate(
        ((900, 600), (600, 900), (850, 850), (960, 540), (540, 960)), start=1
    ):
        with Image.new("RGB", size, (25 * index, 60, 135)) as photo:
            ImageDraw.Draw(photo).rectangle((40, 40, 240, 240), fill="white")
            with (directory / f"sintetica-{index:02}.png").open("xb") as output:
                photo.save(output, format="PNG")


if __name__ == "__main__":
    main()
