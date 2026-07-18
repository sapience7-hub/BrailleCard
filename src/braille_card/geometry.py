"""Deterministic combined card mesh, tactile SVG, and 3MF/STL exporters."""

from __future__ import annotations

import json
import math
import struct
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import spec
from .braille import Translation, dot_centres

Vec3 = tuple[float, float, float]
Triangle = tuple[int, int, int]


@dataclass
class Mesh:
    vertices: list[Vec3] = field(default_factory=list)
    triangles: list[Triangle] = field(default_factory=list)

    def add(self, vertices: list[Vec3], triangles: list[Triangle]) -> None:
        offset = len(self.vertices)
        self.vertices.extend(vertices)
        self.triangles.extend(
            (a + offset, b + offset, c + offset) for a, b, c in triangles
        )

    def add_box(self, bounds: tuple[float, float, float, float, float, float]) -> None:
        x0, y0, z0, x1, y1, z1 = bounds
        vertices = [
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        ]
        triangles = [
            (0, 2, 1), (0, 3, 2),  # bottom
            (4, 5, 6), (4, 6, 7),  # top
            (0, 1, 5), (0, 5, 4),
            (1, 2, 6), (1, 6, 5),
            (2, 3, 7), (2, 7, 6),
            (3, 0, 4), (3, 4, 7),
        ]
        self.add(vertices, triangles)

    def add_bevelled_disc(
        self,
        cx: float,
        cy: float,
        radius: float,
        z0: float,
        z1: float,
        bevel: float,
        segments: int = 64,
    ) -> None:
        """Add a closed disc with an inward top bevel and no point peak."""
        inner = radius - bevel
        vertices: list[Vec3] = []
        for z, r in ((z0, radius), (z1 - bevel, radius), (z1, inner)):
            for index in range(segments):
                angle = 2 * math.pi * index / segments
                vertices.append((cx + r * math.cos(angle), cy + r * math.sin(angle), z))
        bottom_center = len(vertices)
        vertices.append((cx, cy, z0))
        top_center = len(vertices)
        vertices.append((cx, cy, z1))
        triangles: list[Triangle] = []
        for ring in range(2):
            lo = ring * segments
            hi = (ring + 1) * segments
            for index in range(segments):
                nxt = (index + 1) % segments
                triangles.extend(((lo + index, lo + nxt, hi + nxt), (lo + index, hi + nxt, hi + index)))
        for index in range(segments):
            nxt = (index + 1) % segments
            triangles.append((bottom_center, nxt, index))
            triangles.append((top_center, 2 * segments + index, 2 * segments + nxt))
        self.add(vertices, triangles)

    def add_spherical_cap(
        self,
        cx: float,
        cy: float,
        base_z: float,
        diameter: float,
        height: float,
        *,
        downward: bool = False,
        segments: int = 24,
        rings: int = 6,
    ) -> None:
        """Add a closed exact spherical cap with a circular base."""
        a = diameter / 2
        sphere_radius = (a * a + height * height) / (2 * height)
        centre_z = base_z + height - sphere_radius
        angle_base = math.atan2(a, base_z - centre_z)
        vertices: list[Vec3] = []
        for ring in range(rings):
            angle = angle_base * (1 - ring / rings)
            radius = sphere_radius * math.sin(angle)
            z = centre_z + sphere_radius * math.cos(angle)
            for index in range(segments):
                theta = 2 * math.pi * index / segments
                vertices.append((cx + radius * math.cos(theta), cy + radius * math.sin(theta), z))
        apex = len(vertices)
        vertices.append((cx, cy, base_z + height))
        base_center = len(vertices)
        vertices.append((cx, cy, base_z))
        triangles: list[Triangle] = []
        for ring in range(rings - 1):
            lo = ring * segments
            hi = (ring + 1) * segments
            for index in range(segments):
                nxt = (index + 1) % segments
                triangles.extend(((lo + index, lo + nxt, hi + nxt), (lo + index, hi + nxt, hi + index)))
        last = (rings - 1) * segments
        for index in range(segments):
            nxt = (index + 1) % segments
            triangles.append((last + index, last + nxt, apex))
            triangles.append((base_center, nxt, index))
        if downward:
            vertices = [(x, y, 2 * base_z - z) for x, y, z in vertices]
            triangles = [(a_i, c_i, b_i) for a_i, b_i, c_i in triangles]
        self.add(vertices, triangles)

    def bounds(self) -> tuple[float, float, float, float, float, float]:
        xs, ys, zs = zip(*self.vertices)
        return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


# Connected chain of overlapping rounded discs. Values are x, y, radius in mm.
HEART_DISCS = (
    (42.5, 136.0, 25.0),
    (84.5, 136.0, 25.0),
    (63.5, 117.0, 32.0),
    (63.5, 99.0, 24.0),
    (63.5, 85.0, 12.0),
    (63.5, 78.0, 6.0),
)
TACTILE_BEVEL = 0.4


