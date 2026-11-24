from PIL import Image
from pypdf import PdfReader
import pytest
from reportlab.lib.colors import HexColor

from okami_memorias.core import generate_album
from okami_memorias.decoration import THEMES, WHITE, compose_page
from okami_memorias.layouts import A4_HEIGHT, A4_WIDTH, Mosaic, Rect


def test_white_keeps_p1_geometry():
    layout = Mosaic(left=25)
    design = compose_page(layout, WHITE, "  ")
    assert design.slots == layout.slots()
    assert design.heading is None
    assert len(design.fills(4)) == 1
    assert design.background[0].rect == Rect(0, 0, 210, 297)


def test_white_supports_optional_heading():
    layout = Mosaic(left=25)
    design = compose_page(layout, WHITE, "Memórias")
    assert design.heading.text == "Memórias"
    assert design.slots[0].x == 25
    assert design.slots[0].height < layout.slots()[0].height
    assert len(design.fills(4)) == 1


@pytest.mark.parametrize("theme", THEMES[1:], ids=lambda theme: theme.name)
def test_decorated_pdf_matches_scene_and_preserves_originals(tmp_path, theme):
    layout = Mosaic(left=25, right=15, top=12, bottom=14)
    title = "Memórias da turma · 5º ano"
    design = compose_page(layout, theme, title)
    for fill in design.fills(4)[1:]:
        rect = fill.rect
        assert rect.x >= 25
        assert rect.y >= 14
        assert rect.x + rect.width <= A4_WIDTH - 15
        assert rect.y + rect.height <= A4_HEIGHT - 12

    source = tmp_path / "fotos"
    source.mkdir()
    sizes = [(90, 180), (180, 90), (100, 100), (200, 100), (100, 200)]
    for index, size in enumerate(sizes):
        with Image.new("RGB", size, (30 * index, 100, 160)) as photo:
            photo.save(source / f"{index}.png")
    original = {path: path.read_bytes() for path in source.iterdir()}
    destination = tmp_path / "album.pdf"
    assert generate_album(source, destination, layout, theme=theme, title=title) == 5
    pdf = PdfReader(destination)
    assert len(pdf.pages) == 2
    points_per_mm = 72 / 25.4
    for page, page_sizes in zip(pdf.pages, (sizes[:4], sizes[4:])):
        assert float(page.mediabox.width) == pytest.approx(210 * points_per_mm, abs=0.001)
        assert float(page.mediabox.height) == pytest.approx(297 * points_per_mm, abs=0.001)
        assert page.extract_text().strip() == title
        actions = page.get_contents().operations
        rectangles = [values for values, cmd in actions if cmd == b"re"]
        colors = [values for values, cmd in actions if cmd == b"rg"]
        fills = design.fills(len(page_sizes))
        assert len(rectangles) == len(fills)
        for values, color, fill in zip(rectangles, colors, fills):
            rect = fill.rect
            assert values == pytest.approx(
                [v * points_per_mm for v in (rect.x, rect.y, rect.width, rect.height)],
                abs=0.001,
            )
            assert color == pytest.approx(HexColor(fill.color).rgb(), abs=0.00001)
        images = [actions[i - 1][0] for i, (_, cmd) in enumerate(actions) if cmd == b"Do"]
        assert len(images) == len(page_sizes)
        for actual, slot, size in zip(images, design.slots, page_sizes):
            area = slot.contain(*size)
            assert actual == pytest.approx(
                [area.width * points_per_mm, 0, 0, area.height * points_per_mm,
                 area.x * points_per_mm, area.y * points_per_mm], abs=0.001,
            )
    assert {path: path.read_bytes() for path in source.iterdir()} == original


@pytest.mark.parametrize(("layout", "title", "message"), [
    (Mosaic(top=275), "", "pouco espaço"),
    (Mosaic(left=160), "Memórias da turma de educação infantil", "Reduza o título"),
    (Mosaic(), "Turma 🐺", "não suporta"),
])
def test_decorated_layout_validation(layout, title, message):
    with pytest.raises(ValueError, match=message):
        compose_page(layout, THEMES[1], title)
