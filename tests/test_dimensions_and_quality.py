from braille_card import spec
from braille_card.quality import assert_checks_pass, run_flat_card_checks, tactile_is_connected


def test_exact_2010_ada_ranges_from_product_spec() -> None:
    # Exact ranges required by docs/PRODUCT_GOAL.md; this test deliberately
    # names every independently constrained dimension.
    assert 1.5 <= spec.BRAILLE_DOT_DIAMETER <= 1.6
    assert 2.3 <= spec.BRAILLE_DOT_SPACING <= 2.5
    assert 6.1 <= spec.BRAILLE_CELL_SPACING <= 7.6
    assert 10.0 <= spec.BRAILLE_LINE_SPACING <= 10.2
    assert 0.6 <= spec.BRAILLE_DOT_HEIGHT <= 0.9


def test_all_applicable_flat_card_machine_gates() -> None:
    checks = run_flat_card_checks()
    assert_checks_pass(checks)
    assert set(checks) == {
        "safe_margins",
        "braille_artwork_collision",
        "braille_dimensional_baseline",
        "minimum_feature_size",
        "no_isolated_tactile_fragments",
        "no_unsafe_sharp_peaks",
        "panel_thickness",
        "sv07_build_area_fit",
    }
    assert tactile_is_connected()

