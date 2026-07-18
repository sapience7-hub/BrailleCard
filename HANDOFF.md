# Handoff — Braille greeting card immediate milestone

## Status

**Production package generated and machine-checked.** This is intentionally not
a claim that the card is physically proven, Braille-reviewed, tactile-tested,
commercially accessible, or production-approved.

The complete reference package is in `dist/reference-card/`. It contains the
two-page exact-size layout PDF, retained original SVG, normalized and preview
PNGs, print/UEB/review artifacts, tactile preview and SVG source, combined
single-solid STL and deterministic 3MF, offline-sliced G-code, operator guide,
unchecked quality checklist, machine-check report, and checksum manifest.

## What was built

- One deterministic 127.0 × 177.8 × 2.0 mm rigid portrait card.
- Front: high-contrast heart, connected 0.8 mm bevel-edged tactile silhouette,
  raised visual greeting, and matching uncontracted UEB.
- Back: the milestone's “inside” message represented as raised visual text and
  matching uncontracted UEB, mirrored in the CAD coordinate system so it reads
  correctly when the back faces the reader.
- Exact spherical-cap Braille geometry: 1.55 mm base diameter, 2.4 mm within-cell
  spacing, 6.4 mm cell pitch, 10.1 mm line pitch, and 0.75 mm height.
- One Boolean-unioned, manifold, upright production model with supports and brim
  enabled for the two raised faces.
- G-code created locally with the checksum-pinned OrcaSlicer 2.4.2 stock Sovol
  SV07 0.4 mm, SV07 PLA, and 0.20 mm profiles. The generated file has 889 layers
  and records the stock 220 × 220 × 250 mm build volume.

## Verification completed

`pytest -q` passes 8 tests. The gate covers:

- independent authoritative UEB examples from the Australian Braille Authority;
- all five exact ADA dimensional ranges named in `docs/PRODUCT_GOAL.md`;
- safe margins, artwork/Braille separation, minimum feature size, connected
  tactile geometry, no point peaks, panel thickness, and build-area fit;
- one readable retained input and normalized image;
- successful PDF, SVG, STL, 3MF, G-code, guide, and checklist exports;
- one true manifold mesh component and exact cap base/height geometry;
- real stock-profile G-code markers, supports, temperatures, and layer count;
- fixed 3MF ZIP metadata, exact 5 × 7 inch two-page PDF geometry, and manifest
  checksum integrity; and
- two complete regenerations with byte-identical files and no randomness,
  hostnames, absolute paths, wall-clock timestamps, or path-sensitive PDF IDs.

All 10 recorded package checks pass and every checksum in `manifest.json`
matches the generated file. The Braille review status is explicitly
`not yet human-reviewed`.

## Physical-printer boundary

No printer or printer host was contacted, discovered, queried, pinged, probed,
or controlled. No print job was submitted or started. The only printer-related
result is the local `card.gcode` file. The repository contains no printer upload
or print-start implementation.

## Human work that remains

Before this card is “done” in the product specification's sense:

1. An operator must inspect the full local G-code/layer preview and perform a
   supervised SV07 PLA test print, then measure the panel and Braille geometry.
2. A qualified Braille reviewer must proofread the source/transcription and
   evaluate the physical front/back orientation, spacing, punctuation, and dots.
3. At least three tactile testers must evaluate the heart, including at least one
   blind tester or person with substantial tactile-graphics experience.
4. The operator must finish the brim/supports and complete every unchecked item
   in `QUALITY_CONTROL.md`, including sharpness, warping, dot integrity, and layer
   adhesion checks.
5. Three defect-free consecutive cards and independent operator reproduction
   remain required for the broader MVP acceptance criteria.

The upright support strategy and tactile recognizability are therefore honest
physical-validation items, not machine-verified claims.

## Reproduce

Install the pinned offline slicer extraction with `tools/bootstrap_orca.sh`, then:

```sh
pytest -q
PYTHONPATH=src python3 -m braille_card \
  --image examples/heart.svg \
  --card examples/card.json \
  --output dist/reference-card
```

The generator requires an absent or empty destination to prevent stale files
from entering a manifest.
