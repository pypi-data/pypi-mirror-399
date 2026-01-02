"""
WoodML SVG Diagram Generator
Generates visual diagrams of woodworking parts and assemblies
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Literal, Tuple
from enum import Enum
import random
import math

from .types import ResolvedDocument, ResolvedPart, Dimension, GrainDirection


# ============================================
# TYPES
# ============================================

class ColorScheme(str, Enum):
    DEFAULT = "default"
    BLUEPRINT = "blueprint"
    MONOCHROME = "monochrome"


class DiagramType(str, Enum):
    PARTS = "parts"
    EXPLODED = "exploded"
    CUTLIST = "cutlist"


@dataclass
class SVGOptions:
    """Options for SVG generation"""
    width: int = 800
    height: int = 600
    padding: int = 40
    show_dimensions: bool = True
    show_names: bool = True
    show_grain: bool = True
    color_scheme: ColorScheme = ColorScheme.DEFAULT
    scale: float = 10.0  # pixels per inch
    font_size: int = 12


@dataclass
class Rect:
    """A rectangle for layout"""
    x: float
    y: float
    width: float
    height: float


@dataclass
class ColorPalette:
    """Color scheme definition"""
    background: str
    part_fill: str
    part_stroke: str
    dimension_line: str
    dimension_text: str
    name_text: str
    grain_line: str
    joint_highlight: str


# ============================================
# COLOR SCHEMES
# ============================================

COLOR_SCHEMES: Dict[ColorScheme, ColorPalette] = {
    ColorScheme.DEFAULT: ColorPalette(
        background="#ffffff",
        part_fill="#f5deb3",  # Wheat
        part_stroke="#8b4513",  # Saddle brown
        dimension_line="#666666",
        dimension_text="#333333",
        name_text="#000000",
        grain_line="#d2b48c",
        joint_highlight="#ff6b6b",
    ),
    ColorScheme.BLUEPRINT: ColorPalette(
        background="#1a365d",
        part_fill="none",
        part_stroke="#ffffff",
        dimension_line="#90cdf4",
        dimension_text="#e2e8f0",
        name_text="#ffffff",
        grain_line="#4299e1",
        joint_highlight="#fc8181",
    ),
    ColorScheme.MONOCHROME: ColorPalette(
        background="#ffffff",
        part_fill="#f0f0f0",
        part_stroke="#333333",
        dimension_line="#666666",
        dimension_text="#333333",
        name_text="#000000",
        grain_line="#999999",
        joint_highlight="#666666",
    ),
}


# ============================================
# SVG GENERATOR CLASS
# ============================================

class SVGGenerator:
    """Generates SVG diagrams from WoodML documents"""

    def __init__(self, options: Optional[SVGOptions] = None):
        self.options = options or SVGOptions()
        self.colors = COLOR_SCHEMES[self.options.color_scheme]

    def generate_parts_diagram(self, doc: ResolvedDocument) -> str:
        """Generate SVG for all parts in a document"""
        parts = doc.resolved_parts
        if not parts:
            return self._empty_diagram("No parts to display")

        layout = self._calculate_parts_layout(parts)
        elements: List[str] = []

        for part, rect in layout:
            elements.append(self._render_part(part, rect))

        return self._wrap_svg("\n".join(elements), layout)

    def generate_single_part(self, part: ResolvedPart) -> str:
        """Generate SVG for a single part"""
        length_in = part.dimensions.length.value
        width_in = part.dimensions.width.value

        scaled_width = length_in * self.options.scale
        scaled_height = width_in * self.options.scale

        rect = Rect(
            x=self.options.padding,
            y=self.options.padding,
            width=scaled_width,
            height=scaled_height,
        )

        total_width = scaled_width + self.options.padding * 2 + 60
        total_height = scaled_height + self.options.padding * 2 + 60

        elements = [self._render_part(part, rect)]

        return self._wrap_svg("\n".join(elements), None, total_width, total_height)

    def generate_cut_list_diagram(
        self,
        doc: ResolvedDocument,
        stock_width: float = 48,
        stock_height: float = 96,
    ) -> str:
        """Generate a cut list diagram showing part layout on stock"""
        parts = doc.resolved_parts
        if not parts:
            return self._empty_diagram("No parts to display")

        # Sort by area descending
        sorted_parts = sorted(
            parts,
            key=lambda p: p.dimensions.length.value * p.dimensions.width.value * p.quantity,
            reverse=True,
        )

        scale = min(
            (self.options.width - self.options.padding * 2) / stock_width,
            (self.options.height - self.options.padding * 2) / stock_height,
        )

        placements: List[Tuple[ResolvedPart, Rect]] = []
        occupied: List[Rect] = []

        for part in sorted_parts:
            part_length = part.dimensions.length.value
            part_width = part.dimensions.width.value

            for _ in range(part.quantity):
                placement = self._find_placement(
                    part_length * scale,
                    part_width * scale,
                    stock_width * scale,
                    stock_height * scale,
                    occupied,
                )

                if placement:
                    placements.append((
                        part,
                        Rect(
                            x=self.options.padding + placement.x,
                            y=self.options.padding + placement.y,
                            width=part_length * scale,
                            height=part_width * scale,
                        ),
                    ))
                    occupied.append(placement)

        elements: List[str] = []

        # Stock outline
        elements.append(f'''
            <rect
                x="{self.options.padding}"
                y="{self.options.padding}"
                width="{stock_width * scale}"
                height="{stock_height * scale}"
                fill="none"
                stroke="{self.colors.part_stroke}"
                stroke-width="2"
                stroke-dasharray="5,5"
            />
        ''')

        # Parts
        for part, rect in placements:
            elements.append(self._render_cut_part(part, rect))

        # Stock dimensions
        if self.options.show_dimensions:
            elements.append(self._render_dimension_h(
                self.options.padding,
                self.options.padding + stock_height * scale + 20,
                stock_width * scale,
                f'{stock_width}"',
            ))
            elements.append(self._render_dimension_v(
                self.options.padding + stock_width * scale + 20,
                self.options.padding,
                stock_height * scale,
                f'{stock_height}"',
            ))

        return self._wrap_svg(
            "\n".join(elements),
            None,
            stock_width * scale + self.options.padding * 2 + 60,
            stock_height * scale + self.options.padding * 2 + 60,
        )

    def generate_exploded_view(self, doc: ResolvedDocument) -> str:
        """Generate exploded view diagram"""
        parts = doc.resolved_parts
        if not parts:
            return self._empty_diagram("No parts to display")

        elements: List[str] = []
        offset_step = 30
        current_offset = 0

        for part in parts:
            length_in = part.dimensions.length.value
            width_in = part.dimensions.width.value
            thickness_in = part.dimensions.thickness.value

            scale = self.options.scale * 0.8
            scaled_length = length_in * scale
            scaled_width = width_in * scale
            scaled_thickness = thickness_in * scale

            x = self.options.padding + current_offset * 0.5
            y = self.options.padding + current_offset

            elements.append(self._render_3d_part(
                part, x, y, scaled_length, scaled_width, scaled_thickness
            ))

            current_offset += offset_step + scaled_width * 0.3

        return self._wrap_svg("\n".join(elements))

    # ============================================
    # PRIVATE RENDERING METHODS
    # ============================================

    def _render_part(self, part: ResolvedPart, rect: Rect) -> str:
        """Render a single part as SVG"""
        elements: List[str] = []

        # Main rectangle
        elements.append(f'''
            <rect
                x="{rect.x}"
                y="{rect.y}"
                width="{rect.width}"
                height="{rect.height}"
                fill="{self.colors.part_fill}"
                stroke="{self.colors.part_stroke}"
                stroke-width="2"
                rx="2"
            />
        ''')

        # Grain direction
        if self.options.show_grain and part.grain != GrainDirection.ANY:
            grain = part.grain or GrainDirection.LONG
            elements.append(self._render_grain(rect, grain))

        # Part name
        if self.options.show_names:
            name = part.name or part.id
            elements.append(f'''
                <text
                    x="{rect.x + rect.width / 2}"
                    y="{rect.y + rect.height / 2}"
                    font-family="Arial, sans-serif"
                    font-size="{self.options.font_size}"
                    fill="{self.colors.name_text}"
                    text-anchor="middle"
                    dominant-baseline="middle"
                >{self._escape_xml(name)}</text>
            ''')

            # Quantity badge
            if part.quantity > 1:
                elements.append(f'''
                    <circle
                        cx="{rect.x + rect.width - 10}"
                        cy="{rect.y + 10}"
                        r="10"
                        fill="{self.colors.joint_highlight}"
                    />
                    <text
                        x="{rect.x + rect.width - 10}"
                        y="{rect.y + 10}"
                        font-family="Arial, sans-serif"
                        font-size="10"
                        fill="#ffffff"
                        text-anchor="middle"
                        dominant-baseline="middle"
                    >×{part.quantity}</text>
                ''')

        # Dimensions
        if self.options.show_dimensions:
            length_label = part.dimensions.length.original
            width_label = part.dimensions.width.original

            elements.append(self._render_dimension_h(
                rect.x,
                rect.y + rect.height + 15,
                rect.width,
                length_label,
            ))

            elements.append(self._render_dimension_v(
                rect.x + rect.width + 15,
                rect.y,
                rect.height,
                width_label,
            ))

        return f'<g class="part" data-id="{part.id}">{"".join(elements)}</g>'

    def _render_cut_part(self, part: ResolvedPart, rect: Rect) -> str:
        """Render a part for cut list diagram"""
        elements: List[str] = []

        elements.append(f'''
            <rect
                x="{rect.x}"
                y="{rect.y}"
                width="{rect.width}"
                height="{rect.height}"
                fill="{self.colors.part_fill}"
                stroke="{self.colors.part_stroke}"
                stroke-width="1"
            />
        ''')

        name = part.name or part.id
        font_size = min(self.options.font_size, rect.width / 6, rect.height / 3)
        if font_size >= 6:
            elements.append(f'''
                <text
                    x="{rect.x + rect.width / 2}"
                    y="{rect.y + rect.height / 2}"
                    font-family="Arial, sans-serif"
                    font-size="{font_size}"
                    fill="{self.colors.name_text}"
                    text-anchor="middle"
                    dominant-baseline="middle"
                >{self._escape_xml(name)}</text>
            ''')

        return f'<g class="cut-part" data-id="{part.id}">{"".join(elements)}</g>'

    def _render_3d_part(
        self,
        part: ResolvedPart,
        x: float,
        y: float,
        length: float,
        width: float,
        thickness: float,
    ) -> str:
        """Render a 3D-style part"""
        elements: List[str] = []
        iso_angle = 30  # degrees
        offset_x = thickness * math.cos(math.radians(iso_angle))
        offset_y = thickness * math.sin(math.radians(iso_angle))

        # Top face
        top_points = " ".join([
            f"{x},{y}",
            f"{x + length},{y}",
            f"{x + length + offset_x},{y - offset_y}",
            f"{x + offset_x},{y - offset_y}",
        ])

        elements.append(f'''
            <polygon
                points="{top_points}"
                fill="{self.colors.part_fill}"
                stroke="{self.colors.part_stroke}"
                stroke-width="1"
            />
        ''')

        # Front face
        front_points = " ".join([
            f"{x},{y}",
            f"{x + length},{y}",
            f"{x + length},{y + width}",
            f"{x},{y + width}",
        ])

        elements.append(f'''
            <polygon
                points="{front_points}"
                fill="{self._adjust_brightness(self.colors.part_fill, -20)}"
                stroke="{self.colors.part_stroke}"
                stroke-width="1"
            />
        ''')

        # Right face
        right_points = " ".join([
            f"{x + length},{y}",
            f"{x + length + offset_x},{y - offset_y}",
            f"{x + length + offset_x},{y + width - offset_y}",
            f"{x + length},{y + width}",
        ])

        elements.append(f'''
            <polygon
                points="{right_points}"
                fill="{self._adjust_brightness(self.colors.part_fill, -40)}"
                stroke="{self.colors.part_stroke}"
                stroke-width="1"
            />
        ''')

        # Part name
        if self.options.show_names:
            name = part.name or part.id
            elements.append(f'''
                <text
                    x="{x + length / 2}"
                    y="{y + width / 2}"
                    font-family="Arial, sans-serif"
                    font-size="{self.options.font_size}"
                    fill="{self.colors.name_text}"
                    text-anchor="middle"
                    dominant-baseline="middle"
                >{self._escape_xml(name)}</text>
            ''')

        return f'<g class="part-3d" data-id="{part.id}">{"".join(elements)}</g>'

    def _render_grain(self, rect: Rect, direction: GrainDirection) -> str:
        """Render grain direction lines"""
        lines: List[str] = []
        spacing = 8

        if direction == GrainDirection.LONG:
            y = rect.y + spacing
            while y < rect.y + rect.height - spacing:
                wave_amplitude = 2
                path = self._generate_wavy_line(
                    rect.x + 5, y, rect.x + rect.width - 5, y, wave_amplitude
                )
                lines.append(
                    f'<path d="{path}" stroke="{self.colors.grain_line}" '
                    f'fill="none" stroke-width="0.5" opacity="0.5" />'
                )
                y += spacing
        else:
            x = rect.x + spacing
            while x < rect.x + rect.width - spacing:
                wave_amplitude = 2
                path = self._generate_wavy_line(
                    x, rect.y + 5, x, rect.y + rect.height - 5, wave_amplitude
                )
                lines.append(
                    f'<path d="{path}" stroke="{self.colors.grain_line}" '
                    f'fill="none" stroke-width="0.5" opacity="0.5" />'
                )
                x += spacing

        return "\n".join(lines)

    def _generate_wavy_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        amplitude: float,
    ) -> str:
        """Generate a wavy line path"""
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        segments = int(length / 20)

        if segments < 1:
            return f"M{x1},{y1} L{x2},{y2}"

        parts = [f"M{x1},{y1}"]
        for i in range(1, segments + 1):
            t = i / segments
            x = x1 + dx * t
            y = y1 + dy * t
            offset = (amplitude if i % 2 == 0 else -amplitude) * (random.random() * 0.5 + 0.5)

            if abs(dx) > abs(dy):
                parts.append(f"L{x},{y + offset}")
            else:
                parts.append(f"L{x + offset},{y}")

        parts.append(f"L{x2},{y2}")
        return " ".join(parts)

    def _render_dimension_h(
        self,
        x: float,
        y: float,
        width: float,
        label: str,
    ) -> str:
        """Render horizontal dimension line"""
        arrow_size = 6
        return f'''
            <g class="dimension dimension-h">
                <line x1="{x}" y1="{y}" x2="{x + width}" y2="{y}"
                    stroke="{self.colors.dimension_line}" stroke-width="1" />
                <line x1="{x}" y1="{y - 5}" x2="{x}" y2="{y + 5}"
                    stroke="{self.colors.dimension_line}" stroke-width="1" />
                <line x1="{x + width}" y1="{y - 5}" x2="{x + width}" y2="{y + 5}"
                    stroke="{self.colors.dimension_line}" stroke-width="1" />
                <polygon
                    points="{x},{y} {x + arrow_size},{y - 3} {x + arrow_size},{y + 3}"
                    fill="{self.colors.dimension_line}" />
                <polygon
                    points="{x + width},{y} {x + width - arrow_size},{y - 3} {x + width - arrow_size},{y + 3}"
                    fill="{self.colors.dimension_line}" />
                <text
                    x="{x + width / 2}"
                    y="{y + 15}"
                    font-family="Arial, sans-serif"
                    font-size="{self.options.font_size - 2}"
                    fill="{self.colors.dimension_text}"
                    text-anchor="middle"
                >{self._escape_xml(label)}</text>
            </g>
        '''

    def _render_dimension_v(
        self,
        x: float,
        y: float,
        height: float,
        label: str,
    ) -> str:
        """Render vertical dimension line"""
        arrow_size = 6
        return f'''
            <g class="dimension dimension-v">
                <line x1="{x}" y1="{y}" x2="{x}" y2="{y + height}"
                    stroke="{self.colors.dimension_line}" stroke-width="1" />
                <line x1="{x - 5}" y1="{y}" x2="{x + 5}" y2="{y}"
                    stroke="{self.colors.dimension_line}" stroke-width="1" />
                <line x1="{x - 5}" y1="{y + height}" x2="{x + 5}" y2="{y + height}"
                    stroke="{self.colors.dimension_line}" stroke-width="1" />
                <polygon
                    points="{x},{y} {x - 3},{y + arrow_size} {x + 3},{y + arrow_size}"
                    fill="{self.colors.dimension_line}" />
                <polygon
                    points="{x},{y + height} {x - 3},{y + height - arrow_size} {x + 3},{y + height - arrow_size}"
                    fill="{self.colors.dimension_line}" />
                <text
                    x="{x + 15}"
                    y="{y + height / 2}"
                    font-family="Arial, sans-serif"
                    font-size="{self.options.font_size - 2}"
                    fill="{self.colors.dimension_text}"
                    text-anchor="start"
                    dominant-baseline="middle"
                    transform="rotate(90, {x + 15}, {y + height / 2})"
                >{self._escape_xml(label)}</text>
            </g>
        '''

    # ============================================
    # LAYOUT HELPERS
    # ============================================

    def _calculate_parts_layout(
        self,
        parts: List[ResolvedPart],
    ) -> List[Tuple[ResolvedPart, Rect]]:
        """Calculate layout for parts diagram"""
        result: List[Tuple[ResolvedPart, Rect]] = []
        available_width = self.options.width - self.options.padding * 2
        available_height = self.options.height - self.options.padding * 2

        # Find best scale
        max_length = 0.0
        max_width = 0.0

        for part in parts:
            length_in = part.dimensions.length.value
            width_in = part.dimensions.width.value
            max_length = max(max_length, length_in)
            max_width = max(max_width, width_in)

        scale = min(
            (available_width - 100) / max_length if max_length > 0 else self.options.scale,
            (available_height - 100) / max_width if max_width > 0 else self.options.scale,
            self.options.scale,
        )

        # Grid layout
        current_x = float(self.options.padding)
        current_y = float(self.options.padding)
        row_height = 0.0
        gap = 40

        for part in parts:
            length_in = part.dimensions.length.value
            width_in = part.dimensions.width.value
            scaled_length = length_in * scale
            scaled_width = width_in * scale

            # Wrap to next row if needed
            if current_x + scaled_length + gap > self.options.width - self.options.padding:
                current_x = float(self.options.padding)
                current_y += row_height + gap + 30
                row_height = 0.0

            result.append((
                part,
                Rect(
                    x=current_x,
                    y=current_y,
                    width=scaled_length,
                    height=scaled_width,
                ),
            ))

            current_x += scaled_length + gap + 20
            row_height = max(row_height, scaled_width)

        return result

    def _find_placement(
        self,
        width: float,
        height: float,
        stock_width: float,
        stock_height: float,
        occupied: List[Rect],
    ) -> Optional[Rect]:
        """Find placement for a part using first-fit"""
        step = 5

        y = 0.0
        while y <= stock_height - height:
            x = 0.0
            while x <= stock_width - width:
                candidate = Rect(x=x, y=y, width=width, height=height)
                if not self._overlaps_any(candidate, occupied):
                    return candidate
                x += step
            y += step

        return None

    def _overlaps_any(self, rect: Rect, others: List[Rect]) -> bool:
        """Check if rect overlaps any other rect"""
        for other in others:
            if self._overlaps(rect, other):
                return True
        return False

    def _overlaps(self, a: Rect, b: Rect) -> bool:
        """Check if two rects overlap"""
        return not (
            a.x + a.width <= b.x or
            b.x + b.width <= a.x or
            a.y + a.height <= b.y or
            b.y + b.height <= a.y
        )

    # ============================================
    # UTILITY METHODS
    # ============================================

    def _wrap_svg(
        self,
        content: str,
        layout: Optional[List[Tuple[ResolvedPart, Rect]]] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> str:
        """Wrap content in SVG document"""
        w = width if width is not None else self.options.width
        h = height if height is not None else self.options.height

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {w} {h}"
     width="{w}"
     height="{h}">
  <defs>
    <style>
      .part {{ cursor: pointer; }}
      .part:hover rect {{ stroke-width: 3; }}
      .dimension text {{ pointer-events: none; }}
    </style>
  </defs>
  <rect width="100%" height="100%" fill="{self.colors.background}" />
  {content}
</svg>'''

    def _empty_diagram(self, message: str) -> str:
        """Generate an empty diagram with message"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.options.width} {self.options.height}" width="{self.options.width}" height="{self.options.height}">
  <rect width="100%" height="100%" fill="{self.colors.background}" />
  <text x="50%" y="50%" text-anchor="middle" font-family="Arial, sans-serif" fill="{self.colors.name_text}">{self._escape_xml(message)}</text>
