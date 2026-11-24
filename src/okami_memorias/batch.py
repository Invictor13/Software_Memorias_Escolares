"""Validação de turmas e exportação independente por aluno."""

from dataclasses import dataclass
from pathlib import Path

from .core import generate_album
from .decoration import WHITE, Theme, compose_page
from .errors import ExportError, OperationCancelled, PhotoError
from .imaging import discover, load_photo
from .layouts import Mosaic
from .operation import Operation


@dataclass(frozen=True)
class Student:
    directory: Path
    total: int
    invalid: tuple[str, ...] = ()
    issue: str = ""

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def ready(self) -> bool:
        return self.total > 0 and not self.invalid and not self.issue


@dataclass(frozen=True)
class BatchResult:
    generated: tuple[Path, ...]
    failed: tuple[tuple[Student, str], ...]
    skipped: tuple[Student, ...]
    pending: tuple[Student, ...] = ()


def scan_class(directory: Path, operation: Operation) -> tuple[Student, ...]:
    try:
        root = directory.resolve()
        folders = sorted(
            (path for path in directory.iterdir() if path.is_dir() and not path.is_symlink()
             and not getattr(path, "is_junction", lambda: False)()
             and path.resolve().parent == root),
            key=lambda path: (path.name.casefold(), path.name),
        )
    except (OSError, RuntimeError) as exc:
        raise PhotoError(f"Não foi possível ler a pasta da turma: {exc}") from exc
    if not folders:
        raise PhotoError("A pasta da turma deve ter pelo menos uma subpasta de aluno.")
    students = []
    for index, folder in enumerate(folders, start=1):
        operation.progress(f"Verificando aluno {index} de {len(folders)}", index - 1, len(folders))
        try:
            paths = discover(folder)
        except PhotoError as exc:
            students.append(Student(folder, 0, issue=str(exc)))
            continue
        invalid = []
        for path in paths:
            operation.checkpoint()
            try:
                load_photo(path).close()
            except PhotoError:
                invalid.append(path.name)
        students.append(Student(folder, len(paths), tuple(invalid)))
    operation.checkpoint()
    return tuple(students)


def export_class(students: tuple[Student, ...], destination: Path, operation: Operation,
                 *, layout: Mosaic = Mosaic(), theme: Theme = WHITE, title: str = "",
                 student_titles: bool = False) -> BatchResult:
    if not destination.is_dir():
        raise ExportError("Selecione uma pasta de destino existente para os PDFs da turma.")
    compose_page(layout, theme, "" if student_titles else title)
    ready = tuple(student for student in students if student.ready)
    skipped = tuple(student for student in students if not student.ready)
    generated = []
    failed = []
    photo_operation = operation.without_progress()
    for index, student in enumerate(ready):
        target = destination / f"{student.name}.pdf"
        try:
            operation.progress(f"Exportando aluno {index + 1} de {len(ready)}", index, len(ready))
            generate_album(student.directory, target, layout, operation=photo_operation,
                           theme=theme, title=student.name if student_titles else title)
        except OperationCancelled:
            return BatchResult(tuple(generated), tuple(failed), skipped, ready[index:])
        except (ExportError, PhotoError, ValueError) as exc:
            failed.append((student, str(exc)))
        else:
            generated.append(target)
    return BatchResult(tuple(generated), tuple(failed), skipped)
