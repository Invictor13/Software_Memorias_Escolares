"""Janela de seleção, configuração e exportação do mosaico."""

from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

from ..batch import BatchResult, export_class, scan_class
from ..core import generate_album
from ..decoration import THEMES, TITLE_LIMIT, compose_page
from ..errors import OperationCancelled
from ..layouts import Mosaic, page_count
from ..printing import PrintDocument
from .class_panel import ClassPanel, show_batch_result
from .preview import PagePreview
from .print_dialog import PrintDialog
from .tasks import FolderScan, Job, preview_student, scan_folder

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
        self.resize(980, 800)
        self.setStyleSheet(STYLE)
        self.job: Job | None = None
        self.scan: FolderScan | None = None
        self.directory: Path | None = None
        self.destination: Path | None = None
        self.batch_result: BatchResult | None = None
        self.print_documents: tuple[PrintDocument, ...] = ()
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

        self.mode = QComboBox()
        self.mode.addItems(["Álbum único", "Turma — PDFs por aluno"])
        self.mode.setAccessibleName("Tipo de exportação")
        settings.addWidget(self.mode)
        self.source_label = label("Pasta de fotos", "section")
        settings.addWidget(self.source_label)
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
        self.class_panel = ClassPanel()
        self.class_panel.selector.currentIndexChanged.connect(self.select_student)
        self.class_panel.hide()
        settings.addWidget(self.class_panel)

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
        self.use_student_title = QCheckBox("Usar o nome do aluno como título")
        self.use_student_title.toggled.connect(self.update_preview)
        self.use_student_title.hide()
        settings.addWidget(self.use_student_title)

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
        self.target_label = label("Destino do PDF", "section")
        settings.addWidget(self.target_label)
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
        self.result_button = QPushButton("Ver resultado do lote")
        self.result_button.clicked.connect(self.show_result)
        self.result_button.hide()
        self.print_button = QPushButton("Preparar impressão")
        self.print_button.clicked.connect(self.prepare_printing)
        self.print_button.hide()
        self.export = QPushButton("Gerar PDF", objectName="primary")
        self.export.clicked.connect(self.start_export)
        footer.addWidget(self.status, 1)
        footer.addWidget(self.progress)
        footer.addWidget(self.cancel)
        footer.addWidget(self.result_button)
        footer.addWidget(self.print_button)
        footer.addWidget(self.export)
        body.addLayout(footer)
        self.mode.currentIndexChanged.connect(self.change_mode)
        self.update_preview()

    @property
    def is_class(self) -> bool:
        return self.mode.currentIndex() == 1

    def change_mode(self) -> None:
        self.directory = self.destination = self.scan = None
        self.source.clear()
        self.target.clear()
        self.source.setToolTip("")
        self.target.setToolTip("")
        self.status.clear()
        self.summary.setText("Nenhuma pasta selecionada.")
        self.issues.hide()
        self.class_panel.set_students(())
        self.clear_result()
        self.class_panel.setVisible(self.is_class)
        self.use_student_title.setVisible(self.is_class)
        self.source_label.setText("Pasta da turma" if self.is_class else "Pasta de fotos")
        self.source.setAccessibleName(self.source_label.text())
        self.target_label.setText("Pasta dos PDFs" if self.is_class else "Destino do PDF")
        self.target.setAccessibleName(self.target_label.text())
        self.export.setText("Exportar turma" if self.is_class else "Gerar PDF")
        self.update_preview()

    def layout_settings(self) -> Mosaic:
        return Mosaic(**{name: field.value() for name, field in self.margins.items()})

    def update_preview(self) -> None:
        student = self.class_panel.selected if self.is_class else None
        use_name = self.is_class and self.use_student_title.isChecked()
        common_title = "" if use_name else self.album_title.text()
        self.album_title.setEnabled(not use_name and self.job is None)
        layout = self.layout_settings()
        theme = THEMES[self.theme.currentIndex()]
        design = None
        error = ""
        valid_settings = False
        try:
            design = compose_page(layout, theme, common_title)
            valid_settings = True
            if use_name and student:
                design = compose_page(layout, theme, student.name)
        except ValueError as exc:
            design = None
            error = str(exc)
        self.layout_error.setText(error)
        self.layout_error.setVisible(bool(error))
        usable = self.scan is not None and not self.scan.invalid
        self.preview.set_page(design, self.scan.preview if usable else ())
        pages = page_count(self.scan.total) if usable else 0
        heading = f"Prévia da página 1 de {pages}" if pages else "Prévia da primeira página"
        if student:
            heading = f"{heading} · {student.name}"
        self.page_label.setText(
            self.page_label.fontMetrics().elidedText(
                heading, Qt.TextElideMode.ElideRight, max(290, self.preview.width())
            )
        )
        self.page_label.setToolTip(heading)
        ready = any(item.ready for item in self.class_panel.students) if self.is_class else usable
        self.export.setEnabled(bool(valid_settings and ready and self.destination and not self.job))

    def pick_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self, "Escolher pasta da turma" if self.is_class else "Escolher pasta de fotos",
            self.source.text(),
        )
        if selected:
            self.load_folder(Path(selected))

    def load_folder(self, directory: Path) -> None:
        self.directory = directory
        self.source.setText(str(directory))
        self.source.setToolTip(str(directory))
        self.scan = None
        self.clear_result()
        self.issues.hide()
        self.summary.setText("Verificando fotos…")
        if self.is_class:
            self.class_panel.set_students(())
            self.start_job(lambda operation: scan_class(directory, operation), self.class_finished)
        else:
            self.start_job(lambda operation: scan_folder(directory, operation), self.folder_finished)

    def class_finished(self, job: Job) -> None:
        if job.error:
            self.summary.setText("Turma ainda não validada.")
            self.show_job_error(job)
            return
        self.summary.clear()
        self.class_panel.set_students(job.result)
        self.select_student()

    def select_student(self) -> None:
        self.scan = None
        self.update_preview()
        student = self.class_panel.selected
        if student and student.ready:
            self.start_job(lambda operation: preview_student(student.directory, operation),
                           self.student_preview_finished)

    def student_preview_finished(self, job: Job) -> None:
        if job.error:
            self.show_job_error(job)
            return
        student = self.class_panel.selected
        self.scan = FolderScan(student.total, (), job.result)
        self.status.clear()

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
        if self.is_class:
            folder = QFileDialog.getExistingDirectory(
                self, "Escolher pasta dos PDFs", str(self.destination or self.directory or "")
            )
            if folder:
                self.set_destination(Path(folder))
            return
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
        self.clear_result()
        self.update_preview()

    def start_export(self) -> None:
        directory, destination, layout = self.directory, self.destination, self.layout_settings()
        theme = THEMES[self.theme.currentIndex()]
        title = self.album_title.text()
        self.clear_result()
        if self.is_class:
            students = self.class_panel.students
            use_name = self.use_student_title.isChecked()
            self.start_job(
                lambda operation: export_class(students, destination, operation, layout=layout,
                                               theme=theme, title=title, student_titles=use_name),
                self.batch_finished,
            )
            return
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
            self.set_print_documents((PrintDocument.from_photos(self.destination, job.result),))

    def set_print_documents(self, documents: tuple[PrintDocument, ...]) -> None:
        self.print_documents = documents
        self.print_button.setVisible(bool(documents))

    def prepare_printing(self) -> None:
        PrintDialog(self.print_documents, self).exec()

    def clear_result(self) -> None:
        self.batch_result = None
        self.result_button.hide()
        self.set_print_documents(())

    def batch_finished(self, job: Job) -> None:
        if job.error:
            self.show_job_error(job)
            return
        result = self.batch_result = job.result
        prefix = "Lote cancelado · " if result.pending else ""
        self.batch_summary = (f"{prefix}{len(result.generated)} PDF(s) gerado(s) · "
                              f"{len(result.failed)} falha(s) · {len(result.skipped)} ignorado(s)"
                              + (f" · {len(result.pending)} pendente(s)" if result.pending else ""))
        self.status.setText(self.batch_summary)
        self.result_button.show()
        self.set_print_documents(result.documents)

    def show_result(self) -> None:
        show_batch_result(self, self.batch_summary, self.batch_result)

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

    @Slot()
    def finish_job(self) -> None:
        job = self.job
        job.wait()
        self.job = None
        on_finished, self._on_finished = self._on_finished, None
        job.operation = None
        job.deleteLater()
        if self._closing:
            self.close()
            return
        self.set_busy(False)
        on_finished(job)
        self.update_preview()

    def set_busy(self, busy: bool) -> None:
        for widget in (self.mode, self.choose_source, self.choose_target, self.issues,
                       self.theme, self.use_student_title, self.class_panel, self.result_button,
                       self.print_button,
                       *self.margins.values()):
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
