# Handoff — Braille greeting card immediate milestone

## 2026-07-19 one-off Flat v4 physical run

The user explicitly authorized one physical print of
`FLAT-braillecard-RIM-v4-ALLCAPS-1h10m.gcode` on the SV07. The exact uploaded
file was selected and started through Moonraker after confirming that the
printer was ready, the virtual SD was inactive, and the camera showed an empty
build plate.

- Camera capture began at 09:03:45 EDT; the printer entered its start/heat-up
  sequence at approximately 09:07:40 EDT and began extrusion at approximately
  09:10:58 EDT.
- Moonraker reported `complete`, 100% progress, inactive virtual SD, and no
  error message at 10:23:38 EDT. Total job duration was 75.96 minutes and
  extrusion/print duration was 72.67 minutes. The nozzle and bed targets both
  returned to 0 C after completion.
- Read-only one-minute telemetry checks and camera checkpoints found no error,
  obvious spaghetti, or visible part displacement. This does **not** establish
  Braille accuracy, tactile quality, dot integrity, adhesion, or dimensional
  conformance; the cooled part still needs direct human inspection.
- The untouched continuous capture is
  `/mnt/dgxdata/recordings/braille-greeting-cards/FLAT-braillecard-RIM-v4-ALLCAPS-full-capture-2026-07-19.mkv`
  (1600x1200 H.264, 25 fps, 76:57, 1,707,725,924 bytes, SHA-256
  `c7796e364d3d106d2a0bc87a9bf8b1556f54e1db277042276345d4953ad51cdd`).
- The derived 60x timelapse is
  `/mnt/dgxdata/recordings/braille-greeting-cards/FLAT-braillecard-RIM-v4-ALLCAPS-timelapse-2026-07-19.mp4`
  (1280x720 H.264, 30 fps, 01:16.97, 20,996,567 bytes, SHA-256
  `9d192b24caac4398cd95ab922e341d2db3f355f2347ea08e100ac61df5187d28`).
  It is cropped and gently graded for visibility; the MKV above remains the
  archival source. The printer's lamp clips highlights directly beneath the
  toolhead, and the rest of the camera view is dark.

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

When the deterministic reference package described below was generated, no
printer or printer host was contacted, discovered, queried, pinged, probed, or
controlled. Its only printer-related result was the local `card.gcode` file,
and the repository still contains no printer upload or print-start
implementation. The later user-authorized, one-off Flat v4 operator run is
recorded separately above and does not change that implementation boundary.

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