PIXEL_FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
}
PIXEL_SIZE = 0.9
PIXEL_PITCH = 1.05
CHAR_PITCH = 6.3


def _add_pixel_text(
    mesh: Mesh,
    text: str,
    center_x: float,
    bottom_y: float,
    z0: float,
    z1: float,
    *,
    back: bool = False,
) -> None:
    rendered = text.upper()
    width = max(0.0, len(rendered) * CHAR_PITCH - (CHAR_PITCH - 5 * PIXEL_PITCH))
    start_x = center_x - width / 2
    for char_index, char in enumerate(rendered):
        if char == " ":
            continue
        pattern = PIXEL_FONT.get(char)
        if pattern is None:
            raise ValueError(f"Unsupported visual-text character: {char!r}")
        for row, line in enumerate(pattern):
            for col, filled in enumerate(line):
                if filled != "1":
                    continue
                x0 = start_x + char_index * CHAR_PITCH + col * PIXEL_PITCH
                y0 = bottom_y + (6 - row) * PIXEL_PITCH
                x1, y1 = x0 + PIXEL_SIZE, y0 + PIXEL_SIZE
                if back:
                    x0, x1 = spec.CARD_WIDTH - x1, spec.CARD_WIDTH - x0
                mesh.add_box((x0, y0, z0, x1, y1, z1))


def build_combined_mesh(
    front_lines: list[Translation], back_lines: list[Translation]
) -> tuple[Mesh, dict[str, object]]:
    mesh = Mesh()
    mesh.add_box((0.0, 0.0, 0.0, spec.CARD_WIDTH, spec.CARD_HEIGHT, spec.PANEL_THICKNESS))

    for cx, cy, radius in HEART_DISCS:
        mesh.add_bevelled_disc(
            cx, cy, radius, spec.PANEL_THICKNESS,
            spec.PANEL_THICKNESS + spec.TACTILE_RELIEF_HEIGHT,
            TACTILE_BEVEL,
        )

    _add_pixel_text(mesh, "WITH LOVE", spec.CARD_WIDTH / 2, 58.0,
                    spec.PANEL_THICKNESS, spec.PANEL_THICKNESS + spec.VISUAL_TEXT_RELIEF_HEIGHT)
    _add_pixel_text(mesh, "YOU MAKE EVERY", spec.CARD_WIDTH / 2, 143.0,
                    0.0, -spec.VISUAL_TEXT_RELIEF_HEIGHT, back=True)
    _add_pixel_text(mesh, "DAY BRIGHT.", spec.CARD_WIDTH / 2, 132.5,
                    0.0, -spec.VISUAL_TEXT_RELIEF_HEIGHT, back=True)

    front_dots: list[tuple[float, float]] = []
    for line_index, line in enumerate(front_lines):
        front_dots.extend(dot_centres(line.unicode, origin_x=14.0,
                                      origin_y=38.0 - line_index * spec.BRAILLE_LINE_SPACING))
    back_dots_layout: list[tuple[float, float]] = []
    for line_index, line in enumerate(back_lines):
        back_dots_layout.extend(dot_centres(line.unicode, origin_x=14.0,
                                            origin_y=104.0 - line_index * spec.BRAILLE_LINE_SPACING))
    for x, y in front_dots:
        mesh.add_spherical_cap(x, y, spec.PANEL_THICKNESS,
                               spec.BRAILLE_DOT_DIAMETER, spec.BRAILLE_DOT_HEIGHT)
    for layout_x, y in back_dots_layout:
        mesh.add_spherical_cap(spec.CARD_WIDTH - layout_x, y, 0.0,
                               spec.BRAILLE_DOT_DIAMETER, spec.BRAILLE_DOT_HEIGHT,
                               downward=True)

    metadata: dict[str, object] = {
        "coordinate_system": "millimetres; front view is +Z; back geometry mirrors X for correct reading when viewed from -Z",
        "panel": {"width_mm": spec.CARD_WIDTH, "height_mm": spec.CARD_HEIGHT, "thickness_mm": spec.PANEL_THICKNESS},
        "braille": {
            "dot_base_diameter_mm": spec.BRAILLE_DOT_DIAMETER,
            "within_cell_spacing_mm": spec.BRAILLE_DOT_SPACING,
            "cell_to_cell_spacing_mm": spec.BRAILLE_CELL_SPACING,
            "line_to_line_spacing_mm": spec.BRAILLE_LINE_SPACING,
            "dot_height_mm": spec.BRAILLE_DOT_HEIGHT,
            "shape": "spherical cap",
            "front_dot_count": len(front_dots),
            "back_dot_count": len(back_dots_layout),
            "front_dot_centres_mm": front_dots,
            "back_layout_dot_centres_mm": back_dots_layout,
        },
        "tactile": {
            "mode": "silhouette",
            "shape": "connected overlapping bevelled discs",
            "discs_mm": HEART_DISCS,
            "relief_height_mm": spec.TACTILE_RELIEF_HEIGHT,
            "edge_bevel_mm": TACTILE_BEVEL,
            "minimum_feature_mm": min(2 * disc[2] for disc in HEART_DISCS),
        },
        "visual_text": {"style": "raised 5x7 pixel lettering", "minimum_stroke_mm": PIXEL_SIZE, "relief_height_mm": spec.VISUAL_TEXT_RELIEF_HEIGHT},
        "mesh_bounds_mm": mesh.bounds(),
        "mesh_vertex_count": len(mesh.vertices),
        "mesh_triangle_count": len(mesh.triangles),
        "slicing_orientation": "rotate +90 degrees about X, then place lowest point on bed; long-edge upright; supports enabled",
    }
    return mesh, metadata


