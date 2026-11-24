"""Ponto de entrada da interface desktop."""

import sys


def main() -> int:
    from PySide6.QtCore import QLocale
    from PySide6.QtWidgets import QApplication

    from .window import MainWindow

    QLocale.setDefault(QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil))
    app = QApplication(sys.argv)
    app.setApplicationName("OKAMI Memórias Escolares")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
