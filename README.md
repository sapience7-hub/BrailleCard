# Braille greeting card reference generator

This repository generates one deterministic, machine-checked production package
for the flat 5 × 7 inch reference card in `docs/PRODUCT_GOAL.md`. It does not
discover, contact, upload to, or start a printer.

System prerequisites are Python 3.12, liblouis with `en-ueb-g1.ctb`, ImageMagick,
Pillow, ReportLab, and the pinned `manifold3d==3.5.2`. OrcaSlicer is used only as
an offline command-line slicer. On this arm64 host, install its pinned extraction:

```sh
tools/bootstrap_orca.sh
```

Generate the reference package:

```sh
PYTHONPATH=src python3 -m braille_card \
  --image examples/heart.svg \
  --card examples/card.json \
  --output dist/reference-card
```

The destination must be absent or empty so stale files cannot leak into a
manifest. Run all gates with `pytest -q`. The generated G-code remains a file;
printing, Braille review, tactile testing, and operator quality control are
deliberately human steps documented inside the package.

