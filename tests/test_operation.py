from PIL import Image
import pytest

from okami_memorias.core import generate_album
from okami_memorias.errors import OperationCancelled
from okami_memorias.operation import Operation


@pytest.mark.parametrize("cancel_phase", ["Validando fotos", "Montando páginas", "Salvando PDF"])
def test_export_cancels_without_publishing(tmp_path, cancel_phase):
    photos = tmp_path / "fotos"
    photos.mkdir()
    original = photos / "foto.png"
    with Image.new("RGB", (80, 120), "teal") as image:
        image.save(original)
    before = original.read_bytes()
    destination = tmp_path / "album.pdf"

    def report(phase, completed, total):
        if phase == cancel_phase:
            operation.cancel()

    operation = Operation(report)
    with pytest.raises(OperationCancelled):
        generate_album(photos, destination, operation=operation)
    assert original.read_bytes() == before
    assert not destination.exists()
    assert not list(tmp_path.glob(".okami-*.tmp"))
