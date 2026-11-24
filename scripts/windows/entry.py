"""Ponto de entrada do executável empacotado."""

import sys
from pathlib import Path

from okami_memorias.desktop.__main__ import main


def verify_installation(source: Path, destination: Path) -> int:
    from PySide6.QtWidgets import QApplication

    from okami_memorias.batch import export_class, scan_class
    from okami_memorias.decoration import THEMES
    from okami_memorias.desktop.window import MainWindow
    from okami_memorias.layouts import Mosaic
    from okami_memorias.operation import Operation

    app = QApplication([sys.argv[0]])
    window = MainWindow()
    window.show()
    app.processEvents()
    operation = Operation(lambda *_: None)
    try:
        result = export_class(scan_class(source, operation), destination, operation,
                              layout=Mosaic(left=25), theme=THEMES[1], student_titles=True)
        if result.documents and not (result.failed or result.skipped):
            return 0
        with (destination / "diagnostico-okami.txt").open("x", encoding="utf-8") as report:
            for student, reason in result.failed:
                print(f"{student.name}: {reason}", file=report)
            for student in result.skipped:
                print(f"{student.name}: {student.issue or ', '.join(student.invalid)}",
                      file=report)
        return 1
    finally:
        window.close()


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--verificar-instalacao":
        raise SystemExit(verify_installation(Path(sys.argv[2]), Path(sys.argv[3])))
    raise SystemExit(main())
