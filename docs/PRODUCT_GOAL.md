---
title: Braille Greeting Card Generator — Product Goal
status: in-progress
priority: high
tags:
  - braille
  - accessibility
  - tactile-design
  - greeting-cards
  - embossed-art
  - sv07
---

# Braille Greeting Card Generator

## Goal

Build a simple pipeline that accepts an image and written message, then turns them into an accessible U.S. greeting card with:

- a visually recognizable interpretation of the original image;
- a simplified embossed version of the image that can be explored by touch;
- ordinary printed text for sighted readers;
- correctly translated Unified English Braille (UEB); and
- production files that can be printed, assembled, and reproduced reliably.

The user should not need CAD or Braille expertise. They provide an image, enter their text, approve a preview, and receive a ready-to-make card package.

## MVP product

Use a flat, single-panel construction as the default first version:

- Standard finished card size: 5 × 7 inches, portrait or landscape.
- Construction: one rigid PLA card printed on the SV07—no fold, hinge, or separate tactile insert required.
- Front face: embossed image, visual text, and UEB Braille arranged as one composition.
- Back face: optional signature, short printed note, production mark, or left blank.
- Envelope target: common A7 greeting-card envelope.

The card should feel like a substantial keepsake or accessible postcard. Full-color artwork may be added later through a printed overlay, UV printing, or multi-color production, but color is not required for the MVP.

### Construction modes

1. **Flat card:** one rigid 5 × 7 PLA panel; simplest and most reliable default.
2. **Flexure-fold card:** two panels joined by a calibrated thinner center seam that bends as an integral hinge.
3. **Mechanical-hinge card:** two printed panels joined by interlocking hinge barrels and a removable pin or captured printed pin.

The flexure seam and mechanical hinge must be generated parametrically for the selected material, layer height, print orientation, and clearances. PLA fold life varies, so the system must label flexure-fold cards as tested prototypes until bend-cycle testing establishes a reliable profile. The mechanical hinge is preferred when repeated opening and closing are expected.

## User inputs

### Image

Accept common creative and consumer formats:

- JPG/JPEG for photographs;
- PNG or WebP for raster artwork and transparent images;
- SVG for logos, illustrations, and vector artwork; and
- PDF as an optional import when a design tool exports print-ready artwork.

Retain the original image as the source and visual reference. Create a simplified visual/tactile interpretation instead of treating raw brightness as automatically meaningful relief.

### Text

Allow separate fields for:

- headline or greeting;
- main message;
- sender/signature; and
- optional image caption or tactile description.

The user selects the recipient type: fluent adult reader, beginner/child, or custom. This determines whether contracted or uncontracted UEB is recommended.

### Optional choices

- Card orientation: portrait or landscape.
- Construction: flat, flexure fold, or mechanical hinge.
- Image crop and focal subject.
- Tactile style: silhouette, contour, layered relief, or photo bas-relief.
- Braille placement: below the message, beside the image, or in a dedicated lower region.
- Visual theme, font, colors, and occasion.

## Image-to-tactile conversion

Offer four conversion modes:

1. **Silhouette:** best for people, pets, icons, logos, and simple objects.
2. **Contour:** extracts important boundaries and turns them into raised lines.
3. **Layered relief:** separates foreground, subject, and background into a few tactile heights.
4. **Photo bas-relief:** converts tonal depth into relief, with a warning that complex photos may not be recognizable by touch.

The pipeline should identify the main subject, remove irrelevant background detail, simplify small features, round sharp geometry, and generate a tactile preview. The user must be able to adjust crop, detail level, relief strength, and subject/background separation before export.

## Braille requirements

- Use Unified English Braille (UEB), the current U.S. English Braille code.
- Recommend contracted UEB for fluent adult literary readers.
- Recommend uncontracted UEB for beginners, children, short labels, or when requested.
- Preserve punctuation, capitalization indicators, numbers, and line breaks intentionally.
- Show the source text and Braille translation side by side before approval.
- Require qualified Braille review before commercial or production claims are made.

Use the 2010 ADA dimensional ranges as the physical manufacturing baseline:

- dot base diameter: 1.5–1.6 mm;
- center-to-center spacing between dots in one cell: 2.3–2.5 mm;
- center-to-center spacing between corresponding dots in adjacent cells: 6.1–7.6 mm;
- center-to-center spacing between corresponding dots on adjacent lines: 10.0–10.2 mm; and
- dot height: 0.6–0.9 mm.

Dots must be domed or rounded. The generated geometry must be calibrated for the SV07, PLA, and 0.4 mm nozzle without silently changing the meaning or layout of the Braille.

## Card-generation workflow

