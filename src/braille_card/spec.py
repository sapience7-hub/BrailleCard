"""Single-reference-card dimensions and layout constants, in millimetres."""

CARD_WIDTH = 127.0
CARD_HEIGHT = 177.8
PANEL_THICKNESS = 2.0
PANEL_THICKNESS_RANGE = (1.8, 2.2)
SAFE_MARGIN = 6.35

BRAILLE_DOT_DIAMETER = 1.55
BRAILLE_DOT_SPACING = 2.4
BRAILLE_CELL_SPACING = 6.4
BRAILLE_LINE_SPACING = 10.1
BRAILLE_DOT_HEIGHT = 0.75

ADA_RANGES = {
    "dot_base_diameter_mm": (1.5, 1.6),
    "within_cell_spacing_mm": (2.3, 2.5),
    "cell_to_cell_spacing_mm": (6.1, 7.6),
    "line_to_line_spacing_mm": (10.0, 10.2),
    "dot_height_mm": (0.6, 0.9),
}

NOZZLE_DIAMETER = 0.4
MIN_FEATURE_SIZE = 0.8
TACTILE_RELIEF_HEIGHT = 0.8
VISUAL_TEXT_RELIEF_HEIGHT = 0.4

SV07_BUILD_VOLUME = (220.0, 220.0, 250.0)
SV07_PROFILE_NAME = "Sovol SV07 0.4 nozzle"
SV07_FILAMENT_PROFILE = "Sovol SV07 PLA"
SV07_PROCESS_PROFILE = "0.20mm Standard @Sovol SV07"
SV07_PROFILE_BUNDLE_VERSION = "02.04.00.01"
ORCA_SLICER_VERSION = "2.4.2"

# Named rectangles use (left, bottom, right, top) in front-view coordinates.
FRONT_ART_REGION = (16.0, 78.0, 111.0, 166.0)
FRONT_PRINT_REGION = (12.0, 55.0, 115.0, 70.0)
FRONT_BRAILLE_REGION = (12.0, 17.0, 115.0, 45.0)
BACK_PRINT_REGION = (12.0, 126.0, 115.0, 158.0)
BACK_BRAILLE_REGION = (12.0, 77.0, 115.0, 111.0)

