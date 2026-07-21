# BrailleCard implementation workflow

This workflow keeps public browsing, local generation, and physical-printer
control separate. The current target printer is a Sovol SV07 using the bundled
0.4 mm OrcaSlicer profile.

## 1. Source-derived production geometry — coding task

**Goal:** Replace the fixed reference-heart mesh with deterministic tactile
geometry derived from `normalized_production.png` within the 95 × 95 mm front
art region.

**Inputs:** retained upload, normalized bilevel image, greeting and message.

**Outputs:** source-derived `combined_card.stl`, `combined_card.3mf`, tactile
SVG/preview, and geometry metadata that records feature filtering.

**Safety gate:** Convert through a fixed physical grid and remove or merge
features below the defined printable minimum. Generated geometry must remain a
single manifold solid attached to the base panel; no fixed-heart primitives may
remain in an upload-derived package.

**Tests:** deterministic package bytes; artwork-dependent geometry; source-art
bounds within the art region; minimum feature size; one solid; no collision
with Braille; SV07 build fit.

**Owner:** DeepSeek V4 Pro supplies a bounded implementation proposal; local
integration and automated verification decide whether it is accepted.

## 2. Human production approval — human task

**Goal:** An operator reviews the source-derived visual/tactile artifacts and
the Braille review before creating a production-eligible job.

**Safety gate:** The job must remain `preview_ready` until an explicit per-job
approval records the reviewed job identifier. Preview rendering must never set
this approval.

**Tests:** no slice action before approval; stale or mismatched confirmation is
rejected; the approval audit record is persisted without secrets.

## 3. Offline SV07 slicing — coding task

**Goal:** Produce locally sliced, validated G-code from an approved job.

**Safety gate:** The explicit Slice button is the only route to OrcaSlicer. It
uses the pinned SV07 profile and has no Moonraker/network path.

**Tests:** slice only approved jobs; expected profile/header/build limits;
deterministic G-code; failed slices do not mark a job sliced.

## 4. Moonraker handoff — human task

**Goal:** Transfer an already sliced G-code file to the operator's SV07.

**Safety gate:** Upload and start are two separate, explicit confirmations.
The upload request must set `print=false`; start requires a successfully
uploaded job and a second confirmation matching that job ID. Status querying
remains read-only and is never automatic at preview time.

**Tests:** no credentials in browser/job files; upload does not start a print;
start rejects unsliced/unuploaded/unconfirmed jobs; Moonraker responses are
recorded without tokens; status uses only printer-object queries.

## 5. Public hosting — deferred

**Goal:** Host the public GUI at `braillecard.dorqlabs.com` through Cloudflare.
A separate, narrower static read-only judge demo is already live at that
hostname — see `docs/JUDGE_DEMO_HOSTING.md`. It has no create/review/upload
routes and is not the interactive public GUI this step describes.

**Safety gate:** The public service cannot obtain Moonraker credentials or run
OrcaSlicer. It may create/review jobs and communicate only with a private,
authenticated local production service once that boundary is designed and
approved.

**Tests:** public deployment has no printer-control routes or secrets; local
worker rejects unauthenticated requests; no job can transition to upload/start
through the public UI alone.
