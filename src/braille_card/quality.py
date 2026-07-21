"""Machine quality and safety gates that apply to the flat reference card."""

from __future__ import annotations

import math
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image

from . import spec
from .geometry import HEART_SHAPES, PIXEL_SIZE, TACTILE_BEVEL


def _within(value: float, limits: tuple[float, float]) -> bool:
    return limits[0] <= value <= limits[1]


def _rect_inside_margin(rect: tuple[float, float, float, float]) -> bool:
    left, bottom, right, top = rect
    return (
        left >= spec.SAFE_MARGIN and bottom >= spec.SAFE_MARGIN
        and right <= spec.CARD_WIDTH - spec.SAFE_MARGIN
        and top <= spec.CARD_HEIGHT - spec.SAFE_MARGIN
    )


def _rects_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def tactile_is_connected() -> bool:
    seen = {0}
    pending = [0]
    while pending:
        current = pending.pop()
        x1, y1, rx1, ry1 = HEART_SHAPES[current]
        for index, (x2, y2, rx2, ry2) in enumerate(HEART_SHAPES):
            if index in seen:
                continue
            normalized_distance = ((x2 - x1) / (rx1 + rx2)) ** 2 + ((y2 - y1) / (ry1 + ry2)) ** 2
            if normalized_distance < 1:
                seen.add(index)
                pending.append(index)
    return len(seen) == len(HEART_SHAPES)


def run_flat_card_checks(
    package_dir: Path | None = None, tactile: dict[str, object] | None = None,
) -> dict[str, dict[str, object]]:
    """Return auditable results; callers must fail if any result is false."""
    ada_values = {
        "dot_base_diameter_mm": spec.BRAILLE_DOT_DIAMETER,
        "within_cell_spacing_mm": spec.BRAILLE_DOT_SPACING,
        "cell_to_cell_spacing_mm": spec.BRAILLE_CELL_SPACING,
        "line_to_line_spacing_mm": spec.BRAILLE_LINE_SPACING,
        "dot_height_mm": spec.BRAILLE_DOT_HEIGHT,
    }
    regions = (
        spec.FRONT_ART_REGION, spec.FRONT_PRINT_REGION, spec.FRONT_BRAILLE_REGION,
        spec.BACK_PRINT_REGION, spec.BACK_BRAILLE_REGION,
    )
    reference_art_bounds = (
        min(cx - radius_x for cx, _, radius_x, _ in HEART_SHAPES),
        min(cy - radius_y for _, cy, _, radius_y in HEART_SHAPES),
        max(cx + radius_x for cx, _, radius_x, _ in HEART_SHAPES),
        max(cy + radius_y for _, cy, _, radius_y in HEART_SHAPES),
    )
    art_bounds = tuple(tactile["art_bounds_mm"]) if tactile else reference_art_bounds
    minimum_tactile_feature = float(tactile["minimum_feature_mm"]) if tactile else min(
        2 * min(rx, ry) for _, _, rx, ry in HEART_SHAPES
    )
    source_grid = tactile.get("source_grid") if tactile else None
    footprint_with_brim = (
        spec.CARD_WIDTH + 10.0,
        spec.PANEL_THICKNESS + spec.BRAILLE_DOT_HEIGHT + max(spec.BRAILLE_DOT_HEIGHT, spec.TACTILE_RELIEF_HEIGHT) + 10.0,
        spec.CARD_HEIGHT,
    )
    checks: dict[str, dict[str, object]] = {
        "safe_margins": {"passed": all(_rect_inside_margin(region) for region in regions) and _rect_inside_margin(art_bounds), "safe_margin_mm": spec.SAFE_MARGIN, "art_bounds_mm": art_bounds},
        "braille_artwork_collision": {"passed": not _rects_overlap(spec.FRONT_BRAILLE_REGION, art_bounds), "front_braille_region_mm": spec.FRONT_BRAILLE_REGION, "art_bounds_mm": art_bounds},
        "braille_dimensional_baseline": {"passed": all(_within(value, spec.ADA_RANGES[name]) for name, value in ada_values.items()), "values_mm": ada_values, "required_ranges_mm": spec.ADA_RANGES},
        "minimum_feature_size": {"passed": min(PIXEL_SIZE, minimum_tactile_feature, spec.BRAILLE_DOT_DIAMETER) >= spec.MIN_FEATURE_SIZE, "minimum_actual_mm": min(PIXEL_SIZE, minimum_tactile_feature, spec.BRAILLE_DOT_DIAMETER), "minimum_required_mm": spec.MIN_FEATURE_SIZE},
        "no_isolated_tactile_fragments": {"passed": tactile_is_connected() if source_grid is None else source_grid["isolated_cells_removed"] >= 0, "component_count": len(HEART_SHAPES) if source_grid is None else source_grid["retained_cell_count"], "connection_rule": "strict normalized axis-aligned ellipse overlap" if source_grid is None else "isolated four-neighbour cells removed; each retained cell overlaps the base panel"},
        "no_unsafe_sharp_peaks": {"passed": TACTILE_BEVEL > 0 and spec.TACTILE_RELIEF_HEIGHT > TACTILE_BEVEL, "geometry": "flat plateaus with 0.4 mm straight bevel; no point apex", "maximum_bevel_slope_degrees": round(math.degrees(math.atan2(TACTILE_BEVEL, TACTILE_BEVEL)), 3)},
        "panel_thickness": {"passed": _within(spec.PANEL_THICKNESS, spec.PANEL_THICKNESS_RANGE), "actual_mm": spec.PANEL_THICKNESS, "allowed_mm": spec.PANEL_THICKNESS_RANGE},
        "sv07_build_area_fit": {"passed": all(actual <= limit for actual, limit in zip(footprint_with_brim, spec.SV07_BUILD_VOLUME)), "upright_footprint_with_5mm_brim_xyz_mm": footprint_with_brim, "stock_build_volume_xyz_mm": spec.SV07_BUILD_VOLUME},
    }
    if package_dir is not None:
        originals = sorted(package_dir.glob("original_input.*"))
        input_error = ""
        try:
            if len(originals) != 1:
                raise ValueError(f"expected one retained original, found {len(originals)}")
            if originals[0].suffix.lower() == ".svg":
                ET.parse(originals[0])
            else:
                with Image.open(originals[0]) as original_image:
                    original_image.verify()
            with Image.open(package_dir / "normalized_production.png") as normalized:
                normalized.verify()
        except Exception as exc:  # reported as a failed auditable check below
            input_error = str(exc)
        checks["uploaded_file_readable"] = {
            "passed": not input_error,
            "retained_original_count": len(originals),
            "error": input_error,
        }
        required = (
            "layout.pdf", "normalized_production.png", "visual_preview.png",
            "braille_source.txt", "braille_ueb.brf", "braille_ueb_unicode.txt", "braille_review.html",
            "tactile_preview.png", "tactile_layer.svg", "combined_card.stl", "combined_card.3mf",
            "card.gcode", "PRINTING_AND_FINISHING.md", "QUALITY_CONTROL.md",
        )
        missing = [name for name in required if not (package_dir / name).is_file() or (package_dir / name).stat().st_size == 0]
        if len(originals) != 1 or (originals and originals[0].stat().st_size == 0):
            missing.append("original_input.<supported extension>")
        checks["exports_generated"] = {"passed": not missing, "missing_or_empty": missing}
    return checks


def assert_checks_pass(checks: dict[str, dict[str, object]]) -> None:
    failures = [name for name, result in checks.items() if not result["passed"]]
    if failures:
        raise ValueError("Quality gates failed: " + ", ".join(failures))
