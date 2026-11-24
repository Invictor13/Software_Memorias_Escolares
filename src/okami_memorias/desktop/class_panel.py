"""Lista de alunos e leitura dos resultados da turma."""

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import QComboBox, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from ..batch import BatchResult, Student


class ClassPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.students: tuple[Student, ...] = ()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.selector = QComboBox()
        self.selector.setAccessibleName("Aluno para prévia")
        self.details = QPushButton("Ver lista da turma")
        self.details.clicked.connect(self.show_roster)
        layout.addWidget(self.summary)
        layout.addWidget(self.selector)
        layout.addWidget(self.details, alignment=Qt.AlignmentFlag.AlignLeft)
        self.set_students(())

    @property
    def selected(self) -> Student | None:
        index = self.selector.currentIndex()
        return self.students[index] if index >= 0 else None

    def set_students(self, students: tuple[Student, ...]) -> None:
        self.students = students
        ready = sum(student.ready for student in students)
        self.summary.setText(f"{len(students)} aluno(s) · {ready} apto(s) para exportar"
                             if students else "Cada subpasta representa um aluno.")
        with QSignalBlocker(self.selector):
            self.selector.clear()
            for student in students:
                state = " · revisar" if not student.ready else ""
                self.selector.addItem(f"{student.name} · {student.total} foto(s){state}")
            if students:
                first_ready = next((index for index, student in enumerate(students)
                                    if student.ready), 0)
                self.selector.setCurrentIndex(first_ready)
        self.selector.setVisible(bool(students))
        self.details.setVisible(bool(students))

    def show_roster(self) -> None:
        lines = []
        for student in self.students:
            line = f"{student.name} — {student.total - len(student.invalid)}/{student.total} foto(s) válidas"
            if student.issue:
                line += f"\n  {student.issue}"
            if student.invalid:
                line += "\n  Arquivos inválidos: " + ", ".join(student.invalid)
            lines.append(line)
        show_details(self, "Lista da turma", self.summary.text(), lines)


def show_details(parent, title: str, summary: str, lines: list[str]) -> None:
    dialog = QMessageBox(QMessageBox.Icon.Information, title, summary, parent=parent)
    dialog.setTextFormat(Qt.TextFormat.PlainText)
    dialog.setDetailedText("\n\n".join(lines))
    dialog.exec()


def show_batch_result(parent, summary: str, result: BatchResult) -> None:
    lines = [f"Gerado — {path}" for path in result.generated]
    lines.extend(f"Falha — {student.name}\n  {reason}" for student, reason in result.failed)
    lines.extend(f"Ignorado na validação — {student.name}" for student in result.skipped)
    lines.extend(f"Pendente após cancelamento — {student.name}" for student in result.pending)
    show_details(parent, "Resultado do lote", summary, lines)
