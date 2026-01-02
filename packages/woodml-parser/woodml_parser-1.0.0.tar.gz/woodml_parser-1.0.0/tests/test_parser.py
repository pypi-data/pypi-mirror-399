"""Unit Tests for WoodML Parser Module"""

import pytest
from woodml.types import (
    WoodMLDocument, UnitSystem, Materials, Lumber, Hardware, Part, Joint, JointType
)
from woodml.parser import (
    WoodMLParser,
    parse,
    parse_and_resolve,
    validate_document,
    calculate_board_feet,
    generate_cut_list,
    format_cut_list,
    ValidationError,
)


SIMPLE_PROJECT = """
woodml: "1.0"
project:
  name: Test Project
  units: imperial

materials:
  lumber:
    - id: walnut
      species: walnut
      thickness: 4/4

parts:
  - id: top
    name: Table Top
    material: walnut
    dimensions:
      length: 48"
      width: 24"
      thickness: 1"
    quantity: 1
"""

PROJECT_WITH_FORMULAS = """
woodml: "1.0"
project:
  name: Formula Test
  units: imperial

formulas:
  vars:
    table_length: 48"
    table_width: 24"
    leg_height: 30"
  computed:
    apron_length: $table_length - 4"
    apron_depth: $leg_height - 1"

parts:
  - id: top
    material: oak
    dimensions:
      length: $table_length
      width: $table_width
      thickness: 1"
  - id: apron
    material: oak
    dimensions:
      length: $apron_length
      width: 4"
      thickness: 3/4"
    quantity: 2
"""

PROJECT_WITH_JOINERY = """
woodml: "1.0"
project:
  name: Joinery Test

materials:
  lumber:
    - id: oak
      species: white_oak

parts:
  - id: leg
    material: oak
    dimensions:
      length: 30"
      width: 2"
      thickness: 2"
    quantity: 4
  - id: apron
    material: oak
    dimensions:
      length: 24"
      width: 4"
      thickness: 3/4"
    quantity: 2

joinery:
  - type: mortise_and_tenon
    parts: [leg, apron]
"""


class TestWoodMLParser:
    class TestParse:
        def test_parse_simple_document(self):
            parser = WoodMLParser()
            doc = parser.parse(SIMPLE_PROJECT)

            assert doc.woodml == "1.0"
            assert doc.project.name == "Test Project"
            assert doc.project.units == UnitSystem.IMPERIAL

        def test_parse_materials(self):
            parser = WoodMLParser()
            doc = parser.parse(SIMPLE_PROJECT)

            assert doc.materials is not None
            assert len(doc.materials.lumber) == 1
            assert doc.materials.lumber[0].id == "walnut"
            assert doc.materials.lumber[0].species == "walnut"

        def test_parse_parts(self):
            parser = WoodMLParser()
            doc = parser.parse(SIMPLE_PROJECT)

            assert len(doc.parts) == 1
            assert doc.parts[0].id == "top"
            assert doc.parts[0].name == "Table Top"

        def test_parse_formulas_section(self):
            parser = WoodMLParser()
            doc = parser.parse(PROJECT_WITH_FORMULAS)

            assert doc.formulas is not None
            assert doc.formulas.vars is not None
            assert doc.formulas.vars["table_length"] == '48"'
            assert doc.formulas.computed is not None
            assert doc.formulas.computed["apron_length"] == '$table_length - 4"'

        def test_parse_joinery(self):
            parser = WoodMLParser()
            doc = parser.parse(PROJECT_WITH_JOINERY)

            assert len(doc.joinery) == 1
            assert doc.joinery[0].type == JointType.MORTISE_AND_TENON
            assert doc.joinery[0].parts == ["leg", "apron"]

        def test_throw_on_missing_version(self):
            parser = WoodMLParser()
            with pytest.raises(ValueError, match='Missing required "woodml" version field'):
                parser.parse("project:\n  name: Test")

        def test_set_default_unit_from_project(self):
            parser = WoodMLParser()
            parser.parse(SIMPLE_PROJECT)
            assert parser.get_default_unit() == UnitSystem.IMPERIAL

    class TestParseAndResolve:
        def test_resolve_part_dimensions(self):
            parser = WoodMLParser()
            resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

            assert len(resolved.resolved_parts) == 1
            top = resolved.resolved_parts[0]
            assert top.dimensions.length.value == 48
            assert top.dimensions.width.value == 24
            assert top.dimensions.thickness.value == 1

        def test_resolve_formula_variables(self):
            parser = WoodMLParser()
            resolved = parser.parse_and_resolve(PROJECT_WITH_FORMULAS)

            assert resolved.resolved_variables is not None
            assert resolved.resolved_variables["table_length"].value == 48
            assert resolved.resolved_variables["apron_length"].value == 44

        def test_use_resolved_variables_in_part_dimensions(self):
            parser = WoodMLParser()
            resolved = parser.parse_and_resolve(PROJECT_WITH_FORMULAS)

            top = next(p for p in resolved.resolved_parts if p.id == "top")
            assert top.dimensions.length.value == 48

            apron = next(p for p in resolved.resolved_parts if p.id == "apron")
            assert apron.dimensions.length.value == 44

        def test_set_resolved_quantity(self):
            parser = WoodMLParser()
            resolved = parser.parse_and_resolve(PROJECT_WITH_FORMULAS)

            apron = next(p for p in resolved.resolved_parts if p.id == "apron")
            assert apron.quantity == 2

        def test_default_quantity_to_1(self):
            parser = WoodMLParser()
            resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

            assert resolved.resolved_parts[0].quantity == 1


