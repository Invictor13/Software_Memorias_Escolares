from PIL import Image
import pytest

from okami_memorias.errors import PhotoError
from okami_memorias.imaging import discover, load_photo


def test_discovery_order_and_supported_extensions(tmp_path):
    for name in ("c.png", "B.JPEG", "a.jpg", "readme.txt"):
        (tmp_path / name).touch()
    (tmp_path / "subpasta.jpg").mkdir()
    assert [path.name for path in discover(tmp_path)] == ["a.jpg", "B.JPEG", "c.png"]


def test_exif_rotation(tmp_path):
    path = tmp_path / "rotacionada.jpg"
    with Image.new("RGB", (80, 40), "blue") as source:
        source.paste("red", (0, 0, 40, 40))
        exif = source.getexif()
        exif[274] = 6
        source.save(path, exif=exif)
    with load_photo(path) as photo:
        assert photo.size == (40, 80)
        assert photo.getpixel((20, 10))[0] > 200
        assert photo.getpixel((20, 70))[2] > 200


def test_png_transparency_has_white_background(tmp_path):
    path = tmp_path / "transparente.png"
    with Image.new("RGBA", (20, 40), (255, 0, 0, 0)) as source:
        source.save(path)
    with load_photo(path) as photo:
        assert photo.mode == "RGB"
        assert photo.getpixel((0, 0)) == (255, 255, 255)


@pytest.mark.parametrize("contents", [b"corrompido", b""])
def test_invalid_photo(tmp_path, contents):
    path = tmp_path / "invalida.jpg"
    path.write_bytes(contents)
    with pytest.raises(PhotoError, match="invalida.jpg"):
        load_photo(path)


def test_empty_directory(tmp_path):
    with pytest.raises(PhotoError, match="Nenhuma fotografia"):
        discover(tmp_path)
