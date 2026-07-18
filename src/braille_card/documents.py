"""Deterministic visual, print-layout, and Braille review artifacts."""

from __future__ import annotations

import html
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from . import spec
from .braille import Translation, dot_centres


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


def _draw_braille_pil(
    draw: ImageDraw.ImageDraw,
    translations: list[Translation],
    origin: tuple[float, float],
    scale: float,
) -> None:
    radius = spec.BRAILLE_DOT_DIAMETER * scale / 2
    for line_index, translation in enumerate(translations):
        line_origin_y = origin[1] - line_index * spec.BRAILLE_LINE_SPACING
        for x, y in dot_centres(
            translation.unicode, origin_x=origin[0], origin_y=line_origin_y
        ):
            pixel_y = (spec.CARD_HEIGHT - y) * scale
            draw.ellipse(
                ((x * scale - radius), (pixel_y - radius),
                 (x * scale + radius), (pixel_y + radius)),
                fill="#111111",
            )


def create_visual_preview(
    normalized_image: Path,
    greeting: str,
    message: str,
    front_lines: list[Translation],
    back_lines: list[Translation],
    output: Path,
) -> None:
    scale = 4
    panel_size = (round(spec.CARD_WIDTH * scale), round(spec.CARD_HEIGHT * scale))
    gap = 48
    preview = Image.new("RGB", (panel_size[0] * 2 + gap, panel_size[1]), "#ece8df")
    front = Image.new("RGB", panel_size, "#fffdf7")
    back = Image.new("RGB", panel_size, "#fffdf7")
    fd = ImageDraw.Draw(front)
    bd = ImageDraw.Draw(back)

    with Image.open(normalized_image) as subject:
        subject = subject.convert("L")
        art_box = spec.FRONT_ART_REGION
        art_size = (round((art_box[2] - art_box[0]) * scale), round((art_box[3] - art_box[1]) * scale))
        subject = ImageOps.contain(subject, art_size, Image.Resampling.NEAREST)
        front.paste(
            Image.merge("RGB", (subject, subject, subject)),
            (round(art_box[0] * scale), round((spec.CARD_HEIGHT - art_box[3]) * scale)),
        )

    def centered(draw: ImageDraw.ImageDraw, text: str, y_mm: float, font: ImageFont.FreeTypeFont) -> None:
        draw.text((panel_size[0] / 2, (spec.CARD_HEIGHT - y_mm) * scale), text, fill="#111111", font=font, anchor="ma")

    centered(fd, greeting, 64.0, _font(34))
    centered(bd, message, 145.0, _font(25))
    _draw_braille_pil(fd, front_lines, (14.0, 38.0), scale)
    _draw_braille_pil(bd, back_lines, (14.0, 104.0), scale)
    fd.rectangle((0, 0, panel_size[0] - 1, panel_size[1] - 1), outline="#333333", width=2)
    bd.rectangle((0, 0, panel_size[0] - 1, panel_size[1] - 1), outline="#333333", width=2)
    preview.paste(front, (0, 0))
    preview.paste(back, (panel_size[0] + gap, 0))
    pd = ImageDraw.Draw(preview)
    pd.text((12, 12), "FRONT", fill="#555555", font=_font(18))
    pd.text((panel_size[0] + gap + 12, 12), "BACK", fill="#555555", font=_font(18))
    preview.save(output, format="PNG", optimize=False)


def _pdf_braille(c: canvas.Canvas, lines: list[Translation], origin_x: float, origin_y: float) -> None:
    c.setFillColor(black)
    radius = spec.BRAILLE_DOT_DIAMETER * mm / 2
    for line_index, translation in enumerate(lines):
        for x, y in dot_centres(
            translation.unicode,
            origin_x=origin_x,
            origin_y=origin_y - line_index * spec.BRAILLE_LINE_SPACING,
        ):
            c.circle(x * mm, y * mm, radius, stroke=0, fill=1)


