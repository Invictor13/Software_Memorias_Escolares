import pytest

from okami_memorias.layouts import A4_HEIGHT, A4_WIDTH, Mosaic, Rect


def test_margins_spacing_and_order():
    top_left, top_right, bottom_left, bottom_right = Mosaic(
        left=22, right=12, top=8, bottom=14, gap=6
    ).slots()
    assert top_left.x == bottom_left.x == 22
    assert bottom_left.y == bottom_right.y == 14
    assert top_left.y + top_left.height == A4_HEIGHT - 8
    assert top_right.x + top_right.width == A4_WIDTH - 12
    assert top_right.x - (top_left.x + top_left.width) == 6
    assert top_left.y - (bottom_left.y + bottom_left.height) == 6
    assert {(r.width, r.height) for r in (top_left, top_right, bottom_left, bottom_right)} == {
        (85, 134.5)
    }


@pytest.mark.parametrize(("size", "expected"), [
    ((200, 100), Rect(10, 45, 80, 40)),
    ((50, 100), Rect(27.5, 20, 45, 90)),
    ((100, 100), Rect(10, 25, 80, 80)),
])
def test_contain(size, expected):
    assert Rect(10, 20, 80, 90).contain(*size) == expected


@pytest.mark.parametrize("layout", [
    Mosaic(left=-1), Mosaic(gap=float("nan")), Mosaic(top=290), Mosaic(right=190)
])
def test_invalid_margins(layout):
    with pytest.raises(ValueError):
        layout.slots()
