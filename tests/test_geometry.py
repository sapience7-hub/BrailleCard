import pytest
from PIL import Image, ImageDraw

from braille_card import spec
from braille_card.geometry import Mesh, build_combined_mesh, source_tactile_cells
from braille_card.braille import wrap_source


def test_spherical_cap_has_exact_ada_base_and_height() -> None:
    mesh = Mesh()
    mesh.add_spherical_cap(
        10.0,
        20.0,
        2.0,
        spec.BRAILLE_DOT_DIAMETER,
        spec.BRAILLE_DOT_HEIGHT,
    )
    x0, _, z0, x1, _, z1 = mesh.bounds()
    assert x1 - x0 == pytest.approx(1.55, abs=1e-9)
    assert z1 - z0 == pytest.approx(0.75, abs=1e-9)


def test_combined_geometry_is_one_boolean_solid() -> None:
    mesh, metadata = build_combined_mesh(
        wrap_source("With love", spec.MAX_BRAILLE_CELLS_PER_LINE),
        wrap_source("You make every day bright.", spec.MAX_BRAILLE_CELLS_PER_LINE),
    )
    assert len(mesh.vertices) > 10_000
    assert len(mesh.triangles) > 20_000
    assert metadata["braille"]["front_dot_count"] > 0
    assert metadata["braille"]["back_dot_count"] > 0
    assert mesh.bounds()[2] == pytest.approx(-0.75)
    assert mesh.bounds()[5] == pytest.approx(2.8)


def test_source_artwork_controls_tactile_geometry(tmp_path) -> None:
    white = tmp_path / "white.png"
    artwork = tmp_path / "artwork.png"
    Image.new("L", (1200, 1200), 255).save(white)
    image = Image.new("L", (1200, 1200), 255)
    ImageDraw.Draw(image).rectangle((450, 450, 750, 750), fill=0)
    image.save(artwork)

    white_cells, white_grid = source_tactile_cells(white)
    source_cells, source_grid = source_tactile_cells(artwork)
    assert white_cells == []
    assert white_grid["retained_cell_count"] == 0
    assert source_grid["retained_cell_count"] > 0
    assert source_grid["isolated_cells_removed"] == 0

    mesh, metadata = build_combined_mesh(
        wrap_source("With love", spec.MAX_BRAILLE_CELLS_PER_LINE),
        wrap_source("You make every day bright.", spec.MAX_BRAILLE_CELLS_PER_LINE),
        normalized_image=artwork,
    )
    assert metadata["tactile"]["mode"] == "source-derived tactile grid"
    assert metadata["tactile"]["source_grid"] == source_grid
    assert mesh.bounds()[5] == pytest.approx(2.8)

    _, legacy = build_combined_mesh(
        wrap_source("With love", spec.MAX_BRAILLE_CELLS_PER_LINE),
        wrap_source("You make every day bright.", spec.MAX_BRAILLE_CELLS_PER_LINE),
    )
    assert legacy["tactile"]["mode"] == "reference silhouette"
