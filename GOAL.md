# /goal — Braille Greeting Card Generator

Implement the "Immediate next milestone" scope from `docs/PRODUCT_GOAL.md`
in this repository, working autonomously until the Definition of Done below
is met or a stopping condition fires. Read `docs/PRODUCT_GOAL.md` in full
before writing any code — it is the product specification and overrides
anything else you find, except this file's explicit scope and safety
boundaries, which are narrower and take precedence for THIS run.

## Objective (this run's actual scope)

Build the smallest pipeline that turns ONE image + ONE short message into a
complete, printable production package for a single 5x7 flat PLA greeting
card — matching `docs/PRODUCT_GOAL.md`'s own "Immediate next milestone":
a high-contrast single-subject image, a short front greeting + inside
message, flat 5x7 portrait template, silhouette-or-contour tactile
conversion (not full photo bas-relief — that's explicitly harder and
deferred), uncontracted UEB for this first calibration example.

"Smallest" is measured against the spec's own MVP acceptance criteria and
quality/safety gates, not against effort — the dimensional tolerances,
Braille translation correctness, and file-format requirements are real
requirements, not optional polish. Do not build the full 7-phase product
(no user-facing app, no multi-image-mode support, no fold/hinge variants,
no batch/production tooling) — those are explicitly out of scope for this
run. Where the spec is silent on an implementation detail, choose the
simplest approach consistent with the spec's stated dimensional/safety
constraints and note the choice in `scratchpad.md`.

## Hard safety boundary — read this before writing any code

This project ends in a REAL physical object printed on a REAL, currently
network-connected 3D printer (SV07, Moonraker at `192.168.1.144:7125`,
Klipper firmware, PLA, 0.4mm nozzle — facts confirmed live in
`~/dorqlabs-3d-printer-ai/MASTER_PLAN.md`, not guessed). `docs/PRODUCT_GOAL.md`
itself already scopes physical printing as a human ("Operator") step, not
an automated one (see its workflow step 9 and its "Human checks" section)
— this run must not go further than the spec intends:

- Generate G-code as a file. **Never** connect to the printer's Moonraker
  API, submit a print job, or issue any command that would cause the
  physical printer to move, heat, or print. If you write code that talks
  to Moonraker at all, it may only be **read-only** status/capability
  queries (e.g. confirming build-volume/bed-size limits for a geometry
  validation check) — never `/printer/print/start` or equivalent, and
  never anything that writes to the printer.
- If a task seems to require an actual test print to verify success,
  stop and report that as a blocker requiring a human operator — do not
  attempt it yourself.
- This is a genuine, non-negotiable stopping condition. Violating it is a
  failure of this run regardless of what else was accomplished.

## Braille translation

Do not hand-roll a UEB translation table — use a real, established,
open-source Braille translation engine (liblouis is the standard one;
confirm it's actually installable in this environment before depending on
it, and report as a blocker rather than improvising a hand-written
translation table if it isn't available). Braille correctness is a real
accessibility/dignity concern, not a cosmetic detail — `docs/PRODUCT_GOAL.md`
requires a qualified human reviewer before any production claim; your job
is to get the mechanical translation right and generate the side-by-side
source/Braille review artifact the spec calls for, not to claim the
translation is human-verified.

## Definition of Done (this run)

Given one sample high-contrast image (generate or source a simple
placeholder subject if none is provided — e.g. a solid silhouette shape)
and one short sample greeting/message, the pipeline must produce, for a
single flat 5x7 portrait card:

- print-ready layout PDF;
- normalized production image + visual preview PNG;
- Braille source text, UEB transcription (uncontracted), and an explicit
  "not yet human-reviewed" status field — never claim reviewed;
- tactile preview image (silhouette or contour mode);
- SVG/CAD source for the tactile layer;
- STL and 3MF for the combined card geometry;
- G-code generated for the SV07/PLA/0.4mm profile, **not submitted
  anywhere**;
- a manifest recording dimensions, materials, settings, and checksums;
- automated checks from `docs/PRODUCT_GOAL.md`'s "Automated checks"
  section that apply to a flat single-panel card (margins, Braille-vs-artwork
  collision, Braille dimensional baseline, minimum feature size, build-area
  fit) implemented as real, passing tests — not asserted, run.
- Braille dimensional geometry must be checked against the exact 2010 ADA
  ranges in `docs/PRODUCT_GOAL.md` (dot base diameter 1.5-1.6mm, dot
  spacing 2.3-2.5mm within a cell, 6.1-7.6mm cell-to-cell, 10.0-10.2mm
  line-to-line, dot height 0.6-0.9mm) with an automated test, not a
  comment claiming compliance.

Gate: a real test suite you write yourself must pass, covering at minimum
UEB translation correctness (known input/output pairs), Braille dimensional
compliance, and deterministic regeneration (same inputs -> byte-identical
outputs, no randomness, no timestamps/hostnames/absolute paths in generated
files).

## Stopping conditions

- Definition of Done met and gate passes: stop, write `HANDOFF.md`
  summarizing what was built, what was verified, and explicitly restate
  that no print job was submitted to the printer.
- A genuine blocker (missing dependency, ambiguous spec point that
  materially changes output correctness, the "needs a real test print"
  case above): stop, write the blocker to `scratchpad.md` and `HANDOFF.md`,
  do not guess past it.
- Hard run ceiling: 40 iterations. If you hit this without meeting the
  Definition of Done, stop and write down exactly what remains — do not
  keep going past the ceiling, and do not edit tests to make them pass
  artificially.

## Implementation notes

- Python is the natural fit given liblouis' bindings and the existing
  STL/G-code tooling ecosystem; don't add packages beyond what's needed
  for this scope.
- Determinism matters throughout, matching this box's other projects: no
  random seeds without a fixed literal value, no wall-clock timestamps in
  generated file content.
- Commit incrementally as real milestones complete (image pipeline, UEB
  translation, geometry generation, export, tests) — not one giant commit
  at the end.