1. User uploads an image and enters the card text.
2. System validates file type, image quality, text length, and printable area.
3. System creates the visual layout for the selected flat or two-panel construction.
4. System translates the selected text into UEB.
5. System creates one or more tactile interpretations of the image.
6. User reviews the visual layout, Braille transcription, tactile preview, and card orientation.
7. System checks margins, Braille spacing, relief collisions, minimum feature size, card thickness, sharp edges, hinge geometry, and print-bed fit.
8. System exports the complete production package.
9. Operator prints the complete card or its two hinged panels on the SV07.
10. Operator removes supports if present, installs a hinge pin if required, finishes edges, and inspects the card using the quality checklist.

## Output package

Each approved card receives its own project folder containing:

- print-ready PDF showing the approved single-panel layout;
- original image and normalized production image;
- visual preview PNG;
- Braille source text, UEB transcription, and review status;
- tactile preview image;
- SVG or CAD source for the tactile layer;
- STL and preferably 3MF for slicing;
- approved G-code tied to a documented SV07 printer profile;
- printing and finishing guide;
- quality-control checklist; and
- a manifest recording dimensions, materials, versions, settings, and checksums.

## Quality and safety gates

### Automated checks

- Uploaded file is readable and within supported limits.
- Card layout fits the selected 5 × 7 template and safe margins.
- Braille cells do not collide with artwork, trim, edge finishing, or handling areas.
- Braille geometry remains within the selected dimensional baseline.
- Tactile artwork has no isolated fragments, unsafe sharp peaks, or features too small to print reliably.
- Tactile component fits within the SV07 build area.
- A flexure seam meets the calibrated minimum/maximum thickness and bend-radius rules.
- Mechanical hinge barrels, pin diameter, and clearances pass geometry checks.
- Exported PDF, SVG/CAD, STL/3MF, and G-code are generated successfully.

### Human checks

- User approves the visual image crop and message.
- Source text and UEB transcription are proofread.
- A qualified Braille reader verifies the first production template and any material layout change.
- At least three testers evaluate whether the tactile image is distinguishable; at least one tester should be blind or have substantial experience reading tactile graphics.
- Operator checks for merged or missing dots, sharp edges, warping, roughness, excessive flex, and layer separation.
- Folded variants pass opening, closing, alignment, pinch-point, and hinge-retention checks.

## MVP acceptance criteria

- A nontechnical user can create a card from one supported image and text without using CAD.
- The system produces a complete, named production package from one approval action.
- Printed text and Braille convey the same intended message.
- Braille is correctly oriented, dimensioned, and readable in physical testing.
- The tactile image communicates the main subject or an approved tactile description.
- The finished single-panel card fits a standard A7 envelope.
- Three consecutive cards can be produced with no critical defects using the documented settings.
- Another operator can reproduce an approved card from the saved package.
- A flexure-fold prototype survives the defined bend-cycle test without cracking; a mechanical hinge opens smoothly and retains its pin.

## MVP scope

### Included

- One 5 × 7 card template in portrait and landscape.
- JPG/JPEG, PNG, WebP, and SVG input.
- PDF import if technically straightforward.
- Visual image layout and basic crop controls.
- UEB translation and review screen.
- Silhouette, contour, and simple layered-relief conversion.
- STL/3MF, G-code, layout PDF, preview, manifest, and finishing instructions.
- PLA with a 0.4 mm nozzle on the SV07.
- Flat construction plus experimental flexure-fold and mechanical-hinge templates.

### Deferred

- Automatic guarantee that any photograph will be recognizable by touch.
- Complex multi-person scenes and detailed backgrounds.
- Full-color 3D printing, UV printing, or attached color overlays.
- Production claims for folded or hinged variants before bend-cycle and durability testing.
- Automatic commercial accessibility certification.
- Full-scale production before reader testing and pilot approval.

## Implementation phases

1. **Template:** Produce one manually validated flat 5 × 7 PLA card with visual text, a short UEB message, and a tactile silhouette.
2. **Generator:** Automate image/text input, layout, UEB translation, geometry generation, and project export.
3. **Calibration:** Create the SV07 Braille and tactile-feature calibration coupon and lock an approved printer profile.
4. **Fold options:** Add a seam-thickness calibration strip and mechanical-hinge clearance test, then choose validated parameters.
5. **Validation:** Test with Braille readers and tactile-art users; revise geometry and instructions.
6. **Pilot:** Produce three occasions—birthday, thank-you, and general greeting—across at least three image types and construction modes.
7. **Production:** Add job tracking, batch export, versioning, and repeatable quality records.

## Immediate next milestone

Create one end-to-end reference card using:

- a simple high-contrast image with one main subject;
- a short front greeting and inside message;
- a flat 5 × 7 portrait card template;
- a tactile silhouette or contour image;
- uncontracted UEB for the first calibration example; and
- an SV07 PLA test print using the 0.4 mm nozzle.

Success means the output package is complete, the single card prints and finishes cleanly, the Braille is readable, and testers can identify or meaningfully describe the tactile image.
