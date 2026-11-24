from PIL import Image
from pypdf import PdfReader

from okami_memorias import export
from okami_memorias.batch import export_class, scan_class
from okami_memorias.decoration import THEMES, compose_page
from okami_memorias.layouts import Mosaic
from okami_memorias.operation import Operation


def make_student(directory, name, count):
    folder = directory / name
    folder.mkdir()
    for index in range(count):
        with Image.new("RGB", (100 + index, 140), (index * 30, 80, 100)) as photo:
            photo.save(folder / f"{index}.png")
    return folder


def test_batch_exports_three_students_with_their_names_and_template(tmp_path):
    source = tmp_path / "turma"
    target = tmp_path / "pdfs"
    source.mkdir()
    target.mkdir()
    for name, count in (("Luísa", 5), ("Ana", 1), ("João", 4)):
        make_student(source, name, count)
    originals = {path: path.read_bytes() for path in source.rglob("*.png")}
    reported = []
    operation = Operation(lambda *args: reported.append(args))
    roster = scan_class(source, operation)
    assert [(student.name, student.total) for student in roster] == [
        ("Ana", 1), ("João", 4), ("Luísa", 5),
    ]
    layout = Mosaic(left=25)
    theme = THEMES[1]
    result = export_class(roster, target, operation, layout=layout, theme=theme,
                          student_titles=True)
    assert not (result.failed or result.skipped or result.pending)
    assert [entry[1:] for entry in reported if entry[0].startswith("Exportando")] == [
        (0, 3), (1, 3), (2, 3),
    ]
    factor = 72 / 25.4
    for pdf_path, images in zip(result.generated, ([1], [4], [4, 1])):
        pdf = PdfReader(pdf_path)
        assert [len(page.images) for page in pdf.pages] == images
        design = compose_page(layout, theme, pdf_path.stem)
        for page in pdf.pages:
            assert round(float(page.mediabox.width) / factor, 3) == 210
            assert round(float(page.mediabox.height) / factor, 3) == 297
            assert page.extract_text().strip() == pdf_path.stem
            fills = [values for values, cmd in page.get_contents().operations if cmd == b"re"]
            assert round(float(fills[1][0]) / factor, 3) == design.background[1].rect.x == 25
    assert {path: path.read_bytes() for path in source.rglob("*.png")} == originals


def test_batch_reports_empty_invalid_and_existing_output_and_continues(tmp_path):
    source = tmp_path / "turma"
    target = tmp_path / "pdfs"
    source.mkdir()
    target.mkdir()
    make_student(source, "A vazio", 0)
    invalid = make_student(source, "B inválido", 1)
    (invalid / "erro.jpg").write_bytes(b"invalid")
    make_student(source, "C existente", 1)
    make_student(source, "D apto", 1)
    existing = target / "C existente.pdf"
    existing.write_bytes(b"intacto")
    operation = Operation(lambda *_: None)
    roster = scan_class(source, operation)
    assert roster[0].total == 0 and roster[0].issue
    assert roster[1].invalid == ("erro.jpg",)
    result = export_class(roster, target, operation, title="Nossa turma")
    assert [student.name for student in result.skipped] == ["A vazio", "B inválido"]
    assert [student.name for student, _ in result.failed] == ["C existente"]
    assert existing.read_bytes() == b"intacto"
    assert [path.name for path in result.generated] == ["D apto.pdf"]
    assert PdfReader(result.generated[0]).pages[0].extract_text().strip() == "Nossa turma"


def test_batch_cancellation_keeps_completed_pdf_and_discards_current(tmp_path, monkeypatch):
    source = tmp_path / "turma"
    target = tmp_path / "pdfs"
    source.mkdir()
    target.mkdir()
    for name in ("A", "B", "C"):
        make_student(source, name, 1)
    operation = Operation(lambda *_: None)
    roster = scan_class(source, operation)
    render_pdf = export.render_pdf

    def render_and_cancel(stream, photos, design, photo_operation):
        render_pdf(stream, photos, design, photo_operation)
        if photos[0].parent.name == "B":
            operation.cancel()

    monkeypatch.setattr(export, "render_pdf", render_and_cancel)
    result = export_class(roster, target, operation)
    assert result.generated == (target / "A.pdf",)
    assert [document.pages for document in result.documents] == [1]
    assert [student.name for student in result.pending] == ["B", "C"]
    assert list(target.iterdir()) == [target / "A.pdf"]
    assert len(PdfReader(result.generated[0]).pages) == 1
