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

Generate only the local review artifacts:

~~~sh
PYTHONPATH=src python3 -m braille_card \
  --preview-only \
  --image examples/heart.svg \
  --card examples/card.json \
  --output dist/local-preview
~~~

Preview-only output contains the retained/normalized image, visual and tactile
previews, plus uncontracted UEB review artifacts. It does not generate
production geometry or G-code, invoke OrcaSlicer, start a browser, or contact
a printer.

Run the local browser workspace:

~~~sh
PYTHONPATH=src python3 -m braille_card --serve
~~~

The workspace binds to `127.0.0.1:8765` by default. It saves preview jobs
locally and keeps visual/Braille/tactile review separate from slicing, printer
approval, and remote observation.

To enable its **read-only** Sovol SV07 status check, configure Moonraker only
in the shell that starts the local studio. Do not put credentials in a job file
or browser form:

~~~sh
export MOONRAKER_URL="http://printer.local"
export MOONRAKER_API_KEY="your-local-moonraker-api-key"
PYTHONPATH=src python3 -m braille_card --serve
~~~

`MOONRAKER_BEARER_TOKEN` is supported instead of `MOONRAKER_API_KEY`. The
current browser integration queries status only after an operator clicks its
button; it cannot upload G-code, start a print, run G-code, or alter printer
state.

The destination must be absent or empty so stale files cannot leak into a
manifest. Run all gates with `pytest -q`. The generated G-code remains a file;
printing, Braille review, tactile testing, and operator quality control are
deliberately human steps documented inside the package.

## How we built it

BrailleCard was developed through an AI-assisted coding workflow using Codex,
Claude Code, and Hermes. Hermes also allowed us to use free and locally
hosted language models during development.

These tools helped with planning, implementation, debugging, interface
refinement, and testing. The application itself combines image handling,
greeting-card layout, text input, and Braille translation in a simple
workflow:

1. Add a photo.
2. Enter a personal message.
3. Translate the message into Braille.
4. Review the card layout.
5. Save or print the finished design.

We treated Braille generation as structured text processing rather than
image generation, because visual AI systems frequently reproduce Braille
characters incorrectly.
