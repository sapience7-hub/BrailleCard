---
handoff_version: 1
project: Braille Greeting Cards
project_root: /home/tangoren/projects/braille-greeting-cards
updated_at: 2026-07-20T23:58:55-04:00
status: in-progress
branch: feat/browser-print-workflow
head: f7d6832eb7f2568103c83050c24338f0b816b634
obsidian_note: /home/tangoren/Obsidian on DGX/Dev Logs/Handoffs/Braille Greeting Cards.md
---

# Braille Greeting Cards — Handoff

## Closedown update — 2026-07-20

### Objective

Finish the local BrailleCard Studio and its accompanying demonstration work
without exposing printer control publicly. The user explicitly reports that the
video deliverable is still unfinished; do not represent the project as done.

### Resume state

- Current status: Studio code is complete and machine-checked; the video remains
  outstanding.
- Working tree: clean after commit `f7d6832`.
- Active goal: none.
- Last safe checkpoint: `f7d6832` — `feat(web): add live studio card draft`.

### Runtime state

| Component | State | Session action | Reason / check command |
| --- | --- | --- | --- |
| `braillecard-resting.service` | active | unchanged | Public resting page remains the safe public surface. |
| SV07 Moonraker | inactive print, last state cancelled | read status only | `print_stats`/`virtual_sdcard` showed no active job. |
| Crowsnest camera service | running | restarted once, then configuration restored | Camera 2 is stored in Moonraker as `Nozzle`, rotated 180° for compatible viewers; raw JPEG remains unrotated. |

### Completed this session

- Committed a left-input/right-output Studio with a live browser-only 3 × 4
  portrait visual draft. Typed greeting/message and selected artwork stay local
  until the normal preview form submission.
- Retained server-generated visual, tactile, and Grade 1 UEB review artifacts
  as the authoritative proof after submission.
- Confirmed the public resting page contains no printer connection or personal
  card data.

### Decisions and constraints

- The Studio remains local-only. Public hosting is limited to the resting/judge
  surface until an explicitly isolated read-only demo is designed.
- Camera observation is not part of BrailleCard yet. Moonraker metadata labels
  Camera 2 as `Nozzle` with a 180° display rotation; do not treat that as an
  embedded project capability.
- Never upload or start a printer job from this browser workflow.

### Changed files

- `src/braille_card/web.py` — live local card draft and client-side artwork/text preview.
- `tests/test_web.py` — coverage for the live Studio draft markup.

### Verification

| Command | Result | Notes |
| --- | --- | --- |
| `rtk .venv/bin/python -m pytest -q` | PASS | 30 passed; one existing ReportLab deprecation warning. |
| `PYTHONPATH=src .venv/bin/python -m braille_card --help` | PASS | Required because this environment has not installed the package into `.venv`; direct module invocation without `PYTHONPATH=src` fails. |
| `rtk git diff --check` | PASS | No whitespace errors. |

### Remaining work

- Create the outstanding video deliverable. Its intended audience/content was
  not specified during closeout, so confirm that scope before producing it.

### Blockers and risks

- Human UEB, tactile, visual, and physical-print review remains required before
  production claims.

### Next action

Confirm the video’s target audience and format, then produce that video from
the completed Studio/resting-page state.

## Current local-render slice — 2026-07-20

The website-workflow Step 2 local render slice is implemented through 317174c.
The new preview-only CLI produces retained/normalized image, visual/tactile
preview, and uncontracted UEB review artifacts from one image plus card JSON.
It does not invoke OrcaSlicer, export STL/3MF, generate G-code, start a
browser, or contact printer/camera hardware.

- Focused preview suite: 5 passed.
- Full suite: 13 passed.
- The work is on feat/braille-preview-render; it has not been pushed.
- The next product slice is Step 3, a browser preview that must reuse these
  deterministic artifacts and preserve the separate operator print boundary.

## Objective

Retain the deterministic, machine-checked 5x7 Braille greeting-card reference
package and its Flat v4 print evidence, then plan a staged, verifiable website
workflow for tactile-photo cards without starting a one-shot implementation.

## Resume state

- Current status: reference package and Flat v4 operator run are complete. The
  user accepts the larger plaque/tactile-photograph direction and wants the
  next session to plan the website workflow in verified milestones. Earlier
  tactile feedback that the Latin text and Braille were too small is recorded,
  but geometry iteration is not the immediate priority.
- Working tree: clean before this handoff update.
- Active goal: none for this repository.
- Last safe checkpoint: `ff82599437fb2866509e061a6e5d319f167dc554` —
  `docs: close physical print session`.
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

- Treat the product as a tactile photograph/plaque: a relief image with Latin
  text and Braille. Card size remains a product choice for the staged website
  plan; smaller tiles are testers rather than the default finished card.
- Do not make geometry calibration a prerequisite for planning the workflow.
  The prior print established that the larger plaque format is feasible; the
  earlier small-text/small-dot feedback remains a future design input.
- Keep preview and production separate: render first, show the user the
  image/text/Braille result, require explicit operator print approval, then
  show camera and print-job status. Never silently start a printer.
- Camera evidence is not a substitute for cooled-part measurement, dot
  inspection, qualified Braille review, or tactile testing.
- The continuous MKV remains the archival source; the MP4 is cropped and graded
  only as a watchable derivative.
- The repository still contains no printer upload/start implementation. The
  physical action was an operator-session use of Moonraker, not product code.

## Website workflow sequence

1. **Plan and acceptance map:** define upload, short message, size choice,
   rendered preview, explicit print approval, camera, and job-status boundaries.
   Verify in writing; do not write application code.
2. **Local render slice:** build and test a deterministic local render from a
   sample image and message. Verify relief preview, Latin text, and Braille
   artifacts without camera or printer connection.
3. **Browser preview slice:** add upload and message entry, render the same
   artifacts in the browser, and verify error states and saved job metadata.
4. **Operator print slice:** add a separate approval action and mocked job
   state first. Verify that no print can begin before approval.
5. **Hardware observation slice:** connect read-only camera and job-status
   updates, then test a real print only with separate explicit authorization.

## Changed files

- `HANDOFF.md` — preserves the product-direction change and staged website
  workflow for the next session.

## Verification

| Command | Result | Notes |
| --- | --- | --- |
| `pytest -q` | PASS | 8 passed; one ReportLab/Python deprecation warning |
| `git diff --check` | PASS | Clean |
| `ffprobe` on master MKV | PASS | H.264, 1600x1200, 25 fps, 4,617.64 seconds, 1,707,725,924 bytes |
| `ffprobe` on timelapse MP4 | PASS | H.264, 1280x720, 30 fps, 76.97 seconds, 20,996,567 bytes |
| First/middle/last frame decode for both files | PASS | All six frames decoded and were visually inspected |

## Remaining work

- Complete website-workflow step 1 only: a written acceptance map and verified
  implementation plan. Do not begin browser, printer, or camera slices in the
  same step.
- The earlier text/Braille-size feedback, qualified Braille review, and broader
  multi-tester acceptance remain requirements before production claims, but do
  not block the next planning step.

## Blockers and risks

- Finished-card size, website hosting/storage, and eventual camera/printer
  integration are intentionally unselected. Resolve them within the staged plan;
  no hardware action is authorized by this handoff.

## Next action

Create the website-workflow acceptance map, then present only the first
implementation slice (deterministic local render) for approval before coding.

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

## Legacy production-acceptance conditions

These remain conditions for a production-quality claim. They are not a blocker
for the next website-planning session, which the user has explicitly prioritized.

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
