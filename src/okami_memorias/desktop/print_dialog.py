"""Conferência da ordem e das configurações de impressão."""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QHeaderView, QLabel, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from ..printing import PrintDocument


class PrintDialog(QDialog):
    def __init__(self, documents: tuple[PrintDocument, ...], parent=None):
        super().__init__(parent)
        self.documents = documents
        self.setWindowTitle("Preparar impressão")
        self.resize(590, 410)
        layout = QVBoxLayout(self)
        pages = sum(document.pages for document in documents)
        layout.addWidget(QLabel(f"Arquivos: {len(documents)}  ·  Páginas: {pages}"))
        self.table = QTableWidget(len(documents), 3)
        self.table.setHorizontalHeaderLabels(["Ordem", "Arquivo PDF", "Páginas"])
        self.table.setAccessibleName("PDFs em ordem de impressão")
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for row, document in enumerate(documents):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            item = QTableWidgetItem(document.path.name)
            item.setToolTip(str(document.path))
            self.table.setItem(row, 1, item)
            self.table.setItem(row, 2, QTableWidgetItem(str(document.pages)))
        self.table.selectRow(0)
        self.table.cellDoubleClicked.connect(self.open_selected)
        layout.addWidget(self.table, 1)

        guidance = QLabel(
            "No leitor de PDF, selecione papel A4, orientação retrato e escala de 100% "
            "(Tamanho real). Desative opções como Ajustar à página. Imprima uma folha de "
            "teste e confira a margem de encadernação com uma régua antes de imprimir o lote."
        )
        guidance.setWordWrap(True)
        layout.addWidget(guidance)
        buttons = QHBoxLayout()
        open_pdf = QPushButton("Abrir PDF selecionado")
        open_pdf.setAutoDefault(False)
        open_pdf.clicked.connect(self.open_selected)
        open_folder = QPushButton("Abrir pasta")
        open_folder.setAutoDefault(False)
        open_folder.clicked.connect(lambda: self.open_path(documents[0].path.parent))
        close = QPushButton("Fechar")
        close.setDefault(True)
        close.clicked.connect(self.accept)
        buttons.addWidget(open_pdf)
        buttons.addWidget(open_folder)
        buttons.addStretch()
        buttons.addWidget(close)
        layout.addLayout(buttons)

    def open_selected(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.open_path(self.documents[row].path)

    def open_path(self, path: Path) -> None:
        if not path.exists() or not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.absolute()))):
            QMessageBox.warning(self, "Preparar impressão",
                                "Não foi possível abrir o arquivo ou a pasta no sistema.")
