from __future__ import annotations

import argparse
from pathlib import Path

from .package import generate_package
from .preview import generate_preview
from .web import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one offline Braille greeting-card package")
    parser.add_argument("--image", type=Path)
    parser.add_argument("--card", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--serve", action="store_true", help="Run the local browser preview workspace")
    parser.add_argument("--host", default="127.0.0.1", help="Local web-server bind host")
    parser.add_argument("--port", type=int, default=8765, help="Local web-server port")
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Render review artifacts without geometry export or slicing",
    )
    parser.add_argument("--slicer-root", type=Path)
    args = parser.parse_args()
    if args.serve:
        create_app().run(host=args.host, port=args.port, debug=False)
        return
    if args.image is None or args.card is None or args.output is None:
        parser.error("--image, --card, and --output are required unless --serve is used")
    if args.preview_only:
        generated = generate_preview(args.image, args.card, args.output)
    else:
        generated = generate_package(args.image, args.card, args.output, slicer_root=args.slicer_root)
    print(generated)


if __name__ == "__main__":
    main()