</svg>'''

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters"""
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _adjust_brightness(self, hex_color: str, percent: int) -> str:
        """Adjust brightness of a hex color"""
        if hex_color == "none":
            return hex_color

        # Handle named colors
        color_map = {
            "wheat": "#f5deb3",
        }
        hex_color = color_map.get(hex_color.lower(), hex_color)

        # Parse hex
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return f"#{hex_color}"

        num = int(hex_color, 16)
        r = max(0, min(255, ((num >> 16) & 0xFF) + percent))
        g = max(0, min(255, ((num >> 8) & 0xFF) + percent))
        b = max(0, min(255, (num & 0xFF) + percent))

        return f"#{(r << 16 | g << 8 | b):06x}"


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def generate_svg(
    doc: ResolvedDocument,
    diagram_type: DiagramType = DiagramType.PARTS,
    options: Optional[SVGOptions] = None,
) -> str:
    """Generate an SVG diagram for a resolved document"""
    generator = SVGGenerator(options)

    if diagram_type == DiagramType.PARTS:
        return generator.generate_parts_diagram(doc)
    elif diagram_type == DiagramType.EXPLODED:
        return generator.generate_exploded_view(doc)
    elif diagram_type == DiagramType.CUTLIST:
        return generator.generate_cut_list_diagram(doc)
    else:
        return generator.generate_parts_diagram(doc)


def generate_part_svg(
    part: ResolvedPart,
    options: Optional[SVGOptions] = None,
) -> str:
    """Generate an SVG diagram for a single part"""
    generator = SVGGenerator(options)
    return generator.generate_single_part(part)
