# Offline stock profile provenance

The reference package is sliced locally with the profiles shipped inside the
official OrcaSlicer 2.4.2 Linux arm64 AppImage. The generator locates these
read-only files beneath the extracted AppImage at run time:

- `resources/profiles/Sovol/machine/Sovol SV07 0.4 nozzle.json`
- `resources/profiles/Sovol/filament/Sovol SV07 PLA.json`
- `resources/profiles/Sovol/process/0.20mm Standard @Sovol SV07.json`

Pinned AppImage SHA-256:
`e1a07275a25f176626c55a5df39e91bc4476d8c28ee4a3192ff758e29dd5c3ba`

Profile SHA-256 values, in the order above:

- `5433a5ab8ff3e31deba7228185c2aca1bc9c97e42a6c8ed1e390df58f8a0eccd`
- `98de4434a4aa6afeda112b3ee621866c57f24ae7a1d7c20b4307a9e541fe5d35`
- `ffc026a9c0db3985928c2291aa9a95bd2fac3e5324c3c6b3deaa45f5f4d07dd2`

The machine profile's printable area is 220 × 220 mm and its printable height
is 250 mm. It specifies the Sovol SV07, one 0.4 mm nozzle, Klipper-flavor
machine G-code, and its stock start/end macros. The PLA profile specifies 0.98
flow ratio, 235/200 °C initial/normal nozzle temperatures, and 65 °C bed. The
process profile uses 0.20 mm layers. The small JSON override beside this file
enables supports and a brim for the upright two-sided card, disables an
irrelevant single-material prime tower, and adds the layer-local `G92 E0`
required by the slicer's relative-extrusion safety check.

No printer address, host, credential, upload command, or print-start capability
is part of this repository or workflow.
