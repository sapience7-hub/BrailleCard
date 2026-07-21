---
title: Braille Greeting Card Generator — Website Workflow Acceptance Map
status: planning
created_at: 2026-07-20
version: 1.0.0
tags:
  - braille
  - website-workflow
  - acceptance-map
  - planning
  - safety-gates
---

# Website Workflow Acceptance Map

## Overview & Scope

This document defines the complete functional acceptance map, stage boundaries, and safety gates for the **Braille Greeting Card Generator Website Workflow**. 

Per `GOAL.md` and `HANDOFF.md`, the workflow establishes a staged, verifiable pipeline for generating tactile-photo plaque cards. The system maintains a strict separation between **preview rendering**, **explicit human print authorization**, and **read-only hardware monitoring**.

This document represents **Step 1** of the 5-step website workflow sequence outlined in `HANDOFF.md`. No application code, server processes, or printer connections are authorized or implemented as part of this step.

---

## Workflow Sequence & Slice Architecture

The implementation of this workflow follows a 5-step staged progression:

```
[ Step 1: Acceptance Map (This Document) ]
                   │
                   ▼
[ Step 2: Local Render Slice ] ──► (Deterministic offline CLI/Lib render)
                   │
                   ▼
[ Step 3: Browser Preview Slice ] ──► (Web UI: Upload, Text, Preview & Job Metadata)
                   │
                   ▼
[ Step 4: Operator Print Slice ] ──► (Explicit Approval Gate & Mocked Job States)
                   │
                   ▼
[ Step 5: Hardware Observation Slice ] ──► (Read-only Camera & Telemetry Integration)
```

---

## Detailed Stage Acceptance Criteria

### Stage 1: Upload (Image Input & Normalization)

*Goal: Accept user-provided artwork, validate image properties, and prepare visual/tactile representations.*

* **Supported Inputs**:
  * Formats: PNG, JPG/JPEG, WebP, SVG.
  * Maximum file size: 15 MB.
  * Minimum resolution: 600×600 px for raster images; vector paths for SVG.
* **Validation & Processing**:
  * Verify image contrast and subject clarity.
  * Perform boundary/contour extraction or silhouette segmentation.
  * Retain original raw image unmodified alongside the normalized production asset.
* **Automated Acceptance Checks**:
  * Unreadable or corrupted image files are rejected with clear user error messages.
  * Images exceeding size limits or under minimum resolution display actionable warnings.
  * Extracted tactile vectors fit cleanly within safe card margin boundaries without truncation.
* **Safety & Boundary Gate**:
  * Upload processing runs in memory/temp storage with no external API side-effects.

---

### Stage 2: Short Message & Braille Setup

*Goal: Collect greeting text, translate to uncontracted Unified English Braille (UEB), and format multi-surface layout.*

* **Supported Inputs**:
  * **Front Greeting**: Short title/headline (max 9 characters).
  * **Back Note**: Main message placed on the back face of flat cards (max 27 characters).
  * **Recipient Level**: Beginner / Uncontracted UEB (default for initial release).
* **Processing**:
  * Execute deterministic UEB translation via `liblouis`.
  * Mirror/position text and Braille for proper back-face reading orientation.
  * Construct a side-by-side Latin source vs. UEB transcript verification table.
* **Automated Acceptance Checks**:
  * Character limits strictly enforced; overflow triggers UI inline messaging.
  * Non-standard characters or unsupported symbols flagged prior to translation.
  * UEB output matches authoritative baseline examples.
* **Human Review Gate**:
  * UI explicitly displays: `Status: Not yet human-reviewed` for Braille translation accuracy.

---

### Stage 3: Size Choice & Card Geometry Selection

*Goal: Configure card dimensions, orientation, and physical template parameters.*

* **Supported Choices**:
  * **Primary Format**: 3 × 4 inch (76.2 × 101.6 mm) flat rigid plaque card (Portrait).
  * **Alternative Options**: Small tactile tester tiles (e.g., 3 × 3 inch) for low-cost geometry calibration.
* **Physical Constraints (ADA 2010 Compliant)**:
  * Base card thickness: 2.0 mm flat PLA plaque.
  * Dot base diameter: 1.5–1.6 mm.
  * Dot height: 0.6–0.9 mm.
  * Dot spacing within cell: 2.3–2.5 mm; cell pitch: 6.1–7.6 mm; line pitch: 10.0–10.2 mm.
  * Safe margins: Minimum 5.0 mm printable margin around edges.
* **Automated Acceptance Checks**:
  * Geometry collision detector verifies Braille cells do not overlap tactile relief artwork.
  * All dimensions fall strictly within ADA tolerances and Sovol SV07 build volume (220 × 220 mm).

---

### Stage 4: Rendered Preview & Production Package

*Goal: Generate and present full deterministic card preview artifacts before any print consideration.*

