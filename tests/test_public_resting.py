from __future__ import annotations

from pathlib import Path

from braille_card.braille import translate


def test_public_resting_page_uses_verified_uncontracted_ueb() -> None:
    page = (Path(__file__).resolve().parents[1] / "public/resting/index.html").read_text(
        encoding="utf-8"
    )

    assert translate("BrailleCard is resting.").unicode in page
    assert "Uncontracted Unified English Braille" in page
    assert "UEB Grade 1 (uncontracted)" not in page
    assert "no printer connection or personal-card data" not in page
    assert "bedtime-illustration.png" in page
    assert "white-space:nowrap" in page