class TestValidateDocument:
    def test_pass_valid_document(self):
        parser = WoodMLParser()
        doc = parser.parse(SIMPLE_PROJECT)
        errors = validate_document(doc)

        assert len(errors) == 0

    def test_detect_missing_version(self):
        doc = WoodMLDocument(
            woodml="",
            project=None,
            materials=None,
            parts=[],
            joinery=[],
        )
        errors = validate_document(doc)

        assert any(e.path == "woodml" for e in errors)

    def test_detect_duplicate_lumber_ids(self):
        doc = WoodMLDocument(
            woodml="1.0",
            project=None,
            materials=Materials(
                lumber=[Lumber(id="walnut"), Lumber(id="walnut")],
                hardware=[],
                sheet_goods=[],
            ),
            parts=[],
            joinery=[],
        )
        errors = validate_document(doc)

        assert any("Duplicate ID" in e.message for e in errors)

    def test_detect_duplicate_part_ids(self):
        doc = WoodMLDocument(
            woodml="1.0",
            project=None,
            materials=None,
            parts=[Part(id="top"), Part(id="top")],
            joinery=[],
        )
        errors = validate_document(doc)

        assert any("Duplicate part ID" in e.message for e in errors)

    def test_detect_unknown_material_reference(self):
        doc = WoodMLDocument(
            woodml="1.0",
            project=None,
            materials=Materials(
                lumber=[Lumber(id="oak")],
                hardware=[],
                sheet_goods=[],
            ),
            parts=[Part(id="top", material="walnut")],
            joinery=[],
        )
        errors = validate_document(doc)

        assert any("Unknown material reference" in e.message for e in errors)

    def test_detect_unknown_part_reference_in_joinery(self):
        doc = WoodMLDocument(
            woodml="1.0",
            project=None,
            materials=None,
            parts=[Part(id="leg")],
            joinery=[Joint(type=JointType.MORTISE_AND_TENON, parts=["leg", "missing_part"])],
        )
        errors = validate_document(doc)

        assert any("Unknown part reference in joinery" in e.message for e in errors)

    def test_handle_hardware_and_sheet_goods_duplicate_detection(self):
        doc = WoodMLDocument(
            woodml="1.0",
            project=None,
            materials=Materials(
                lumber=[Lumber(id="shared_id")],
                hardware=[Hardware(id="shared_id", type="screw")],
                sheet_goods=[],
            ),
            parts=[],
            joinery=[],
        )
        errors = validate_document(doc)

        assert any("Duplicate ID" in e.message for e in errors)


