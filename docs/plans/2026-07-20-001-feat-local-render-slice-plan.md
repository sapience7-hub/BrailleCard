---
title: "feat: Add preview-only local render slice"
created_at: 2026-07-20
type: feat
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-plan-bootstrap
origin: docs/WEBSITE_ACCEPTANCE_MAP.md
execution: code
---

# Preview-only local render slice

## Goal Capsule

Add website-workflow Step 2 to the deterministic card generator: a local CLI path that accepts one supported image and one short greeting/message, then emits reviewable visual, tactile, and UEB artifacts without invoking OrcaSlicer, producing production geometry, generating G-code, starting a browser, or contacting hardware.

The acceptance map is the product authority for this slice. GOAL.md remains the safety authority: no printer discovery, networking, upload, or print-start capability may be introduced.

---

## Product Contract

### Summary

The existing generator produces a complete offline production package, which includes geometry and slicing. The website workflow needs an earlier, lower-risk render boundary so a user can inspect the normalized image, Latin text, tactile representation, and uncontracted UEB before any production-package work is considered.

### Problem Frame

There is no independent render path today. generate_package() always progresses through geometry and slice_card(), making local preview slower and coupling a review action to an OrcaSlicer installation even though Step 2 expressly has no slicer or hardware need.

### Requirements

- R1. A preview-only local command accepts one PNG, JPEG, WebP, or SVG image and an existing card JSON input containing a greeting and a message.
- R2. The command emits a deterministic, self-contained preview directory with the retained original, normalized production image, front/back visual preview, tactile preview, tactile SVG, UEB source/Unicode/BRF artifacts, side-by-side Braille review HTML, and a render manifest.
- R3. The render manifest states that the output is not human-reviewed, is not print-ready, and has not contacted or submitted work to a printer.
- R4. Preview-only input validation rejects unsupported or unreadable images, raster files larger than 15 MB, raster images below 600 by 600 pixels, greetings above 30 characters, and messages above 140 characters with actionable errors.
- R5. The preview path reuses the existing liblouis Grade 1 UEB translation and visual/tactile rendering conventions; it does not hand-roll Braille translation or create a separate layout system.
- R6. The existing full-package CLI and its output contract remain compatible and continue to be the only path that invokes geometry export or offline slicing.

### Scope Boundaries

The slice does not add a browser UI, persistence, user accounts, crop controls, 3D interactive preview, PDF/STL/3MF/G-code, print approval, printer networking, camera access, Moonraker telemetry, or hardware controls.

Image contrast and subject-quality assessment remain explicit human review concerns in this slice. Validation only establishes deterministic, objective file and size constraints.

---

## Planning Contract

### Key Technical Decisions

- KTD1. Add a separate preview orchestration function instead of introducing a preview mode inside generate_package(). This makes the no-slicer boundary directly testable and preserves the full-package contract.
- KTD2. Keep the existing JSON card input schema for the first slice. It supplies the required greeting/message without prematurely selecting a web request schema.
- KTD3. Reuse normalize_image(), wrap_source(), write_braille_artifacts(), create_visual_preview(), write_tactile_preview(), and write_tactile_svg(). The new path may compose those helpers but must not call write_geometry_outputs() or slice_card().
- KTD4. Enforce the acceptance-map input limits only on the preview path. The reference package remains reproducible from its existing sample inputs and does not gain a new, unrelated validation constraint.

### High-Level Technical Design

The render flow is: image and card JSON enter preview validation; deterministic orchestration then creates the normalized/visual, UEB/review, and tactile artifacts; those artifacts are listed in a preview manifest. No stage branches into geometry export, slicing, browser serving, or hardware interaction.

### Assumptions

- The current single-subject silhouette is the only tactile mode in this slice.
- Text that passes the character limits must still fit the current fixed card layout. Layout-specific overflow is an actionable render error, not silently truncated text.

### Risks and Mitigations

- The full generator and preview path could drift in visual/Braille output. Focused integration tests will compare their shared artifacts for the same input.
- Refactoring tactile-output helpers could accidentally affect production geometry. Geometry and determinism tests remain unchanged and run in the full suite.

---

## Implementation Units

### U1. Add deterministic preview orchestration and validation

