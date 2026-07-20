"""Deterministic normalization and preview generation for the reference image."""

from __future__ import annotations

import io
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageOps

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
MAX_PREVIEW_RASTER_BYTES = 15 * 1024 * 1024
MIN_PREVIEW_RASTER_DIMENSION = 600


def _open_image(path: Path) -> Image.Image:
    if path.suffix.lower() == ".svg":
        completed = subprocess.run(
            ["convert", str(path), "png:-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return Image.open(io.BytesIO(completed.stdout))
    return Image.open(path)


def validate_preview_image(source: Path) -> None:
    """Validate the objective image constraints for the local preview slice."""
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED:
        supported = ", ".join(sorted(SUPPORTED))
        raise ValueError(
            f"Unsupported image type: {suffix or '<none>'}. Supported types: {supported}"
        )
    if not source.is_file():
        raise ValueError(f"Image file does not exist: {source}")
    if suffix == ".svg":
        try:
            ET.parse(source)
        except ET.ParseError as exc:
            raise ValueError(f"Unreadable SVG image: {source.name}") from exc
        return
    if source.stat().st_size > MAX_PREVIEW_RASTER_BYTES:
        raise ValueError("Raster image must not exceed 15 MB")
    try:
        with Image.open(source) as image:
            image.verify()
        with Image.open(source) as image:
            width, height = image.size
    except OSError as exc:
        raise ValueError(f"Unreadable raster image: {source.name}") from exc
    if width < MIN_PREVIEW_RASTER_DIMENSION or height < MIN_PREVIEW_RASTER_DIMENSION:
        raise ValueError(
            f"Raster image must be at least {MIN_PREVIEW_RASTER_DIMENSION} by "
            f"{MIN_PREVIEW_RASTER_DIMENSION} pixels"
        )


def normalize_image(source: Path, package_dir: Path) -> tuple[Path, Path]:
    """Retain source bytes and emit a 1200×1200 bilevel production PNG."""
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported image type: {suffix}")
    original = package_dir / f"original_input{suffix}"
    shutil.copyfile(source, original)

    with _open_image(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("L")
        image = ImageOps.contain(image, (1100, 1100), Image.Resampling.LANCZOS)
        canvas = Image.new("L", (1200, 1200), 255)
        canvas.paste(image, ((1200 - image.width) // 2, (1200 - image.height) // 2))
        normalized = canvas.point(lambda value: 0 if value < 128 else 255, mode="1")

    normalized_path = package_dir / "normalized_production.png"
    normalized.save(normalized_path, format="PNG", optimize=False)
    return original, normalized_path
