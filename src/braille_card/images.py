"""Deterministic normalization and preview generation for the reference image."""

from __future__ import annotations

import io
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".svg"}


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

