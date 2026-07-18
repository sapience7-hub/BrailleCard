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
deferred), uncontracted UEB for this first calibration example. Note the
milestone says "inside message" but a flat card has no inside: place the
main message on the back face (the spec's flat-card layout puts image,
greeting, and Braille on the front; the back face is the spec-sanctioned
place for a note), in both print and Braille, and record that layout
decision in `scratchpad.md`.

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
network-connected 3D printer (Sovol SV07, Klipper/Moonraker, PLA, 0.4mm
nozzle — facts confirmed by the operator, not guessed). `docs/PRODUCT_GOAL.md`
itself already scopes physical printing as a human ("Operator") step, not
an automated one (see its workflow step 9 and its "Human checks" section)
— this run must not go further than the spec intends:

- Generate G-code as a file. **Never open any network connection to the
  printer or its host** — no Moonraker API calls of any kind, not even
  "read-only" status or capability queries, no ping, no port probe, no
  websocket. There is no fact this run needs that requires contacting the
  printer: take build-volume/bed-size limits from the slicer's own stock
  Sovol SV07 profile (offline data shipped with the slicer), and record
  the values you used in the manifest. Do not write code that is capable
  of submitting or starting a print job, even if you never call it.
- The printer's network address, hostname, and any credentials are out of
  scope for this run: do not put them in code, tests, generated files,
  `scratchpad.md`, `HANDOFF.md`, or commits. Do not read files outside
  this repository looking for printer details (in particular, do not open
  `~/dorqlabs-3d-printer-ai/` — it contains operational credentials);
  everything you need is in this repo or in the slicer's offline profile
  data.
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
- the original input image retained unmodified in the package, plus the
  normalized production image + visual preview PNG;
- Braille source text, UEB transcription (uncontracted), the side-by-side
  source/Braille review artifact the spec calls for, and an explicit
  "not yet human-reviewed" status field — never claim reviewed;
- tactile preview image (silhouette or contour mode);
- SVG/CAD source for the tactile layer;
- STL and 3MF for the combined card geometry;
- G-code generated for the SV07/PLA/0.4mm profile, **not submitted
  anywhere**;
- a printing-and-finishing guide and quality-control checklist (both are
  in the spec's "Output package"; for this run they may be short, honest
  documents — including the spec's operator/human-check steps as unchecked
  items — but they must exist in the package);
- a manifest recording dimensions, materials, versions, settings, and
  checksums;
- automated checks from `docs/PRODUCT_GOAL.md`'s "Automated checks"
  section that apply to a flat single-panel card (margins, Braille-vs-artwork
  collision, Braille dimensional baseline, minimum feature size, no isolated
  tactile fragments or unsafe sharp peaks, card thickness within the flat-card
  template, build-area fit) implemented as real, passing tests — not
  asserted, run.
- Braille dimensional geometry must be checked against the exact 2010 ADA
  ranges in `docs/PRODUCT_GOAL.md` (dot base diameter 1.5-1.6mm, dot
  spacing 2.3-2.5mm within a cell, 6.1-7.6mm cell-to-cell, 10.0-10.2mm
  line-to-line, dot height 0.6-0.9mm) with an automated test, not a
  comment claiming compliance.

Gate: a real test suite you write yourself must pass, covering at minimum
UEB translation correctness (known input/output pairs), Braille dimensional
compliance, and deterministic regeneration (same inputs -> byte-identical
outputs, no randomness, no timestamps/hostnames/absolute paths in generated
files). Two rules that keep this gate honest:

- The UEB known-good pairs must come from an authoritative source
  independent of the translation engine you use (e.g. published UEB/BANA
  examples), with the source cited in the test file. Generating expected
  outputs by running liblouis and pasting them back in only proves
  liblouis equals itself — that is not a correctness test.
- Slicers and 3MF/zip containers embed timestamps and version strings.
  Deterministic regeneration still applies: normalize or strip that
  metadata in a documented post-processing step (fixed zip mtimes,
  stripped/pinned slicer header comments) rather than weakening the
  byte-identical test to accommodate it. Record exactly what is
  normalized in the manifest.

## Stopping conditions

- Definition of Done met and gate passes: stop, write `HANDOFF.md`
  summarizing what was built, what was verified, explicitly restating
  that no print job was submitted to the printer, and listing the human
  steps that remain before this card is "done" in the spec's sense
  (operator test print on the SV07, qualified Braille review, tactile
  tester evaluation) — this run's success claim is "production package
  generated and machine-checked", nothing stronger.
- A genuine blocker (missing dependency, ambiguous spec point that
  materially changes output correctness, the "needs a real test print"
  case above): stop, write the blocker to `scratchpad.md` and `HANDOFF.md`,
  do not guess past it.
- Hard run ceiling: 40 iterations, where one iteration is one
  plan-act-verify cycle (one coherent batch of edits plus the commands run
  to check them). Append a one-line entry to `scratchpad.md` at the end of
  each iteration (`iteration N: what changed, what was verified`) so the
  count is auditable. If you hit the ceiling without meeting the
  Definition of Done, stop and write down exactly what remains — do not
  keep going past the ceiling, do not reset or reinterpret the count to
  buy more iterations, and do not edit tests to make them pass
  artificially. Independent of the iteration count, if the run exceeds
  4 hours of wall-clock time, stop the same way.

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
