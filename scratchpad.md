# Implementation scratchpad

## Fixed scope and choices

- This run is offline with respect to the physical printer. It may create a G-code file, but it will not discover, contact, submit to, or start the printer. No code in this repository will implement printer networking.
- The card is a single rigid portrait panel, 127.0 mm × 177.8 mm. The front carries the tactile silhouette, printed greeting, and matching uncontracted UEB. Because a flat card has no inside, the main message is placed on the back face in both print and uncontracted UEB, as explicitly directed by `GOAL.md` and sanctioned by the product spec's back-face note placement.
- The reference subject will be a deterministic, repository-owned, high-contrast heart silhouette so there are no licensing or network-source concerns.
- Human validation remains outside machine completion: no output will be marked Braille-reviewed, tactile-tested, test-printed, or operator-approved.
- The physical card will carry raised Braille on both faces. For single-piece slicing it will be oriented upright on its long edge with generated supports enabled; this preserves raised, correctly oriented back-face dots instead of flattening or recessing them. This is a machine-generated candidate that still requires the operator test print and inspection required by the spec.
- The base panel thickness is 2.0 mm (machine-check tolerance 1.8-2.2 mm), with 0.75 mm domed Braille and 0.8 mm tactile-art relief. The spec does not prescribe a rigid-panel thickness, so this conservative keepsake/postcard value is used for the reference package pending physical calibration.
- Safe edge margin is 6.35 mm (0.25 in). The silhouette and Braille occupy disjoint named regions; the visual text is engraved 0.30 mm so it does not create additional unsupported raised detail.

## Iteration log

iteration 1: read the full product goal and run scope; inventoried the repository and local toolchain; verified Python liblouis 3.29.0 is installed; found no installed slicer yet; recorded the flat-card/back-message and offline-only decisions.
iteration 2: located authoritative independent UEB examples in the Australian Braille Authority 2022 Unicode training manual; downloaded and locally extracted official OrcaSlicer 2.4.2 arm64; verified its shipped SV07 profile specifies 220 × 220 × 250 mm, a 0.4 mm nozzle, SV07 PLA, and a 0.20 mm process; recorded two-sided upright/support and thickness choices.
iteration 3: added the deterministic heart source/normalization pipeline, liblouis UEB Grade 1 translation and wrapping, review/layout artifact generators, and authoritative ABA known-good tests; verified compilation, 2 passing tests, exact source copying, and a 1200 × 1200 bilevel normalized PNG.
