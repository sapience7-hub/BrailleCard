import pytest

from braille_card import spec
from braille_card.geometry import Mesh, build_combined_mesh
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
        wrap_source("With love", 16),
        wrap_source("You make every day bright.", 16),
    )
    assert len(mesh.vertices) > 10_000
    assert len(mesh.triangles) > 20_000
    assert metadata["braille"]["front_dot_count"] > 0
    assert metadata["braille"]["back_dot_count"] > 0
    assert mesh.bounds()[2] == pytest.approx(-0.75)
    assert mesh.bounds()[5] == pytest.approx(2.8)

