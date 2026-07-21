"""Deterministic, preview-only local render workflow."""

from __future__ import annotations

import json
from pathlib import Path

from .braille import REVIEW_STATUS, translate, wrap_source
from .documents import (
    create_visual_preview,
    write_braille_artifacts,
)
from .geometry import write_source_tactile_preview, write_source_tactile_svg
from .images import normalize_image, validate_preview_image
from .spec import MAX_BRAILLE_CELLS_PER_LINE, MAX_GREETING_CHARACTERS, MAX_MESSAGE_CHARACTERS


def _load_card(card_config_path: Path) -> tuple[str, str]:
    try:
        config = json.loads(card_config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unreadable card configuration: {card_config_path}") from exc
    greeting = config.get("greeting")
    message = config.get("message")
    if not isinstance(greeting, str) or not greeting.strip():
        raise ValueError("Greeting is required")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Message is required")
    greeting = greeting.strip()
    message = message.strip()
    if len(greeting) > MAX_GREETING_CHARACTERS:
        raise ValueError(
            f"Greeting must not exceed {MAX_GREETING_CHARACTERS} characters "
            f"(got {len(greeting)})"
        )
    if len(message) > MAX_MESSAGE_CHARACTERS:
        raise ValueError(
            f"Message must not exceed {MAX_MESSAGE_CHARACTERS} characters "
            f"(got {len(message)})"
        )
    return greeting, message


def _write_manifest(output_dir: Path, image_path: Path, greeting: str, message: str) -> None:
    manifest = {
        "schema_version": 1,
        "claim": "preview artifacts generated; not print-ready",
        "human_review": {
            "braille": REVIEW_STATUS,
            "visual_layout_approved": False,
            "tactile_tester_evaluation_completed": False,
        },
        "printer_interaction": {
            "contacted_printer": False,
            "submitted_to_printer": False,
            "print_started": False,
        },
        "inputs": {
            "source_filename": image_path.name,
            "greeting": greeting,
            "message": message,
        },
        "artifacts": [
            f"original_input{image_path.suffix.lower()}",
            "normalized_production.png",
            "visual_preview.png",
            "tactile_preview.png",
            "tactile_layer.svg",
            "braille_source.txt",
            "braille_ueb.brf",
            "braille_ueb_unicode.txt",
            "braille.json",
            "braille_review.html",
        ],
    }
    (output_dir / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def generate_preview(image_path: Path, card_config_path: Path, output_dir: Path) -> Path:
    """Render review artifacts without geometry export, slicing, or hardware access."""
    validate_preview_image(image_path)
    greeting, message = _load_card(card_config_path)
    greeting_translation = translate(greeting)
    message_translation = translate(message)
    front_lines = wrap_source(greeting, MAX_BRAILLE_CELLS_PER_LINE)
    back_lines = wrap_source(message, MAX_BRAILLE_CELLS_PER_LINE)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    _, normalized = normalize_image(image_path, output_dir)
    write_braille_artifacts(
        greeting_translation, message_translation, front_lines, back_lines, output_dir
    )
    create_visual_preview(
        normalized,
        greeting,
        message,
        front_lines,
        back_lines,
        output_dir / "visual_preview.png",
    )
    write_source_tactile_preview(normalized, output_dir / "tactile_preview.png")
    write_source_tactile_svg(normalized, output_dir / "tactile_layer.svg")
    _write_manifest(output_dir, image_path, greeting, message)
    return output_dir
