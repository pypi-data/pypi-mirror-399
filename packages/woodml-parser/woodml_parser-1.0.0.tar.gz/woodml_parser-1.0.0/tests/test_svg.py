"""
Tests for SVG diagram generation
"""

import pytest
from woodml.types import (
    Dimension,
    UnitSystem,
    GrainDirection,
    ResolvedPart,
    ResolvedDimensions,
    ResolvedDocument,
    Project,
)
from woodml.svg import (
    SVGGenerator,
    SVGOptions,
    ColorScheme,
    DiagramType,
    generate_svg,
    generate_part_svg,
)


# ============================================
# TEST HELPERS
# ============================================

def make_dimension(value: float, original: str) -> Dimension:
    return Dimension(value=value, unit=UnitSystem.IMPERIAL, original=original)


def make_resolved_part(
    id: str,
    length: float,
    width: float,
    thickness: float,
    quantity: int = 1,
    name: str = None,
    grain: GrainDirection = GrainDirection.LONG,
) -> ResolvedPart:
    return ResolvedPart(
        id=id,
        name=name or id,
        material="pine",
        dimensions=ResolvedDimensions(
            length=make_dimension(length, f'{length}"'),
            width=make_dimension(width, f'{width}"'),
            thickness=make_dimension(thickness, f'{thickness}"'),
        ),
        grain=grain,
        quantity=quantity,
        notes=None,
    )


def make_document(parts: list[ResolvedPart]) -> ResolvedDocument:
    return ResolvedDocument(
        woodml="1.0",
        project=Project(name="Test Project", units=UnitSystem.IMPERIAL),
        materials=None,
        resolved_parts=parts,
        resolved_variables={},
        joinery=[],
        assembly=[],
        finishing=None,
        tools=None,
        notes=None,
    )


# ============================================
# SVG GENERATOR TESTS
# ============================================

class TestSVGGeneratorConstructor:
    def test_default_options(self):
        generator = SVGGenerator()
        assert generator.options.width == 800
        assert generator.options.height == 600

    def test_custom_options(self):
        generator = SVGGenerator(SVGOptions(
            width=1200,
            height=800,
            color_scheme=ColorScheme.BLUEPRINT,
        ))
        assert generator.options.width == 1200


class TestGeneratePartsDiagram:
    def test_single_part(self):
        generator = SVGGenerator()
        doc = make_document([make_resolved_part("top", 24, 12, 0.75)])

        svg = generator.generate_parts_diagram(doc)

        assert '<?xml version="1.0"' in svg
        assert "<svg" in svg
        assert "</svg>" in svg
        assert 'data-id="top"' in svg

    def test_multiple_parts(self):
        generator = SVGGenerator()
        doc = make_document([
            make_resolved_part("top", 24, 12, 0.75),
            make_resolved_part("side", 12, 6, 0.75, quantity=2),
            make_resolved_part("bottom", 24, 12, 0.5),
        ])

        svg = generator.generate_parts_diagram(doc)

        assert 'data-id="top"' in svg
        assert 'data-id="side"' in svg
        assert 'data-id="bottom"' in svg

    def test_empty_parts(self):
        generator = SVGGenerator()
        doc = make_document([])

        svg = generator.generate_parts_diagram(doc)

        assert "No parts to display" in svg

    def test_shows_dimensions(self):
        generator = SVGGenerator(SVGOptions(show_dimensions=True))
        doc = make_document([make_resolved_part("panel", 36, 18, 0.75)])

        svg = generator.generate_parts_diagram(doc)

        # Quotes are escaped in SVG
        assert '36&quot;' in svg
        assert '18&quot;' in svg

    def test_shows_part_names(self):
        generator = SVGGenerator(SVGOptions(show_names=True))
        doc = make_document([
            make_resolved_part("side_panel", 24, 12, 0.75, name="Side Panel")
        ])

        svg = generator.generate_parts_diagram(doc)

        assert "Side Panel" in svg

    def test_quantity_badge(self):
        generator = SVGGenerator()
        doc = make_document([make_resolved_part("shelf", 30, 10, 0.75, quantity=4)])

        svg = generator.generate_parts_diagram(doc)

        assert "×4" in svg


class TestGenerateSinglePart:
    def test_single_part(self):
        generator = SVGGenerator()
        part = make_resolved_part("door", 30, 20, 0.75)

        svg = generator.generate_single_part(part)

        assert "<svg" in svg
        assert 'data-id="door"' in svg

    def test_with_options(self):
        generator = SVGGenerator(SVGOptions(scale=5))
        part = make_resolved_part("small", 10, 5, 0.5)

        svg = generator.generate_single_part(part)

        assert "<rect" in svg


class TestGenerateCutListDiagram:
    def test_cut_list_layout(self):
        generator = SVGGenerator()
        doc = make_document([
            make_resolved_part("piece1", 24, 6, 0.75),
            make_resolved_part("piece2", 24, 6, 0.75),
            make_resolved_part("piece3", 12, 8, 0.75),
        ])

        svg = generator.generate_cut_list_diagram(doc)

        assert "<svg" in svg
        assert "stroke-dasharray" in svg  # Stock outline

    def test_custom_stock_size(self):
        generator = SVGGenerator()
        doc = make_document([make_resolved_part("panel", 20, 10, 0.75)])

        svg = generator.generate_cut_list_diagram(doc, 24, 48)

        assert "<svg" in svg