class TestCalculateBoardFeet:
    def test_calculate_board_feet_for_single_part(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

        # 48" x 24" x 1" / 144 = 8 board feet
        bf = calculate_board_feet(resolved)
        assert bf == 8

    def test_account_for_quantity(self):
        doc = """
woodml: "1.0"
parts:
  - id: leg
    dimensions:
      length: 30"
      width: 2"
      thickness: 2"
    quantity: 4
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        # 30" x 2" x 2" x 4 / 144 = 3.33 board feet
        bf = calculate_board_feet(resolved)
        assert abs(bf - 3.333) < 0.01

    def test_sum_multiple_parts(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(PROJECT_WITH_FORMULAS)

        bf = calculate_board_feet(resolved)
        # top: 48 x 24 x 1 / 144 = 8
        # aprons: 44 x 4 x 0.75 x 2 / 144 = 1.83
        assert bf > 9.5


class TestGenerateCutList:
    def test_generate_cut_list_items(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

        cut_list = generate_cut_list(resolved)
        assert len(cut_list) == 1
        assert cut_list[0].part_id == "top"
        assert cut_list[0].part_name == "Table Top"

    def test_include_formatted_dimensions(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

        cut_list = generate_cut_list(resolved)
        assert cut_list[0].length == "4'"
        assert cut_list[0].width == "2'"
        assert cut_list[0].thickness == '1"'

    def test_include_material(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

        cut_list = generate_cut_list(resolved)
        assert cut_list[0].material == "walnut"

    def test_include_quantity(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(PROJECT_WITH_FORMULAS)

        cut_list = generate_cut_list(resolved)
        apron = next(c for c in cut_list if c.part_id == "apron")
        assert apron.quantity == 2

    def test_include_board_feet_calculation(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)

        cut_list = generate_cut_list(resolved)
        assert cut_list[0].board_feet == 8

    def test_sort_by_material_then_size(self):
        doc = """
woodml: "1.0"
parts:
  - id: small_oak
    material: oak
    dimensions: { length: 12", width: 6", thickness: 1" }
  - id: big_walnut
    material: walnut
    dimensions: { length: 48", width: 24", thickness: 1" }
  - id: big_oak
    material: oak
    dimensions: { length: 48", width: 24", thickness: 1" }
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        cut_list = generate_cut_list(resolved)
        assert cut_list[0].part_id == "big_oak"
        assert cut_list[1].part_id == "small_oak"
        assert cut_list[2].part_id == "big_walnut"

    def test_handle_missing_material(self):
        doc = """
woodml: "1.0"
parts:
  - id: top
    dimensions: { length: 24", width: 12", thickness: 1" }
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        cut_list = generate_cut_list(resolved)
        assert cut_list[0].material == "unspecified"

    def test_use_part_id_as_name_if_no_name(self):
        doc = """
woodml: "1.0"
parts:
  - id: unnamed_part
    dimensions: { length: 24", width: 12", thickness: 1" }
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        cut_list = generate_cut_list(resolved)
        assert cut_list[0].part_name == "unnamed_part"


class TestFormatCutList:
    def test_format_cut_list_as_table(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)
        cut_list = generate_cut_list(resolved)

        formatted = format_cut_list(cut_list)
        assert "Part" in formatted
        assert "Material" in formatted
        assert "Table Top" in formatted
        assert "walnut" in formatted

    def test_include_total_board_feet(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)
        cut_list = generate_cut_list(resolved)

        formatted = format_cut_list(cut_list)
        assert "Total Board Feet: 8.00" in formatted

    def test_align_columns(self):
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(SIMPLE_PROJECT)
        cut_list = generate_cut_list(resolved)

        formatted = format_cut_list(cut_list)
        lines = formatted.split("\n")

        # All lines should have consistent column separators
        pipe_count = lambda s: s.count("|")
        header_pipes = pipe_count(lines[0])
        # Check data rows have same pipe count
        for line in lines[2:-2]:
            if line.strip():
                assert pipe_count(line) == header_pipes


class TestMetricUnits:
    def test_handle_metric_project(self):
        doc = """
woodml: "1.0"
project:
  units: metric
parts:
  - id: top
    dimensions:
      length: 1200mm
      width: 600mm
      thickness: 25mm
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        top = resolved.resolved_parts[0]
        assert top.dimensions.length.value == 1200
        assert top.dimensions.length.unit == UnitSystem.METRIC


class TestEdgeCases:
    def test_handle_document_with_no_parts(self):
        doc = """
woodml: "1.0"
project:
  name: Empty Project
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        assert len(resolved.resolved_parts) == 0
        assert calculate_board_feet(resolved) == 0
        assert len(generate_cut_list(resolved)) == 0

    def test_handle_parts_with_missing_dimensions(self):
        doc = """
woodml: "1.0"
parts:
  - id: partial
    dimensions:
      length: 24"
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        part = resolved.resolved_parts[0]
        assert part.dimensions.length.value == 24
        assert part.dimensions.width.value == 0
        assert part.dimensions.thickness.value == 0

    def test_handle_depth_as_alias_for_width(self):
        doc = """
woodml: "1.0"
parts:
  - id: box_side
    dimensions:
      length: 24"
      depth: 12"
      thickness: 3/4"
"""
        parser = WoodMLParser()
        resolved = parser.parse_and_resolve(doc)

        part = resolved.resolved_parts[0]
        assert part.dimensions.width.value == 12
