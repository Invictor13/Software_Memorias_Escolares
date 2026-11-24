from PIL import Image
from pypdf import PdfReader
import pytest

from okami_memorias import export
from okami_memorias.__main__ import main
from okami_memorias.core import generate_album
from okami_memorias.errors import ExportError, PhotoError
from okami_memorias.layouts import Mosaic


@pytest.fixture
def photos(tmp_path):
    directory = tmp_path / "fotos"
    directory.mkdir()
    return directory


def make_photos(directory, count):
    sizes = [(2400, 1200), (80, 180), (150, 150), (180, 120), (70, 130)]
    for number in reversed(range(count)):
        with Image.new("RGB", sizes[number], (30 * number, 90, 180)) as image:
            image.save(directory / f"{number}.png")
    return {p: p.read_bytes() for p in directory.iterdir()}


@pytest.mark.parametrize(("count", "per_page"), [(1, [1]), (4, [4]), (5, [4, 1])])
def test_pdf_geometry_pagination_and_originals(photos, tmp_path, count, per_page):
    originals = make_photos(photos, count)
    destination = tmp_path / "album.pdf"
    layout = Mosaic(left=25, right=15, top=12, bottom=14, gap=4)
    assert generate_album(photos, destination, layout) == count
    pdf = PdfReader(destination)
    assert pdf.metadata.title == "Álbum de fotografias"
    assert len(pdf.pages) == len(per_page)
    sizes = [(2400, 1200), (80, 180), (150, 150), (180, 120), (70, 130)]
    points_per_mm = 72 / 25.4
    for page_number, (page, expected_count) in enumerate(zip(pdf.pages, per_page)):
        assert float(page.mediabox.width) == pytest.approx(210 * points_per_mm, abs=0.001)
        assert float(page.mediabox.height) == pytest.approx(297 * points_per_mm, abs=0.001)
        operations = page.get_contents().operations
        assert [float(v) for v in next(values for values, op in operations if op == b"rg")] == [1, 1, 1]
        transforms = [
            [float(v) for v in operations[index - 1][0]]
            for index, (_, operator) in enumerate(operations) if operator == b"Do"
        ]
        assert len(transforms) == expected_count
        for index, transform in enumerate(transforms):
            fit = layout.slots()[index].contain(*sizes[4 * page_number + index])
            assert transform == pytest.approx(
                [fit.width * points_per_mm, 0, 0, fit.height * points_per_mm,
                 fit.x * points_per_mm, fit.y * points_per_mm], abs=0.001
            )
    first_page = pdf.pages[0]
    first_image_name = next(
        values[0] for values, op in first_page.get_contents().operations if op == b"Do"
    )
    first_image = first_page["/Resources"]["/XObject"][first_image_name]
    assert first_image["/Width"] == pytest.approx(layout.slots()[0].width * 300 / 25.4, abs=1)
    assert {path: path.read_bytes() for path in photos.iterdir()} == originals


def test_deterministic_export(photos, tmp_path):
    make_photos(photos, 5)
    first, second = tmp_path / "a.pdf", tmp_path / "b.pdf"
    generate_album(photos, first)
    generate_album(photos, second)
    assert first.read_bytes() == second.read_bytes()


def test_corrupt_photo_fails_before_render(photos, tmp_path, monkeypatch):
    make_photos(photos, 1)
    (photos / "corrompida.jpg").write_bytes(b"invalid")
    destination = tmp_path / "album.pdf"

    def unexpected_render(*args):
        pytest.fail("A renderização começou antes do fim da validação")

    monkeypatch.setattr(export, "render_pdf", unexpected_render)
    with pytest.raises(PhotoError):
        generate_album(photos, destination)
    assert not destination.exists()


def test_existing_destination_is_preserved(photos, tmp_path):
    make_photos(photos, 1)
    destination = tmp_path / "album.pdf"
    destination.write_bytes(b"original")
    with pytest.raises(ExportError, match="já existe"):
        generate_album(photos, destination)
    assert destination.read_bytes() == b"original"


@pytest.mark.parametrize("failure", [OSError("Falha simulada"), KeyboardInterrupt()])
def test_partial_export_is_removed(photos, tmp_path, monkeypatch, failure):
    make_photos(photos, 1)
    destination = tmp_path / "album.pdf"

    def partial_render(stream, *_):
        stream.write(b"parcial")
        raise failure

    monkeypatch.setattr(export, "render_pdf", partial_render)
    with pytest.raises(ExportError if isinstance(failure, OSError) else KeyboardInterrupt):
        generate_album(photos, destination)
    assert sorted(tmp_path.iterdir()) == [photos]


def test_missing_destination_parent(photos, tmp_path):
    make_photos(photos, 1)
    with pytest.raises(ExportError):
        generate_album(photos, tmp_path / "inexistente" / "album.pdf")


def test_destination_created_during_export_is_preserved(photos, tmp_path, monkeypatch):
    make_photos(photos, 1)
    destination = tmp_path / "album.pdf"

    def render_while_another_process_publishes(stream, *_):
        stream.write(b"preparado")
        destination.write_bytes(b"concorrente")

    monkeypatch.setattr(export, "render_pdf", render_while_another_process_publishes)
    with pytest.raises(ExportError):
        generate_album(photos, destination)
    assert destination.read_bytes() == b"concorrente"
    assert not list(tmp_path.glob(".okami-*.tmp"))


def test_cli(photos, tmp_path, capsys):
    destination = tmp_path / "album.pdf"
    arguments = ["--input", str(photos), "--output", str(destination)]
    assert main(arguments) == 1
    assert "Nenhuma fotografia" in capsys.readouterr().err
    make_photos(photos, 1)
    assert main(arguments + ["--binding-margin-mm", "23"]) == 0
    assert destination.exists()
