# Sample output (for judges without the hardware)

This is the exact, byte-deterministic production package produced by:

```sh
PYTHONPATH=src python3 -m braille_card \
  --image examples/heart.svg \
  --card examples/card.json \
  --output dist/reference-card
```

Regenerate it yourself with the command above (delete `dist/reference-card`
first if it already exists — the generator refuses to write into a
non-empty destination).

| File | What it is |
| --- | --- |
| `visual_preview.png` | Front/back visual card layout |
| `tactile_preview.png` | Source-derived tactile interpretation preview |
| `tactile_layer.svg` | Tactile layer as SVG |
| `original_input.svg`, `normalized_production.png` | Retained input and normalized artwork |
| `braille_source.txt`, `braille_ueb_unicode.txt`, `braille_ueb.brf`, `braille_review.html` | UEB Grade 1 (uncontracted) transcription in three formats, plus a side-by-side review page |
| `combined_card.stl`, `combined_card.3mf` | Production-ready 3D geometry (one manifold solid) |
| **`card.gcode`** | **G-code sliced for a Sovol SV07, 0.4 mm nozzle, stock SV07 PLA, 0.20 mm layer profile (OrcaSlicer 2.4.2).** Slicing is fully offline — no printer was contacted to produce this file. |
| `layout.pdf` | Exact-size two-page print layout |
| `geometry.json`, `checks.json`, `manifest.json` | Machine-verified dimensions, safety-gate results, and a checksum manifest for every file in this folder |
| `PRINTING_AND_FINISHING.md`, `QUALITY_CONTROL.md` | Operator guide and the unchecked physical quality-control checklist |

**What this proves:** the full software pipeline — photo in, UEB Braille
translation, tactile geometry, and a printer-specific G-code file out — runs
completely offline and produces a real, checksummed production package.

**What this does not prove:** physical print quality, Braille legibility, or
tactile recognizability. Those require an actual SV07 print and human
review — see `QUALITY_CONTROL.md`. `card.gcode` in this folder has not been
printed; it is provided so judges can inspect real slicer output without
owning a Sovol SV07.