* **Generated Artifact Package**:
  1. `preview.png`: 2D rendered visual overlay of relief image, Latin text, and Braille.
  2. `layout.pdf`: 2-page exact-scale layout document (Front and Back).
  3. `card.stl` / `card.3mf`: Combined single-solid 3D mesh model.
  4. `card.gcode`: Offline-sliced G-code for stock Sovol SV07 (0.4 mm nozzle, PLA).
  5. `manifest.json`: Checksum manifest, settings record, and version tracking.
  6. `QUALITY_CONTROL.md`: Unchecked quality checklist and finishing guide.
* **Preview UI Requirements**:
  * Interactive 2D/3D visualizer showing front/back relief surfaces.
  * Display side-by-side source text and Braille transcription.
  * Display manifest checksums and machine verification status.
* **Automated Acceptance Checks**:
  * Package build passes 100% of automated tests (`pytest` suite: determinism, manifold mesh, margin checks).
  * G-code generated completely offline; zero network requests made.

---

### Stage 5: Explicit Print Approval & Safety Gate

*Goal: Enforce an impassable human approval boundary preventing unauthorized or automated printing.*

* **Hard Safety Boundaries**:
  * **Zero Automatic Execution**: Under no circumstances can a render automatically trigger a print job.
  * **No Direct Network Slicing**: Printer host or Moonraker endpoints are never invoked during preview.
* **Explicit Approval Action**:
  * Interactive modal requiring explicit operator confirmation:
    1. Operator has reviewed visual relief and side-by-side Braille transcription.
    2. Operator confirms printer bed is physically clear and loaded with PLA.
    3. Operator manually clicks **"Approve & Submit Print Job"**.
* **Automated Acceptance Checks**:
  * Job submission endpoint remains strictly disabled / mocked until Stage 4 artifacts are generated and approved.
  * Unapproved jobs cannot be queued or sent to any printing interface.

---

### Stage 6: Camera Observation (Read-Only)

*Goal: Provide live visual inspection of the printer bed without operational control capability.*

* **Interface Specifications**:
  * Read-only WebRTC / MJPEG camera feed embedded in the job view.
  * Frame rate & resolution display (e.g., 1600×1200 @ 25 fps).
* **Boundaries**:
  * **Strict Read-Only Access**: No motion control, temperature override, or emergency stop triggers via camera component.
  * Camera stream failure does not interrupt an active print or block status queries.
* **Automated Acceptance Checks**:
  * Stream connection errors fail gracefully without crashing UI state.
  * Stream URI is configurable and completely isolated from control endpoints.

---

### Stage 7: Job Status & Telemetry

*Goal: Display real-time Moonraker print progress and state transitions.*

* **Monitored Telemetry Fields**:
  * Print Status: `standby` | `heating` | `printing` | `complete` | `error` | `cancelled`.
  * Progress: Extrusion percentage (0 - 100%) and current layer count (e.g., Layer 450 / 889).
  * Temperatures: Actual vs. Target for Nozzle and Bed (read-only query).
  * Estimated time remaining & total elapsed print time.
* **Automated Acceptance Checks**:
  * Telemetry queries rely strictly on read-only Moonraker REST/WebSocket status endpoints (`print_stats`, `virtual_sdcard`).
  * Job completion records final timestamps in job history; browser telemetry never changes heater targets.
  * Any printer disconnect or error transitions UI to a safe `disconnected` / `error` state with full log capture.

---

## Verification Matrix Summary

| Workflow Stage | Primary Artifact / Output | Automated Verification | Human Safety Gate |
| :--- | :--- | :--- | :--- |
| **1. Upload** | Normalized PNG / SVG vector | Format, resolution, margin check | User image selection & crop |
| **2. Message & Braille** | UEB text & side-by-side table | Character set, `liblouis` UEB check | `Not human-reviewed` status warning |
| **3. Size Choice** | Parametric plaque spec | ADA 2010 tolerances, bed fit | 3×4 portrait template |
| **4. Rendered Preview** | PDF, STL, 3MF, G-code, Manifest | 100% `pytest` pass, checksum audit | Review visual & tactile layout |
| **5. Explicit Approval** | Signed Job Authorization Token | UI state gate, mock verification | **Explicit Operator Click Required** |
| **6. Camera** | Read-only stream widget | Stream health & isolation check | Visual bed clearance check |
| **7. Job Status** | Telemetry dashboard | Read-only Moonraker query validation | Post-print physical inspection |

---

## Step 2 completion

The deterministic local-render slice is complete. The CLI preview-only path
accepts one supported image and one greeting/message card JSON, then creates
normalized/visual/tactile/UEB review artifacts without invoking OrcaSlicer,
creating STL/3MF/G-code, starting a browser, or contacting any hardware.

This slice is machine-checked only. Braille review, visual approval, tactile
evaluation, print approval, camera observation, and telemetry remain deferred
to their respective workflow stages.

## Next Steps

Proceed to Step 3: Browser Preview Slice. It must reuse the deterministic
preview artifacts, add upload/message entry and error states, and retain the
separate explicit print-approval boundary.
