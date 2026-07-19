---
handoff_version: 1
project: Braille Greeting Cards
project_root: /home/tangoren/projects/braille-greeting-cards
updated_at: 2026-07-19T12:00:22-04:00
status: ready
branch: master
head: e8d569acc4ed269e65875932fcebb7346a4ff10e
obsidian_note: /home/tangoren/Obsidian on DGX/Dev Logs/Handoffs/Braille Greeting Cards.md
---

# Braille Greeting Cards — Handoff

## Objective

Retain the deterministic, machine-checked 5x7 Braille greeting-card reference
package and record the separately authorized one-off Flat v4 SV07 print and its
continuous/timelapse evidence without overstating physical or Braille quality.

## Resume state

- Current status: reference package objective complete; the Flat v4 operator
  run completed successfully, but direct tactile/quality inspection remains.
- Working tree: expected clean after the closedown documentation commit.
- Active goal: none for this repository; the thread's Ambient P8.1 goal is
  complete and separate.
- Last safe checkpoint: `e8d569acc4ed269e65875932fcebb7346a4ff10e` —
  `docs: record Flat v4 physical run`.
- Branch relation: `master` has no configured upstream or remote; nothing was
  pushed.

## Runtime state

| Component | State | Session action | Reason / check command |
| --- | --- | --- | --- |
| SV07 Flat v4 job | complete, 100%, virtual SD inactive, heater targets 0 C | explicitly started and monitored to completion | Moonraker `print_stats` and `virtual_sdcard` query |
| Continuous camera capture | stopped and finalized | started before print; stopped after post-roll | MKV probes as 1600x1200 H.264, 76:57 |
| 60x timelapse transcode | complete | generated from untouched master | MP4 probes as 1280x720 H.264, 01:16.97 |
| Printer/capture monitors | stopped | one-minute polling completed | No ffmpeg or polling process remains |

## Completed this session

- Printed the exact user-authorized
  `FLAT-braillecard-RIM-v4-ALLCAPS-1h10m.gcode`; Moonraker reported complete
  with no error after 72.67 minutes of extrusion.
- Preserved a hash-verified untouched master and a separately derived,
  hash-verified 60x timelapse on `/mnt/dgxdata`.
- Camera checkpoints found no obvious spaghetti or displacement while keeping
  tactile/Braille claims explicitly unverified.
- Updated the project record to distinguish the original offline pipeline's
  printer boundary from the later, separately authorized operator run.

## Decisions and constraints

- Camera evidence is not a substitute for cooled-part measurement, dot
  inspection, qualified Braille review, or tactile testing.
- The continuous MKV remains the archival source; the MP4 is cropped and graded
  only as a watchable derivative.
- The repository still contains no printer upload/start implementation. The
  physical action was an operator-session use of Moonraker, not product code.

## Changed files

- `HANDOFF.md` — physical run, media evidence, runtime state, and resumable
  closedown snapshot.

## Verification

| Command | Result | Notes |
| --- | --- | --- |
| `pytest -q` | PASS | 8 passed; one ReportLab/Python deprecation warning |
| `git diff --check` | PASS | Clean |
| `ffprobe` on master MKV | PASS | H.264, 1600x1200, 25 fps, 4,617.64 seconds, 1,707,725,924 bytes |
| `ffprobe` on timelapse MP4 | PASS | H.264, 1280x720, 30 fps, 76.97 seconds, 20,996,567 bytes |
| First/middle/last frame decode for both files | PASS | All six frames decoded and were visually inspected |

## Remaining work

- Inspect the cooled Flat v4 card directly for adhesion, warping, dimensions,
  heart rim, printed text, Braille dot integrity, and tactile readability.
- Qualified Braille review and the broader multi-tester/MVP acceptance work
  remain required before any production claim.

## Blockers and risks

- Physical and tactile quality cannot be resolved remotely from the current
  dark, high-contrast camera angle.

## Next action

Remove the cooled Flat v4 card, inspect it against the generated quality
checklist, and record measured defects or acceptance evidence before iterating
the geometry.

## Openup checklist

1. Verify project root, branch, checkpoint, and working tree.
2. Read `GOAL.md`, `docs/PRODUCT_GOAL.md`, and this handoff.
3. Preserve the distinction between machine checks and human review.
4. Report drift before making changes.
5. Continue with the Next action.

## Detailed run record

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