- **Goal:** Introduce a preview-only library entry point with a structural manifest and objective input validation.
- **Requirements:** R1, R2, R3, R4, R5.
- **Dependencies:** None.
- **Files:** src/braille_card/preview.py (new), src/braille_card/images.py, src/braille_card/geometry.py, tests/test_preview.py (new).
- **Approach:** Extract only the tactile PNG/SVG writers needed by preview from the production geometry wrapper. The preview orchestrator validates inputs before creating output, retains and normalizes the image, creates the existing visual and Braille review artifacts, writes tactile PNG/SVG, and writes a deterministic manifest. It contains no slicer import or printer-facing behavior.
- **Execution note:** Start with failing integration tests that establish the expected artifact set and prove the preview entry point does not depend on a slicer root.
- **Patterns to follow:** generate_package() for deterministic directory handling and manifest convention; normalize_image() for source retention; write_braille_artifacts() and create_visual_preview() for artifact formats.
- **Test scenarios:** A valid SVG/sample card produces all required preview artifacts and an explicitly unreviewed/non-print manifest; a 600 by 600 raster image is accepted while a 599 by 600 image is rejected; a raster file over 15 MB is rejected before rendering; unsupported and unreadable files fail clearly; 31-character greetings and 141-character messages fail; preview output contains no G-code, production mesh, or printer-submission fields; identical inputs produce byte-identical preview files.
- **Verification:** The preview-only integration tests pass and require no OrcaSlicer path or printer connection.

### U2. Expose the local-render CLI without changing the full-package command

- **Goal:** Make the preview-only path available from the repository CLI while keeping the established package invocation compatible.
- **Requirements:** R1, R6.
- **Dependencies:** U1.
- **Files:** src/braille_card/__main__.py, README.md, tests/test_preview.py.
- **Approach:** Add an explicit preview-only CLI selection that accepts the existing image/card/output arguments and dispatches only to the new preview entry point. Preserve the current command form as the production-package path, including its optional slicer-root behavior.
- **Execution note:** Add a subprocess-level CLI test before changing argument dispatch so compatibility failures are visible.
- **Patterns to follow:** Current argparse entry point and README invocation style.
- **Test scenarios:** The preview command returns the output directory and creates review artifacts without a slicer root; the existing package command still parses its current flags; invalid preview input exits nonzero with the validation message; preview invocation cannot create card.gcode or invoke the slicer.
- **Verification:** CLI tests prove the two modes are distinguishable and the original full-package invocation remains supported.

### U3. Record the staged workflow boundary and verify regression safety

- **Goal:** Update the project record so future work treats Step 2 as complete while deferring browser, print approval, and hardware observation slices.
- **Requirements:** R2, R3, R6.
- **Dependencies:** U1, U2.
- **Files:** docs/WEBSITE_ACCEPTANCE_MAP.md, HANDOFF.md, scratchpad.md, tests/test_determinism.py.
- **Approach:** Document the preview-only artifact contract and its no-slicer/no-hardware boundary. Keep human Braille/tactile review requirements explicit and leave later workflow stages unchanged.
- **Patterns to follow:** Existing handoff language that distinguishes machine checks from human validation.
- **Test scenarios:** The existing complete-production-package determinism test still passes; the preview determinism test covers its distinct artifact set; the full suite establishes that extraction did not alter production outputs.
- **Verification:** Documentation names the completed local-render boundary, all tests pass, and the working tree contains no generated package output.

---

## Verification Contract

| Scope | Evidence | Done signal |
| --- | --- | --- |
| U1 preview library | pytest -q tests/test_preview.py | Valid, invalid, boundary, artifact, and deterministic-preview scenarios pass without a slicer root. |
| U2 CLI | pytest -q tests/test_preview.py | Preview and existing package CLI routes retain their separate contracts. |
| Regression | pytest -q | Preview tests plus the existing production-package, UEB, geometry, quality, and determinism suite pass. |
| Repository hygiene | git diff --check | No whitespace errors; no generated preview directory is staged. |

---

## Definition of Done

- The repository has a deterministic preview-only CLI and library path that satisfies R1 through R5.
- That path never imports or calls the slicer and produces no production geometry or G-code.
- Valid preview output has the image, visual, tactile, UEB, and review artifacts plus an honest machine-review manifest.
- Boundary and failure cases are covered by focused tests, and the full suite remains green.
- The current full production-package command remains compatible and its established artifacts remain deterministic.
- Documentation records that this completes only website-workflow Step 2; browser, approval, and hardware stages remain deferred.
