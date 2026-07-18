"""UEB Grade 1 translation and physical-cell layout."""

from __future__ import annotations

from dataclasses import dataclass

import louis

from . import spec

TABLE = "en-ueb-g1.ctb"
REVIEW_STATUS = "not yet human-reviewed"


@dataclass(frozen=True)
class Translation:
    source: str
    brf: str
    unicode: str
    table: str = TABLE
    grade: str = "UEB Grade 1 (uncontracted)"
    review_status: str = REVIEW_STATUS


def translate(source: str) -> Translation:
    """Translate print to uncontracted UEB with the installed liblouis table."""
    if not source or source != source.strip():
        raise ValueError("Braille source must be non-empty and have no outer whitespace")
    tables = [TABLE]
    brf = louis.translateString(tables, source)
    unicode_braille = louis.translateString(
        tables, source, mode=louis.dotsIO | louis.ucBrl
    )
    return Translation(source=source, brf=brf, unicode=unicode_braille)


def cells_for_unicode(text: str) -> list[int | None]:
    """Return six-dot bit masks; spaces become None."""
    cells: list[int | None] = []
    for char in text:
        if char in {" ", "\u2800"}:
            cells.append(None)
        elif "\u2800" <= char <= "\u283f":
            cells.append(ord(char) - 0x2800)
        else:
            raise ValueError(f"Unexpected non-Braille character {char!r}")
    return cells


def wrap_source(source: str, max_cells: int) -> list[Translation]:
    """Greedily wrap at print spaces, measuring each candidate after translation."""
    words = source.split()
    if not words:
        raise ValueError("Source must contain a word")
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(cells_for_unicode(translate(candidate).unicode)) <= max_cells:
            current = candidate
        else:
            if len(cells_for_unicode(translate(current).unicode)) > max_cells:
                raise ValueError(f"Braille word does not fit in {max_cells} cells")
            lines.append(current)
            current = word
    if len(cells_for_unicode(translate(current).unicode)) > max_cells:
        raise ValueError(f"Braille word does not fit in {max_cells} cells")
    lines.append(current)
    return [translate(line) for line in lines]


def dot_centres(
    unicode_text: str, *, origin_x: float, origin_y: float
) -> list[tuple[float, float]]:
    """Lay out one Braille line from the upper-left dot centre."""
    centres: list[tuple[float, float]] = []
    for cell_index, mask in enumerate(cells_for_unicode(unicode_text)):
        if mask is None:
            continue
        cell_x = origin_x + cell_index * spec.BRAILLE_CELL_SPACING
        for dot in range(1, 7):
            if mask & (1 << (dot - 1)):
                column = 0 if dot <= 3 else 1
                row = (dot - 1) % 3
                centres.append(
                    (
                        cell_x + column * spec.BRAILLE_DOT_SPACING,
                        origin_y - row * spec.BRAILLE_DOT_SPACING,
                    )
                )
    return centres

