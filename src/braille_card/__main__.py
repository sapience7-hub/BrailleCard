from __future__ import annotations

import argparse
from pathlib import Path

from .package import generate_package
from .preview import generate_preview


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one offline Braille greeting-card package")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Render review artifacts without geometry export or slicing",
    )
    parser.add_argument("--slicer-root", type=Path)
    args = parser.parse_args()
    if args.preview_only:
        generated = generate_preview(args.image, args.card, args.output)
    else:
        generated = generate_package(args.image, args.card, args.output, slicer_root=args.slicer_root)
    print(generated)


if __name__ == "__main__":
    main()
