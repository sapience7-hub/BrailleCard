"""End-to-end production-package orchestration."""

from __future__ import annotations

import importlib.metadata
import json
import platform
from pathlib import Path

import PIL
import louis
import reportlab

from . import __version__, spec
from .braille import REVIEW_STATUS, translate, wrap_source
from .documents import (
    create_layout_pdf,
    create_visual_preview,
    write_braille_artifacts,
)
from .geometry import write_geometry_outputs
from .images import normalize_image
from .quality import assert_checks_pass, run_flat_card_checks
from .slicer import APPIMAGE_SHA256, PROFILE_HASHES, sha256_file, slice_card


def _write_operator_documents(package_dir: Path) -> None:
    printing = """# Printing and finishing guide

Status: **machine-generated candidate; not test-printed or operator-approved**.

This package targets one upright, long-edge-on-bed, single-piece 127.0 × 177.8
mm PLA card. `card.gcode` was generated offline for the stock OrcaSlicer 2.4.2
Sovol SV07 0.4 mm machine, Sovol SV07 PLA, and 0.20 mm process profiles, with
tree(auto) snug supports and a 5 mm brim. The stock PLA temperatures resolved to
235 °C first-layer / 200 °C normal nozzle and 65 °C bed. No print was submitted.

Operator steps (all remain human actions):

1. Inspect `card.gcode`, layer preview, profile name, temperatures, 220 × 220 ×
   250 mm build limits, upright orientation, support contacts, and brim in a
   trusted local G-code viewer before using it.
2. Confirm the installed nozzle is 0.4 mm, filament is known PLA, the bed is
   clean, and the machine is mechanically ready. Do not print unattended.
3. Run one calibration/test print using the operator's established safe loading
   procedure. Stop for collisions, poor adhesion, excessive vibration, or other
   abnormal behavior.
4. Let the card cool before removal. Remove the brim and supports slowly with
   eye protection, keeping tools away from Braille dots.
5. Deburr and round only the card perimeter. Do not sand, melt, coat, or reshape
   Braille dots before they have been dimensionally inspected.
6. Complete every unchecked item in `QUALITY_CONTROL.md`. A qualified Braille
   reader and tactile-graphics testers must evaluate the physical result.

If supports merge dots, the upright card is unstable, the physical dimensions
fall outside the specified ranges, or any edge remains sharp, do not treat this
package as approved; revise and regenerate after human calibration.
"""
    quality = """# Quality-control checklist

Machine checks in `checks.json` passed, but every item below requires a person
and remains deliberately unchecked.

## Before printing

- [ ] User approves the heart crop, front greeting, and back message.
- [ ] Source print text and UEB transcription are proofread side by side.
- [ ] A qualified Braille reviewer approves the transcription and layout.
- [ ] Operator previews the complete G-code and confirms the intended SV07,
      PLA, 0.4 mm nozzle, 0.20 mm layers, upright orientation, supports, brim,
      temperatures, and bed fit.
- [ ] Operator confirms the printer and work area are safe and ready.

## Test print and finishing

- [ ] Operator performs the first physical SV07 test print; no job has been
      submitted or started by this generator.
- [ ] Card finishes at 127.0 × 177.8 mm and fits an A7 envelope without forcing.
- [ ] Base panel is 1.8–2.2 mm thick away from relief.
- [ ] Braille dot base diameter is 1.5–1.6 mm and height is 0.6–0.9 mm.
- [ ] Within-cell, cell-to-cell, and line-to-line spacing meet the documented
      2.3–2.5 mm, 6.1–7.6 mm, and 10.0–10.2 mm ranges.
- [ ] No Braille dots are merged, missing, flattened, loose, or support-damaged.
- [ ] Supports and brim are removed without gouging either face.
- [ ] No sharp edges, sharp peaks, warping, roughness, excessive flex, cracks,
      or layer separation remain.

## Accessibility validation

- [ ] A qualified Braille reader verifies the physical front and back text,
      orientation, spacing, punctuation, and readability.
- [ ] At least three people evaluate the tactile heart; at least one is blind or
      has substantial tactile-graphics experience.
- [ ] Testers identify the heart or provide a consistent meaningful description.
- [ ] Feedback and any required geometry/profile revisions are recorded.

## Reproduction gate (deferred)

- [ ] Three consecutive cards are produced with no critical defects using the
      documented settings.
- [ ] Another operator reproduces an approved card from this package.
"""
    (package_dir / "PRINTING_AND_FINISHING.md").write_text(printing, encoding="utf-8", newline="\n")
    (package_dir / "QUALITY_CONTROL.md").write_text(quality, encoding="utf-8", newline="\n")


