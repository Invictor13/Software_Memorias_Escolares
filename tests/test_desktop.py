import os
from threading import Event
from time import monotonic, sleep

from PIL import Image
from pypdf import PdfReader
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QFileDialog

from okami_memorias.desktop import window as desktop
from okami_memorias.desktop.window import MainWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app):
    widget = MainWindow()
    widget.show()
    app.processEvents()
    yield widget
    wait_for_job(widget)
    widget.close()
    widget.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def wait_until(condition):
    deadline = monotonic() + 5
    while not condition() and monotonic() < deadline:
        QApplication.processEvents()
        sleep(0.01)
    assert condition()


def wait_for_job(window):
    wait_until(lambda: window.job is None)


@pytest.mark.parametrize("theme_index", [0, 2])
def test_desktop_previews_and_exports(tmp_path, window, monkeypatch, theme_index):
    photos = tmp_path / "fotos"
    photos.mkdir()
    for index in range(5):
        with Image.new("RGB", (150 + index, 300 - 20 * index), (index * 40, 80, 120)) as image:
            image.save(photos / f"{index}.png")
    originals = {path: path.read_bytes() for path in photos.iterdir()}
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *_: str(photos))
    window.choose_source.click()
    wait_for_job(window)
    assert "Válidas: 5" in window.summary.text()
    assert window.page_label.text() == "Prévia da página 1 de 2"
    assert len(window.preview.photos) == 4

    destination = tmp_path / "album.pdf"
    monkeypatch.setattr(QFileDialog, "exec", lambda self: 1)
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(destination)])
    window.choose_target.click()
    window.margins["left"].setValue(297)
    assert not window.export.isEnabled()
    window.margins["left"].setValue(25)
    assert window.preview.slots[0].x == 25
    window.theme.setCurrentIndex(theme_index)
    if theme_index:
        window.album_title.setText("Memórias da turma")
        assert window.preview.design.heading.text == "Memórias da turma"
        assert window.preview.slots[0].x > 25
    assert window.export.isEnabled()
    window.export.click()
    wait_for_job(window)

    pdf = PdfReader(destination)
    assert [len(page.images) for page in pdf.pages] == [4, 1]
    if theme_index:
        assert all(page.extract_text().strip() == "Memórias da turma" for page in pdf.pages)
    assert float(pdf.pages[0].mediabox.width) * 25.4 / 72 == pytest.approx(210, abs=0.001)
    assert float(pdf.pages[0].mediabox.height) * 25.4 / 72 == pytest.approx(297, abs=0.001)
    actions = pdf.pages[0].get_contents().operations
    first_image = next(index for index, (_, cmd) in enumerate(actions) if cmd == b"Do")
    fit = window.preview.slots[0].contain(*window.preview.photos[0].size)
    assert float(actions[first_image - 1][0][4]) * 25.4 / 72 == pytest.approx(fit.x, abs=0.001)
    assert {path: path.read_bytes() for path in photos.iterdir()} == originals


def test_desktop_lists_invalid_files_and_blocks_export(tmp_path, window):
    (tmp_path / "a.png").write_bytes(b"invalid")
    (tmp_path / "b.jpg").write_bytes(b"invalid")
    window.load_folder(tmp_path)
    wait_for_job(window)
    window.set_destination(tmp_path / "album.pdf")
    assert window.scan.invalid == ("a.png", "b.jpg")
    assert window.issues.isVisible()
    assert not window.export.isEnabled()


def test_desktop_cancel_button_signals_worker(tmp_path, window, monkeypatch):
    with Image.new("RGB", (80, 120), "teal") as image:
        image.save(tmp_path / "foto.png")
    window.load_folder(tmp_path)
    wait_for_job(window)
    window.set_destination(tmp_path / "album.pdf")
    resume = Event()

    def export_with_pause(directory, destination, layout, *, operation, theme, title):
        operation.progress("Montando páginas", 1, 2)
        if not resume.wait(timeout=5):
            raise AssertionError("A janela não respondeu")
        operation.checkpoint()

    monkeypatch.setattr(desktop, "generate_album", export_with_pause)
    window.export.click()
    try:
        wait_until(lambda: window.progress.value() == 1)
        assert not window.export.isEnabled()
        window.cancel.click()
    finally:
        resume.set()
    wait_for_job(window)
    assert window.status.text() == "Operação cancelada."
    assert window.export.isEnabled()
    assert not window.destination.exists()


def test_desktop_class_mode_previews_students_and_exports_batch(tmp_path, window, monkeypatch):
    classroom = tmp_path / "turma"
    target = tmp_path / "pdfs"
    target.mkdir()
    for name, count in (("Alice", 1), ("Bruno", 4), ("Cecília", 5)):
        folder = classroom / name
        folder.mkdir(parents=True)
        for index in range(count):
            with Image.new("RGB", (80, 120 + index), (index * 40, 80, 100)) as photo:
                photo.save(folder / f"{index}.png")
    (classroom / "Sem fotos").mkdir()
    paths = iter((str(classroom), str(target)))
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *_: next(paths))

    window.mode.setCurrentIndex(1)
    window.choose_source.click()
    wait_for_job(window)
    assert "4 aluno(s) · 3 apto(s)" in window.class_panel.summary.text()
    assert len(window.preview.photos) == 1
    window.class_panel.selector.setCurrentIndex(2)
    wait_for_job(window)
    assert len(window.preview.photos) == 4
    assert "1 de 2 · Cecília" in window.page_label.text()
    window.use_student_title.setChecked(True)
    window.margins["left"].setValue(25)
    window.theme.setCurrentIndex(2)
    assert window.preview.design.heading.text == "Cecília"
    window.choose_target.click()
    assert window.export.isEnabled()
    window.export.click()
    wait_for_job(window)
    assert window.result_button.isVisible()
    assert len(window.batch_result.skipped) == 1
    assert len(window.batch_result.generated) == 3
    expected = [1, 1, 2]
    for path, pages in zip(window.batch_result.generated, expected):
        pdf = PdfReader(path)
        assert len(pdf.pages) == pages
        assert pdf.pages[0].extract_text().strip() == path.stem
