from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from PIL import Image

from braille_card.preview import generate_preview


def _card(path: Path, greeting: str = "With love", message: str = "You make every day bright.") -> Path:
    path.write_text(
        json.dumps({"greeting": greeting, "message": message, "subject": "heart"}),
        encoding="utf-8",
    )
    return path


def test_preview_emits_review_artifacts_without_production_outputs(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]
    preview = generate_preview(
        repository / "examples/heart.svg",
        repository / "examples/card.json",
        tmp_path / "preview",
    )

    expected = {
        "original_input.svg",
        "normalized_production.png",
        "visual_preview.png",
        "tactile_preview.png",
        "tactile_layer.svg",
        "braille_source.txt",
        "braille_ueb.brf",
        "braille_ueb_unicode.txt",
        "braille.json",
        "braille_review.html",
        "render_manifest.json",
    }
    assert {path.name for path in preview.iterdir()} == expected
    assert all((preview / name).stat().st_size > 0 for name in expected)

    manifest = json.loads((preview / "render_manifest.json").read_text(encoding="utf-8"))
    assert manifest["claim"] == "preview artifacts generated; not print-ready"
    assert manifest["human_review"]["braille"] == "not yet human-reviewed"
    assert manifest["printer_interaction"] == {
        "contacted_printer": False,
        "submitted_to_printer": False,
        "print_started": False,
    }
    assert manifest["artifacts"][0] == "original_input.svg"
    assert not {"card.gcode", "combined_card.stl", "combined_card.3mf"} & {
        path.name for path in preview.iterdir()
    }


def test_preview_output_is_byte_identical(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]
    first = generate_preview(
        repository / "examples/heart.svg",
        repository / "examples/card.json",
        tmp_path / "first",
    )
    second = generate_preview(
        repository / "examples/heart.svg",
        repository / "examples/card.json",
        tmp_path / "second",
    )
    assert {path.name: path.read_bytes() for path in first.iterdir()} == {
        path.name: path.read_bytes() for path in second.iterdir()
    }


def test_preview_enforces_raster_and_text_limits(tmp_path: Path) -> None:
    image = Image.new("RGB", (600, 600), "white")
    valid = tmp_path / "valid.png"
    image.save(valid)
    assert generate_preview(valid, _card(tmp_path / "valid.json"), tmp_path / "valid-preview").is_dir()

    too_small = tmp_path / "too-small.png"
    Image.new("RGB", (599, 600), "white").save(too_small)
    with pytest.raises(ValueError, match="at least 600"):
        generate_preview(too_small, _card(tmp_path / "small.json"), tmp_path / "small-preview")

    too_large = tmp_path / "too-large.png"
    too_large.write_bytes(b"x" * (15 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="15 MB"):
        generate_preview(too_large, _card(tmp_path / "large.json"), tmp_path / "large-preview")

    with pytest.raises(ValueError, match="30 characters"):
        generate_preview(valid, _card(tmp_path / "long-greeting.json", greeting="g" * 31), tmp_path / "long-greeting")
    with pytest.raises(ValueError, match="140 characters"):
        generate_preview(valid, _card(tmp_path / "long-message.json", message="m" * 141), tmp_path / "long-message")


def test_preview_rejects_unsupported_and_unreadable_images(tmp_path: Path) -> None:
    unsupported = tmp_path / "unsupported.gif"
    unsupported.write_bytes(b"not an image")
    with pytest.raises(ValueError, match="Unsupported image type"):
        generate_preview(unsupported, _card(tmp_path / "unsupported.json"), tmp_path / "unsupported-preview")

    unreadable = tmp_path / "broken.svg"
    unreadable.write_text("<svg>", encoding="utf-8")
    with pytest.raises(ValueError, match="Unreadable SVG"):
        generate_preview(unreadable, _card(tmp_path / "broken.json"), tmp_path / "broken-preview")


def test_preview_cli_does_not_need_a_slicer_root(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]
    environment = {**os.environ, "PYTHONPATH": str(repository / "src")}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "braille_card",
            "--preview-only",
            "--image",
            str(repository / "examples/heart.svg"),
            "--card",
            str(repository / "examples/card.json"),
            "--output",
            str(tmp_path / "preview"),
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "preview" / "card.gcode").exists()

    help_result = subprocess.run(
        [sys.executable, "-m", "braille_card", "--help"],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0
    assert "--slicer-root" in help_result.stdout
