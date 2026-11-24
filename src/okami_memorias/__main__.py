"""Interface de linha de comando do núcleo P0."""

import argparse
import sys
from pathlib import Path

from .core import generate_album
from .errors import ExportError, PhotoError
from .layouts import PHOTOS_PER_PAGE, Mosaic


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera um mosaico fotográfico em PDF A4.")
    parser.add_argument("--input", required=True, type=Path, help="Pasta de fotografias")
    parser.add_argument("--output", required=True, type=Path, help="Caminho de um novo PDF")
    parser.add_argument("--photos-per-page", type=int, choices=[PHOTOS_PER_PAGE],
                        default=PHOTOS_PER_PAGE, help="Quantidade de espaços por página")
    parser.add_argument("--binding-margin-mm", type=float, default=20, help="Margem esquerda")
    parser.add_argument("--right-margin-mm", type=float, default=10, help="Margem direita")
    parser.add_argument("--top-margin-mm", type=float, default=10, help="Margem superior")
    parser.add_argument("--bottom-margin-mm", type=float, default=10, help="Margem inferior")
    parser.add_argument("--gap-mm", type=float, default=5, help="Espaçamento da grade")
    args = parser.parse_args(argv)
    layout = Mosaic(left=args.binding_margin_mm, right=args.right_margin_mm,
                    top=args.top_margin_mm, bottom=args.bottom_margin_mm, gap=args.gap_mm)
    try:
        count = generate_album(args.input, args.output, layout)
    except (PhotoError, ExportError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Exportação cancelada.", file=sys.stderr)
        return 130
    print(f"PDF salvo em {args.output} com {count} fotografia(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
