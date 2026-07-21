# Printing and finishing guide

Status: **machine-generated candidate; not test-printed or operator-approved**.

This package targets one upright, long-edge-on-bed, single-piece 76.2 × 101.6
mm PLA card. `card.gcode` was generated offline for the stock OrcaSlicer 2.4.2
Sovol SV07 0.4 mm machine, Sovol SV07 PLA, and 0.20 mm process profiles, with
tree(auto) snug supports and a 5 mm brim. The stock PLA temperatures resolved to
235 °C first-layer / 200 °C normal nozzle and 65 °C bed. No print was submitted.

Operator steps (all remain human actions):

1. Inspect `card.gcode`, layer preview, profile name, temperatures, 220 × 220 ×
   250 mm build limits, upright orientation, support contacts, and brim in a
   trusted local G-code viewer before using it.
2. Confirm the installed nozzle is 0.4 mm, filament is known PLA, the bed is
   clean, and the machine is mechanically ready. Do not print unattended.
3. Run one calibration/test print using the operator's established safe loading
   procedure. Stop for collisions, poor adhesion, excessive vibration, or other
   abnormal behavior.
4. Let the card cool before removal. Remove the brim and supports slowly with
   eye protection, keeping tools away from Braille dots.
5. Deburr and round only the card perimeter. Do not sand, melt, coat, or reshape
   Braille dots before they have been dimensionally inspected.
6. Complete every unchecked item in `QUALITY_CONTROL.md`. A qualified Braille
   reader and tactile-graphics testers must evaluate the physical result.

If supports merge dots, the upright card is unstable, the physical dimensions
fall outside the specified ranges, or any edge remains sharp, do not treat this
package as approved; revise and regenerate after human calibration.
