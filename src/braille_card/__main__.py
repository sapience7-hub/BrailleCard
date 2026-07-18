from __future__ import annotations

import argparse
from pathlib import Path

from .package import generate_package


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one offline Braille greeting-card package")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--slicer-root", type=Path)
    args = parser.parse_args()
    generated = generate_package(args.image, args.card, args.output, slicer_root=args.slicer_root)
    print(generated)


if __name__ == "__main__":
    main()