class TestGenerateExplodedView:
    def test_exploded_view(self):
        generator = SVGGenerator()
        doc = make_document([
            make_resolved_part("top", 24, 12, 0.75),
            make_resolved_part("side", 12, 12, 0.75, quantity=2),
            make_resolved_part("bottom", 24, 12, 0.5),
        ])

        svg = generator.generate_exploded_view(doc)

        assert "<polygon" in svg  # 3D faces
        assert 'class="part-3d"' in svg


class TestColorSchemes:
    def test_default_colors(self):
        generator = SVGGenerator(SVGOptions(color_scheme=ColorScheme.DEFAULT))
        doc = make_document([make_resolved_part("part", 10, 5, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert "#ffffff" in svg  # White background
        assert "#f5deb3" in svg  # Wheat fill

    def test_blueprint_colors(self):
        generator = SVGGenerator(SVGOptions(color_scheme=ColorScheme.BLUEPRINT))
        doc = make_document([make_resolved_part("part", 10, 5, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert "#1a365d" in svg  # Dark blue background

    def test_monochrome_colors(self):
        generator = SVGGenerator(SVGOptions(color_scheme=ColorScheme.MONOCHROME))
        doc = make_document([make_resolved_part("part", 10, 5, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert "#f0f0f0" in svg  # Light gray fill


class TestGrainDirection:
    def test_long_grain(self):
        generator = SVGGenerator(SVGOptions(show_grain=True))
        doc = make_document([
            make_resolved_part("panel", 24, 12, 0.75, grain=GrainDirection.LONG)
        ])

        svg = generator.generate_parts_diagram(doc)

        assert "<path" in svg  # Grain lines

    def test_any_grain(self):
        generator = SVGGenerator(SVGOptions(show_grain=True))
        doc = make_document([
            make_resolved_part("panel", 24, 12, 0.75, grain=GrainDirection.ANY)
        ])

        svg = generator.generate_parts_diagram(doc)

        assert "<svg" in svg


# ============================================
# CONVENIENCE FUNCTION TESTS
# ============================================

class TestGenerateSVG:
    def test_parts_diagram_default(self):
        doc = make_document([make_resolved_part("test", 12, 6, 0.5)])
        svg = generate_svg(doc)

        assert 'data-id="test"' in svg

    def test_exploded_view(self):
        doc = make_document([make_resolved_part("test", 12, 6, 0.5)])
        svg = generate_svg(doc, DiagramType.EXPLODED)

        assert 'class="part-3d"' in svg

    def test_cutlist_diagram(self):
        doc = make_document([make_resolved_part("test", 12, 6, 0.5)])
        svg = generate_svg(doc, DiagramType.CUTLIST)

        assert "stroke-dasharray" in svg

    def test_with_options(self):
        doc = make_document([make_resolved_part("test", 12, 6, 0.5)])
        svg = generate_svg(doc, DiagramType.PARTS, SVGOptions(color_scheme=ColorScheme.BLUEPRINT))

        assert "#1a365d" in svg


class TestGeneratePartSVG:
    def test_single_part(self):
        part = make_resolved_part("single", 24, 12, 0.75)
        svg = generate_part_svg(part)

        assert "<svg" in svg
        assert 'data-id="single"' in svg


# ============================================
# XML ESCAPING TESTS
# ============================================

class TestXMLEscaping:
    def test_special_characters(self):
        generator = SVGGenerator()
        part = make_resolved_part("test", 12, 6, 0.5, name='Part <A> & "B"')
        doc = make_document([part])

        svg = generator.generate_parts_diagram(doc)

        assert "&lt;" in svg
        assert "&gt;" in svg
        assert "&amp;" in svg
        assert "&quot;" in svg


# ============================================
# DIMENSION RENDERING TESTS
# ============================================

class TestDimensionRendering:
    def test_horizontal_dimensions(self):
        generator = SVGGenerator(SVGOptions(show_dimensions=True))
        doc = make_document([make_resolved_part("part", 20, 10, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert 'class="dimension dimension-h"' in svg
        assert "<polygon" in svg  # Arrow heads

    def test_vertical_dimensions(self):
        generator = SVGGenerator(SVGOptions(show_dimensions=True))
        doc = make_document([make_resolved_part("part", 20, 10, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert 'class="dimension dimension-v"' in svg


# ============================================
# SVG SIZE AND VIEWBOX TESTS
# ============================================

class TestSVGSizeAndViewBox:
    def test_size_attributes(self):
        generator = SVGGenerator(SVGOptions(width=1000, height=700))
        doc = make_document([make_resolved_part("part", 10, 5, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert 'width="1000"' in svg
        assert 'height="700"' in svg
        assert 'viewBox="0 0 1000 700"' in svg

    def test_includes_styles(self):
        generator = SVGGenerator()
        doc = make_document([make_resolved_part("part", 10, 5, 0.5)])

        svg = generator.generate_parts_diagram(doc)

        assert "<defs>" in svg
        assert "<style>" in svg
        assert "</style>" in svg
        assert "</defs>" in svg