def create_layout_pdf(
    normalized_image: Path,
    greeting: str,
    message: str,
    front_lines: list[Translation],
    back_lines: list[Translation],
    output: Path,
) -> None:
    c = canvas.Canvas(
        str(output),
        pagesize=(spec.CARD_WIDTH * mm, spec.CARD_HEIGHT * mm),
        pageCompression=1,
        invariant=1,
    )
    c.setTitle("Reference Braille greeting card — print layout")
    stable_image = ImageReader(io.BytesIO(normalized_image.read_bytes()))
    for face in ("FRONT", "BACK"):
        c.setFillColor(white)
        c.rect(0, 0, spec.CARD_WIDTH * mm, spec.CARD_HEIGHT * mm, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#999999"))
        c.rect(0.25 * mm, 0.25 * mm, (spec.CARD_WIDTH - 0.5) * mm, (spec.CARD_HEIGHT - 0.5) * mm, stroke=1, fill=0)
        c.setFont("Helvetica", 7)
        c.setFillColor(HexColor("#666666"))
        c.drawString(3 * mm, 3 * mm, face)
        if face == "FRONT":
            box = spec.FRONT_ART_REGION
            c.drawImage(
                stable_image, box[0] * mm, box[1] * mm,
                width=(box[2] - box[0]) * mm, height=(box[3] - box[1]) * mm,
                preserveAspectRatio=True, anchor="c", mask="auto",
            )
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(spec.CARD_WIDTH * mm / 2, 61 * mm, greeting)
            _pdf_braille(c, front_lines, 14.0, 38.0)
        else:
            c.setFillColor(black)
            c.setFont("Helvetica", 15)
            c.drawCentredString(spec.CARD_WIDTH * mm / 2, 144 * mm, message)
            _pdf_braille(c, back_lines, 14.0, 104.0)
        c.showPage()
    c.save()


def write_braille_artifacts(
    greeting: Translation,
    message: Translation,
    front_lines: list[Translation],
    back_lines: list[Translation],
    package_dir: Path,
) -> None:
    source_text = f"front greeting: {greeting.source}\nback message: {message.source}\n"
    (package_dir / "braille_source.txt").write_text(source_text, encoding="utf-8", newline="\n")
    (package_dir / "braille_ueb.brf").write_text(
        f"front: {greeting.brf}\nback: {message.brf}\n", encoding="ascii", newline="\n"
    )
    (package_dir / "braille_ueb_unicode.txt").write_text(
        f"front: {greeting.unicode}\nback: {message.unicode}\n", encoding="utf-8", newline="\n"
    )
    payload = {
        "grade": greeting.grade,
        "liblouis_table": greeting.table,
        "review_status": greeting.review_status,
        "faces": {
            "front": {"source": greeting.source, "brf": greeting.brf, "unicode": greeting.unicode, "wrapped_unicode": [line.unicode for line in front_lines]},
            "back": {"source": message.source, "brf": message.brf, "unicode": message.unicode, "wrapped_unicode": [line.unicode for line in back_lines]},
        },
    }
    (package_dir / "braille.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    rows = []
    for face, item in (("Front greeting", greeting), ("Back message", message)):
        rows.append(
            f"<tr><th scope=\"row\">{face}</th><td>{html.escape(item.source)}</td>"
            f"<td class=\"braille\" lang=\"en\">{item.unicode}</td><td><code>{html.escape(item.brf)}</code></td></tr>"
        )
    review = """<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Braille transcription review</title>
<style>body{font:16px sans-serif;max-width:70rem;margin:2rem auto;padding:0 1rem}table{border-collapse:collapse;width:100%}th,td{border:1px solid #777;padding:.75rem;text-align:left}.braille{font-size:2rem;letter-spacing:.08em}.status{border:3px solid #9a6700;padding:1rem;background:#fff8c5}</style>
<h1>Source / UEB side-by-side review</h1>
<p class="status"><strong>Status:</strong> not yet human-reviewed. A qualified Braille reviewer must approve this transcription and physical layout before any production claim.</p>
<p>Translation: UEB Grade 1 (uncontracted), liblouis table <code>en-ueb-g1.ctb</code>.</p>
<table><thead><tr><th>Placement</th><th>Print source</th><th>Unicode Braille</th><th>BRF</th></tr></thead><tbody>
""" + "\n".join(rows) + "\n</tbody></table></html>\n"
    (package_dir / "braille_review.html").write_text(review, encoding="utf-8", newline="\n")
