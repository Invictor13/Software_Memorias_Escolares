"""Janela de seleção, configuração e exportação do mosaico."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

from ..core import generate_album
from ..decoration import THEMES, TITLE_LIMIT, compose_page
from ..errors import OperationCancelled
from ..layouts import Mosaic, PHOTOS_PER_PAGE
from .preview import PagePreview
from .tasks import FolderScan, Job, scan_folder

STYLE = """
QWidget#window { background: #f4f7f5; color: #182b23; }
QFrame#card { background: white; border: 1px solid #d8e2dc; border-radius: 12px; }
QLabel#title { font-size: 25px; font-weight: 700; color: #17382d; }
QLabel#section { font-weight: 700; color: #17382d; }
QLabel#secondary { color: #425c50; }
QPushButton#primary { background: #17624b; color: white; border-radius: 6px;
                      padding: 8px 14px; font-weight: 700; }
QPushButton#primary:hover { background: #134c3b; }
QPushButton#primary:focus { border: 2px solid #102f25; padding: 6px 12px; }
QPushButton#primary:disabled { background: #dce7e1; color: #435f52; }
"""


def label(text: str, role: str = "") -> QLabel:
    widget = QLabel(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setObjectName(role)
    return widget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OKAMI Memórias Escolares")
        self.setObjectName("window")
        self.resize(960, 720)
        self.setStyleSheet(STYLE)
        self.job: Job | None = None
        self.scan: FolderScan | None = None
        self.directory: Path | None = None
        self.destination: Path | None = None
        self._closing = False

        body = QVBoxLayout(self)
        body.setContentsMargins(22, 18, 22, 18)
        body.setSpacing(12)
        body.addWidget(label("OKAMI Memórias Escolares", "title"))
        columns = QHBoxLayout()
        columns.setSpacing(14)
        body.addLayout(columns, 1)

        controls = QFrame(objectName="card")
        controls.setMinimumWidth(335)
        settings = QVBoxLayout(controls)
        settings.setContentsMargins(16, 14, 16, 14)
        settings.setSpacing(8)
        columns.addWidget(controls, 1)

        settings.addWidget(label("Pasta de fotos", "section"))
        self.source = QLineEdit(readOnly=True, placeholderText="Selecione uma pasta")
        self.source.setAccessibleName("Pasta de fotos")
        self.choose_source = QPushButton("Escolher pasta…")
        self.choose_source.clicked.connect(self.pick_folder)
        source_row = QHBoxLayout()
        source_row.addWidget(self.source, 1)
        source_row.addWidget(self.choose_source)
        settings.addLayout(source_row)
        self.summary = label("Nenhuma pasta selecionada.", "secondary")
        self.summary.setWordWrap(True)
        settings.addWidget(self.summary)
        self.issues = QPushButton("Ver arquivos inválidos")
        self.issues.clicked.connect(self.show_issues)
        self.issues.hide()
        settings.addWidget(self.issues, alignment=Qt.AlignmentFlag.AlignLeft)

        settings.addSpacing(8)
        settings.addWidget(label("Modelo do mosaico", "section"))
        self.theme = QComboBox()
        self.theme.setAccessibleName("Modelo do mosaico")
        self.theme.addItems([theme.name for theme in THEMES])
        self.theme.currentIndexChanged.connect(self.update_preview)
        settings.addWidget(self.theme)
        self.album_title = QLineEdit(placeholderText="Título opcional")
        self.album_title.setAccessibleName("Título opcional")
        self.album_title.setMaxLength(TITLE_LIMIT)
        self.album_title.textChanged.connect(self.update_preview)
        settings.addWidget(self.album_title)

        settings.addSpacing(8)
        settings.addWidget(label("Margens e espaçamento", "section"))
        self.margins = {}
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        defaults = Mosaic()
        for field, name in (
            ("left", "Esquerda (encadernação)"), ("right", "Direita"),
            ("top", "Superior"), ("bottom", "Inferior"), ("gap", "Entre fotos"),
        ):
            spin = QDoubleSpinBox()
            spin.setRange(0, 297)
            spin.setSuffix(" mm")
            spin.setSingleStep(1)
            spin.setValue(getattr(defaults, field))
            spin.setAccessibleName(name)
            spin.valueChanged.connect(self.update_preview)
            self.margins[field] = spin
            form.addRow(name, spin)
        settings.addLayout(form)
        self.layout_error = label("")
        self.layout_error.setWordWrap(True)
        self.layout_error.hide()
        settings.addWidget(self.layout_error)

        settings.addSpacing(8)
        settings.addWidget(label("Destino do PDF", "section"))
        self.target = QLineEdit(readOnly=True, placeholderText="Selecione onde salvar")
        self.target.setAccessibleName("Destino do PDF")
        self.choose_target = QPushButton("Escolher destino…")
        self.choose_target.clicked.connect(self.pick_destination)
        target_row = QHBoxLayout()
        target_row.addWidget(self.target, 1)
        target_row.addWidget(self.choose_target)
        settings.addLayout(target_row)
        settings.addStretch()

        preview_card = QFrame(objectName="card")
        preview_column = QVBoxLayout(preview_card)
        preview_column.setContentsMargins(14, 14, 14, 14)
        self.page_label = label("Prévia da primeira página", "section")
        preview_column.addWidget(self.page_label)
        self.preview = PagePreview()
        preview_column.addWidget(self.preview, 1)
        preview_column.addWidget(label("A4 retrato · 210 × 297 mm · grade 2 × 2", "secondary"))
        columns.addWidget(preview_card, 2)

        footer = QHBoxLayout()
        self.status = label("", "secondary")
        self.status.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setAccessibleName("Progresso da operação")
        self.progress.setFixedWidth(135)
        self.progress.hide()
        self.cancel = QPushButton("Cancelar")
        self.cancel.clicked.connect(self.cancel_job)
        self.cancel.hide()
        self.export = QPushButton("Gerar PDF", objectName="primary")
        self.export.clicked.connect(self.start_export)
        footer.addWidget(self.status, 1)
        footer.addWidget(self.progress)
        footer.addWidget(self.cancel)
        footer.addWidget(self.export)
        body.addLayout(footer)
        self.update_preview()

    def layout_settings(self) -> Mosaic:
        return Mosaic(**{name: field.value() for name, field in self.margins.items()})

    def update_preview(self) -> None:
        try:
            design = compose_page(self.layout_settings(), THEMES[self.theme.currentIndex()],
                                  self.album_title.text())
            error = ""
        except ValueError as exc:
            design = None
            error = str(exc)
        self.layout_error.setText(error)
        self.layout_error.setVisible(bool(error))
        usable = self.scan is not None and not self.scan.invalid
        self.preview.set_page(design, self.scan.preview if usable else ())
        pages = (self.scan.total + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE if usable else 0
        self.page_label.setText(
            f"Prévia da página 1 de {pages}" if pages else "Prévia da primeira página"
        )
        self.export.setEnabled(bool(design and usable and self.destination and not self.job))

    def pick_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Escolher pasta de fotos",
                                                      self.source.text())
        if selected:
            self.load_folder(Path(selected))

    def load_folder(self, directory: Path) -> None:
        self.directory = directory
        self.source.setText(str(directory))
        self.source.setToolTip(str(directory))
        self.scan = None
        self.issues.hide()
        self.summary.setText("Verificando fotos…")
        self.start_job(lambda operation: scan_folder(directory, operation), self.folder_finished)

    def folder_finished(self, job: Job) -> None:
        if job.error:
            self.summary.setText("Pasta ainda não validada.")
            self.show_job_error(job)
            return
        self.scan = job.result
        invalid = len(self.scan.invalid)
        valid = self.scan.total - invalid
        self.summary.setText(f"Fotos encontradas: {self.scan.total}  ·  Válidas: {valid}"
                             + (f"  ·  Inválidas: {invalid}" if invalid else ""))
        self.issues.setVisible(bool(invalid))
        self.status.setText("Corrija os arquivos inválidos e selecione a pasta novamente."
                            if invalid else "")

    def show_issues(self) -> None:
        dialog = QMessageBox(QMessageBox.Icon.Warning, "Arquivos inválidos",
                             "Estes arquivos não puderam ser lidos como fotografias.",
                             parent=self)
        dialog.setTextFormat(Qt.TextFormat.PlainText)
        dialog.setDetailedText("\n".join(self.scan.invalid))
        dialog.exec()

    def pick_destination(self) -> None:
        dialog = QFileDialog(self, "Salvar mosaico", str(self.destination or self.directory or ""))
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter("Documento PDF (*.pdf)")
        dialog.setDefaultSuffix("pdf")
        dialog.setOption(QFileDialog.Option.DontConfirmOverwrite)
        if dialog.exec():
            self.set_destination(Path(dialog.selectedFiles()[0]))

    def set_destination(self, path: Path) -> None:
        self.destination = path
        self.target.setText(str(path))
        self.target.setToolTip(str(path))
        self.status.clear()
        self.update_preview()

    def start_export(self) -> None:
        directory, destination, layout = self.directory, self.destination, self.layout_settings()
        theme = THEMES[self.theme.currentIndex()]
        title = self.album_title.text()
        self.start_job(
            lambda operation: generate_album(directory, destination, layout, operation=operation,
                                             theme=theme, title=title),
            self.export_finished,
        )

    def export_finished(self, job: Job) -> None:
        if job.error:
            self.show_job_error(job)
        else:
            self.status.setText(f"PDF salvo com {job.result} foto(s).")
            self.status.setToolTip(str(self.destination))

    def show_job_error(self, job: Job) -> None:
        if isinstance(job.error, OperationCancelled):
            self.status.setText("Operação cancelada.")
        else:
            self.status.setText("Não foi possível concluir a operação.")
            dialog = QMessageBox(QMessageBox.Icon.Warning, "Falha na operação",
                                 str(job.error), parent=self)
            dialog.setTextFormat(Qt.TextFormat.PlainText)
            dialog.exec()

    def start_job(self, task, on_finished) -> None:
        job = self.job = Job(task, self)
        self._on_finished = on_finished
        job.progress.connect(self.update_progress)
        job.finished.connect(self.finish_job)
        self.set_busy(True)
        self.update_progress("Preparando…", 0, 0)
        job.start()

    def finish_job(self) -> None:
        job = self.job
        self.job = None
        job.deleteLater()
        if self._closing:
            self.close()
            return
        self.set_busy(False)
        self._on_finished(job)
        self.update_preview()

    def set_busy(self, busy: bool) -> None:
        for widget in (self.choose_source, self.choose_target, self.issues,
                       self.theme, self.album_title, *self.margins.values()):
            widget.setEnabled(not busy)
        self.cancel.setVisible(busy)
        self.cancel.setEnabled(busy)
        self.progress.setVisible(busy)
        self.update_preview()

    def update_progress(self, phase: str, completed: int, total: int) -> None:
        if self.cancel.isEnabled():
            self.status.setText(phase)
            self.progress.setRange(0, total)
            self.progress.setValue(completed)

    def cancel_job(self) -> None:
        self.job.operation.cancel()
        self.cancel.setEnabled(False)
        self.status.setText("Cancelando…")

    def closeEvent(self, event) -> None:
        if self.job is not None:
            self._closing = True
            self.cancel_job()
            event.ignore()
        else:
            super().closeEvent(event)