def _normal(a: Vec3, b: Vec3, c: Vec3) -> Vec3:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (0.0, 0.0, 0.0) if length == 0 else (nx / length, ny / length, nz / length)


def write_binary_stl(mesh: Mesh, output: Path) -> None:
    header = b"BRAILLE_GREETING_CARD_STL_V1".ljust(80, b" ")
    with output.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(mesh.triangles)))
        for ia, ib, ic in mesh.triangles:
            a, b, c = mesh.vertices[ia], mesh.vertices[ib], mesh.vertices[ic]
            values = _normal(a, b, c) + a + b + c
            handle.write(struct.pack("<12fH", *values, 0))


def _zip_write(archive: zipfile.ZipFile, name: str, data: str) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    archive.writestr(info, data.encode("utf-8"))


def write_3mf(mesh: Mesh, output: Path) -> None:
    vertices = "\n".join(
        f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in mesh.vertices
    )
    triangles = "\n".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.triangles
    )
    model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
<metadata name="Title">Braille greeting card reference geometry</metadata>
<metadata name="Designer">braille-greeting-card generator 0.1.0</metadata>
<resources><object id="1" type="model"><mesh><vertices>
{vertices}
</vertices><triangles>
{triangles}
</triangles></mesh></object></resources>
<build><item objectid="1"/></build></model>
'''
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>
'''
    relationships = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>
'''
    with zipfile.ZipFile(output, "w") as archive:
        _zip_write(archive, "[Content_Types].xml", content_types)
        _zip_write(archive, "_rels/.rels", relationships)
        _zip_write(archive, "3D/3dmodel.model", model)


def write_tactile_svg(output: Path) -> None:
    circles = "\n".join(
        f'  <circle cx="{cx:.3f}" cy="{spec.CARD_HEIGHT - cy:.3f}" r="{radius:.3f}"/>'
        for cx, cy, radius in HEART_DISCS
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{spec.CARD_WIDTH}mm" height="{spec.CARD_HEIGHT}mm" viewBox="0 0 {spec.CARD_WIDTH} {spec.CARD_HEIGHT}">
<title>Connected heart tactile silhouette source</title>
<g fill="#111111" stroke="none">
{circles}
</g></svg>
'''
    output.write_text(svg, encoding="utf-8", newline="\n")


def write_tactile_preview(output: Path) -> None:
    scale = 5
    image = Image.new("RGB", (round(spec.CARD_WIDTH * scale), round(spec.CARD_HEIGHT * scale)), "#f5f0e6")
    draw = ImageDraw.Draw(image)
    for cx, cy, radius in HEART_DISCS:
        draw.ellipse(
            ((cx - radius) * scale, (spec.CARD_HEIGHT - cy - radius) * scale,
             (cx + radius) * scale, (spec.CARD_HEIGHT - cy + radius) * scale),
            fill="#b04a5a", outline="#6b2330", width=3,
        )
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    draw.text((12, 12), "TACTILE SILHOUETTE — 0.8 mm RAISED, BEVELLED EDGE", fill="#222222", font=font)
    image.save(output, format="PNG", optimize=False)


def write_geometry_outputs(
    front_lines: list[Translation], back_lines: list[Translation], package_dir: Path
) -> dict[str, object]:
    mesh, metadata = build_combined_mesh(front_lines, back_lines)
    write_binary_stl(mesh, package_dir / "combined_card.stl")
    write_3mf(mesh, package_dir / "combined_card.3mf")
    write_tactile_svg(package_dir / "tactile_layer.svg")
    write_tactile_preview(package_dir / "tactile_preview.png")
    (package_dir / "geometry.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return metadata