def _manifest(
    package_dir: Path,
    source_image: Path,
    greeting: str,
    message: str,
    geometry: dict[str, object],
    gcode: dict[str, object],
    checks: dict[str, dict[str, object]],
) -> dict[str, object]:
    files = {
        path.name: {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in sorted(package_dir.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "manifest.json"
    }
    return {
        "schema_version": 1,
        "package_id": "reference-heart-with-love",
        "claim": "production package generated and machine-checked",
        "human_review": {
            "braille": REVIEW_STATUS,
            "visual_layout_approved": False,
            "physical_test_print_completed": False,
            "tactile_tester_evaluation_completed": False,
            "operator_quality_control_completed": False,
        },
        "printer_interaction": {
            "gcode_generated_offline": True,
            "submitted_to_printer": False,
            "print_started": False,
        },
        "inputs": {
            "source_filename": source_image.name,
            "source_sha256": sha256_file(source_image),
            "greeting": greeting,
            "main_message_placement": "back face in print and uncontracted UEB",
            "main_message": message,
        },
        "card": {
            "construction": "flat single rigid panel",
            "orientation": "portrait design; upright long-edge production model",
            "finished_width_mm": spec.CARD_WIDTH,
            "finished_height_mm": spec.CARD_HEIGHT,
            "base_panel_thickness_mm": spec.PANEL_THICKNESS,
            "safe_margin_mm": spec.SAFE_MARGIN,
            "material": "PLA",
            "envelope_target": "A7",
        },
        "braille": {
            "code": "Unified English Braille",
            "grade": "Grade 1 (uncontracted)",
            "translation_engine": f"liblouis {louis.version()}",
            "table": "en-ueb-g1.ctb",
            "review_status": REVIEW_STATUS,
            "dot_shape": "spherical cap",
            "dot_base_diameter_mm": spec.BRAILLE_DOT_DIAMETER,
            "within_cell_spacing_mm": spec.BRAILLE_DOT_SPACING,
            "cell_to_cell_spacing_mm": spec.BRAILLE_CELL_SPACING,
            "line_to_line_spacing_mm": spec.BRAILLE_LINE_SPACING,
            "dot_height_mm": spec.BRAILLE_DOT_HEIGHT,
        },
        "tactile": {
            "mode": "silhouette",
            "subject": "heart",
            "relief_height_mm": spec.TACTILE_RELIEF_HEIGHT,
            "edge_treatment": "0.4 mm straight bevel with flat plateau",
            "isolated_fragments": 0,
        },
        "printer_profile": {
            "machine": spec.SV07_PROFILE_NAME,
            "stock_build_volume_xyz_mm": spec.SV07_BUILD_VOLUME,
            "filament": spec.SV07_FILAMENT_PROFILE,
            "process": spec.SV07_PROCESS_PROFILE,
            "nozzle_diameter_mm": spec.NOZZLE_DIAMETER,
            "layer_height_mm": 0.2,
            "initial_nozzle_temperature_c": 235,
            "normal_nozzle_temperature_c": 200,
            "bed_temperature_c": 65,
            "supports": "tree(auto), snug",
            "brim_width_mm": 5,
            "profile_bundle_version": spec.SV07_PROFILE_BUNDLE_VERSION,
            "stock_profile_sha256": PROFILE_HASHES,
        },
        "versions": {
            "generator": __version__,
            "python": platform.python_version(),
            "liblouis": louis.version(),
            "Pillow": PIL.__version__,
            "reportlab": reportlab.Version,
            "manifold3d": importlib.metadata.version("manifold3d"),
            "OrcaSlicer": spec.ORCA_SLICER_VERSION,
            "OrcaSlicer_AppImage_sha256": APPIMAGE_SHA256,
        },
        "deterministic_normalization": {
            "image": "fixed 1200x1200 bilevel PNG; metadata omitted",
            "pdf": "ReportLab invariant mode with page compression",
            "stl": "fixed 80-byte header; little-endian binary triangles",
            "3mf": "sorted deterministic XML; fixed ZIP entry mtime 1980-01-01 and permissions 0644",
            "gcode": "OrcaSlicer pinned at 2.4.2; generated-on wall-clock comment replaced with fixed text; executable commands unchanged",
            "generated_content_excludes": ["randomness", "hostnames", "absolute paths", "wall-clock timestamps"],
            "manifest_self_checksum": "omitted to avoid a recursive checksum; all other package files are listed",
        },
        "geometry": geometry,
        "gcode": gcode,
        "automated_checks": checks,
        "files": files,
    }


def generate_package(
    image_path: Path,
    card_config_path: Path,
    output_dir: Path,
    *,
    slicer_root: Path | None = None,
) -> Path:
    """Generate exactly one package and fail closed on any quality gate."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(card_config_path.read_text(encoding="utf-8"))
    greeting = config["greeting"].strip()
    message = config["message"].strip()
    if not greeting or not message:
        raise ValueError("Greeting and message are required")

    _, normalized = normalize_image(image_path, output_dir)
    greeting_translation = translate(greeting)
    message_translation = translate(message)
    front_lines = wrap_source(greeting, 16)
    back_lines = wrap_source(message, 16)
    write_braille_artifacts(
        greeting_translation, message_translation, front_lines, back_lines, output_dir
    )
    create_visual_preview(
        normalized, greeting, message, front_lines, back_lines,
        output_dir / "visual_preview.png",
    )
    create_layout_pdf(
        normalized, greeting, message, front_lines, back_lines,
        output_dir / "layout.pdf",
    )
    geometry = write_geometry_outputs(front_lines, back_lines, output_dir)
    gcode = slice_card(output_dir / "combined_card.stl", output_dir / "card.gcode", slicer_root)
    _write_operator_documents(output_dir)

    checks = run_flat_card_checks(output_dir)
    assert_checks_pass(checks)
    (output_dir / "checks.json").write_text(
        json.dumps(checks, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    manifest = _manifest(
        output_dir, image_path, greeting, message, geometry, gcode, checks
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return output_dir

