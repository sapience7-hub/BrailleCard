# Quality-control checklist

Machine checks in `checks.json` passed, but every item below requires a person
and remains deliberately unchecked.

## Before printing

- [ ] User approves the tactile artwork crop, front greeting, and back message.
- [ ] Source print text and UEB transcription are proofread side by side.
- [ ] A qualified Braille reviewer approves the transcription and layout.
- [ ] Operator previews the complete G-code and confirms the intended SV07,
      PLA, 0.4 mm nozzle, 0.20 mm layers, upright orientation, supports, brim,
      temperatures, and bed fit.
- [ ] Operator confirms the printer and work area are safe and ready.

## Test print and finishing

- [ ] Operator performs the first physical SV07 test print; no job has been
      submitted or started by this generator.
- [ ] Card finishes at 76.2 × 101.6 mm and fits the intended small envelope without forcing.
- [ ] Base panel is 1.8–2.2 mm thick away from relief.
- [ ] Braille dot base diameter is 1.5–1.6 mm and height is 0.6–0.9 mm.
- [ ] Within-cell, cell-to-cell, and line-to-line spacing meet the documented
      2.3–2.5 mm, 6.1–7.6 mm, and 10.0–10.2 mm ranges.
- [ ] No Braille dots are merged, missing, flattened, loose, or support-damaged.
- [ ] Supports and brim are removed without gouging either face.
- [ ] No sharp edges, sharp peaks, warping, roughness, excessive flex, cracks,
      or layer separation remain.

## Accessibility validation

- [ ] A qualified Braille reader verifies the physical front and back text,
      orientation, spacing, punctuation, and readability.
- [ ] At least three people evaluate the tactile artwork; at least one is blind or
      has substantial tactile-graphics experience.
- [ ] Testers identify the intended artwork or provide a consistent meaningful description.
- [ ] Feedback and any required geometry/profile revisions are recorded.

## Reproduction gate (deferred)

- [ ] Three consecutive cards are produced with no critical defects using the
      documented settings.
- [ ] Another operator reproduces an approved card from this package.
