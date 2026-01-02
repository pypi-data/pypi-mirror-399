"""
WoodML Parser
Main parser for WoodML documents
"""

import yaml
from typing import Dict, List, Union, Optional, Any
from dataclasses import dataclass

from .types import (
    WoodMLDocument,
    ResolvedDocument,
    ResolvedPart,
    ResolvedDimensions,
    Part,
    Dimension,
    UnitSystem,
    Project,
    Materials,
    Lumber,
    Hardware,
    SheetGood,
    Formulas,
    Joint,
    JointType,
    CutList,
    AssemblyStep,
    Finishing,
    Tools,
    Dimensions,
    GrainDirection,
)
from .units import parse_dimension, to_inches, format_dimension
from .formulas import evaluate_formula, resolve_formulas, FormulaContext, FormulaValue


# ============================================
# PARSER CLASS
# ============================================

class WoodMLParser:
    """Parser for WoodML documents"""

    def __init__(self):
        self.default_unit = UnitSystem.IMPERIAL
        self.context: Optional[FormulaContext] = None

    def parse(self, source: str) -> WoodMLDocument:
        """Parse a WoodML string into a document"""
        data = yaml.safe_load(source)

        if not data.get("woodml"):
            raise ValueError('Missing required "woodml" version field')

        # Set default units
        if data.get("project", {}).get("units"):
            self.default_unit = UnitSystem(data["project"]["units"])

        return self._parse_document(data)

    def parse_and_resolve(self, source: str) -> ResolvedDocument:
        """Parse and resolve all variables and dimensions"""
        doc = self.parse(source)

        # Resolve formulas
        resolved_variables: Dict[str, FormulaValue] = {}
        if doc.formulas:
            resolved_variables = resolve_formulas(doc.formulas, self.default_unit)

        self.context = FormulaContext(
            variables=resolved_variables,
            default_unit=self.default_unit
        )

        # Resolve parts
        resolved_parts: List[ResolvedPart] = []
        for part in doc.parts:
            resolved_parts.append(self._resolve_part(part))

        return ResolvedDocument(
            woodml=doc.woodml,
            project=doc.project,
            materials=doc.materials,
            resolved_parts=resolved_parts,
            resolved_variables=resolved_variables,
            joinery=doc.joinery,
            assembly=doc.assembly,
            finishing=doc.finishing,
            tools=doc.tools,
            notes=doc.notes,
        )

    def _parse_document(self, data: Dict[str, Any]) -> WoodMLDocument:
        """Parse raw data into a WoodMLDocument"""
        return WoodMLDocument(
            woodml=data.get("woodml", "1.0"),
            project=self._parse_project(data.get("project")),
            imports=data.get("imports", []),
            materials=self._parse_materials(data.get("materials")),
            formulas=self._parse_formulas(data.get("formulas")),
            parts=self._parse_parts(data.get("parts", [])),
            joinery=self._parse_joinery(data.get("joinery", [])),
            cutlist=self._parse_cutlist(data.get("cutlist")),
            assembly=self._parse_assembly(data.get("assembly", [])),
            finishing=self._parse_finishing(data.get("finishing")),
            tools=self._parse_tools(data.get("tools")),
            notes=data.get("notes"),
        )

    def _parse_project(self, data: Optional[Dict]) -> Optional[Project]:
        if not data:
            return None
        return Project(
            name=data.get("name"),
            author=data.get("author"),
            version=data.get("version"),
            units=UnitSystem(data["units"]) if data.get("units") else UnitSystem.IMPERIAL,
            description=data.get("description"),
        )

    def _parse_materials(self, data: Optional[Dict]) -> Optional[Materials]:
        if not data:
            return None
        return Materials(
            lumber=[Lumber(id=l["id"], **{k: v for k, v in l.items() if k != "id"})
                    for l in data.get("lumber", [])],
            hardware=[Hardware(id=h["id"], type=h["type"], **{k: v for k, v in h.items() if k not in ("id", "type")})
                      for h in data.get("hardware", [])],
            sheet_goods=[SheetGood(id=s["id"], type=s["type"], **{k: v for k, v in s.items() if k not in ("id", "type")})
                         for s in data.get("sheet_goods", [])],
        )

    def _parse_formulas(self, data: Optional[Dict]) -> Optional[Formulas]:
        if not data:
            return None
        return Formulas(
            vars=data.get("vars", {}),
            computed=data.get("computed", {}),
            use_library=data.get("use_library", []),
            custom={},  # TODO: Parse custom formulas
        )

    def _parse_parts(self, data: List[Dict]) -> List[Part]:
        parts = []
        for p in data:
            dims = p.get("dimensions", {})
            grain = None
            if p.get("grain"):
                grain = GrainDirection(p["grain"])

            parts.append(Part(
                id=p["id"],
                name=p.get("name"),
                use=p.get("use"),
                params=p.get("params"),
                material=p.get("material"),
                dimensions=Dimensions(
                    length=dims.get("length"),
                    width=dims.get("width"),
                    thickness=dims.get("thickness"),
                    depth=dims.get("depth"),
                ) if dims else None,
                grain=grain,
                quantity=p.get("quantity", 1),
                notes=p.get("notes"),
            ))
        return parts

    def _parse_joinery(self, data: List[Dict]) -> List[Joint]:
        joints = []
        for j in data:
            joints.append(Joint(
                type=JointType(j["type"]),
                parts=j.get("parts"),
                ratio=j.get("ratio"),
                style=j.get("style"),
                width=j.get("width"),
                depth=j.get("depth"),
            ))
        return joints

    def _parse_cutlist(self, data: Optional[Dict]) -> Optional[CutList]:
        if not data:
            return None
        return CutList(
            optimize=data.get("optimize", True),
            kerf=data.get("kerf"),
        )

    def _parse_assembly(self, data: List[Dict]) -> List[AssemblyStep]:
        steps = []
        for s in data:
            steps.append(AssemblyStep(
                step=s.get("step", len(steps) + 1),
                title=s.get("title", ""),
                parts=s.get("parts", []),
                operations=s.get("operations", []),
                tools=s.get("tools", []),
                notes=s.get("notes"),
            ))
        return steps

    def _parse_finishing(self, data: Optional[Dict]) -> Optional[Finishing]:
        if not data:
            return None
        return Finishing(steps=[])  # TODO: Parse finish steps

    def _parse_tools(self, data: Optional[Dict]) -> Optional[Tools]:
        if not data:
            return None
        return Tools(
            required=data.get("required", []),
            optional=data.get("optional", []),
        )

    def _resolve_part(self, part: Part) -> ResolvedPart:
        """Resolve a single part's dimensions"""

        def resolve_dim(value: Optional[str]) -> Dimension:
            if not value:
                return Dimension(value=0, unit=self.default_unit, original="0")

            # Check if it's a formula/variable reference
            if "$" in value or "(" in value:
                result = evaluate_formula(value, self.context)
                if isinstance(result, (int, float)):
                    return Dimension(value=result, unit=self.default_unit, original=value)
                return result

            return parse_dimension(value, self.default_unit)

        dims = part.dimensions or Dimensions()

        return ResolvedPart(
            id=part.id,
            name=part.name,
            material=part.material,
            dimensions=ResolvedDimensions(
                length=resolve_dim(dims.length),
                width=resolve_dim(dims.width or dims.depth),
                thickness=resolve_dim(dims.thickness),
            ),
            grain=part.grain,
            quantity=part.quantity,
            notes=part.notes,
        )

    def get_default_unit(self) -> UnitSystem:
        """Get the default unit system"""
        return self.default_unit


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def parse(source: str) -> WoodMLDocument:
    """Parse a WoodML string"""
    parser = WoodMLParser()
    return parser.parse(source)


def parse_and_resolve(source: str) -> ResolvedDocument:
    """Parse and resolve a WoodML string"""
    parser = WoodMLParser()
    return parser.parse_and_resolve(source)


# ============================================
# VALIDATION
# ============================================

@dataclass
class ValidationError:
    path: str
    message: str
    severity: str  # "error" or "warning"


def validate_document(doc: WoodMLDocument) -> List[ValidationError]:
    """Validate a WoodML document"""
    errors: List[ValidationError] = []

    # Check version
    if not doc.woodml:
        errors.append(ValidationError(
            path="woodml",
            message="Missing required version field",
            severity="error"
        ))

    # Check for duplicate IDs
    ids = set()

    if doc.materials:
        for item in doc.materials.lumber:
            if item.id in ids:
                errors.append(ValidationError(
                    path=f"materials.lumber.{item.id}",
                    message=f"Duplicate ID: {item.id}",
                    severity="error"
                ))
            ids.add(item.id)

        for item in doc.materials.hardware:
            if item.id in ids:
                errors.append(ValidationError(
                    path=f"materials.hardware.{item.id}",
                    message=f"Duplicate ID: {item.id}",
                    severity="error"
                ))
            ids.add(item.id)

        for item in doc.materials.sheet_goods:
            if item.id in ids:
                errors.append(ValidationError(
                    path=f"materials.sheet_goods.{item.id}",
                    message=f"Duplicate ID: {item.id}",
                    severity="error"
                ))
            ids.add(item.id)

    part_ids = set()
    for part in doc.parts:
        if part.id in part_ids:
            errors.append(ValidationError(
                path=f"parts.{part.id}",
                message=f"Duplicate part ID: {part.id}",
                severity="error"
            ))
        part_ids.add(part.id)

        # Validate material references
        if part.material and part.material not in ids:
            errors.append(ValidationError(
                path=f"parts.{part.id}.material",
                message=f"Unknown material reference: {part.material}",
                severity="error"
            ))

    # Validate joinery references
    for i, joint in enumerate(doc.joinery):
        if joint.parts:
            for part_id in joint.parts:
                if part_id not in part_ids:
                    errors.append(ValidationError(
                        path=f"joinery[{i}].parts",
                        message=f"Unknown part reference in joinery: {part_id}",
                        severity="error"
                    ))

    return errors


# ============================================
# UTILITY FUNCTIONS
# ============================================

def calculate_board_feet(doc: ResolvedDocument) -> float:
    """Calculate total board feet for a document"""
    total = 0.0

    for part in doc.resolved_parts:
        length = to_inches(part.dimensions.length)
        width = to_inches(part.dimensions.width)
        thickness = to_inches(part.dimensions.thickness)
        quantity = part.quantity

        bf = (length * width * thickness * quantity) / 144
        total += bf

    return total


@dataclass
class CutListItem:
    part_id: str
    part_name: str
    material: str
    length: str
    width: str
    thickness: str
    quantity: int
    grain: str
    board_feet: float


def generate_cut_list(doc: ResolvedDocument) -> List[CutListItem]:
    """Generate a cut list from a document"""
    items: List[CutListItem] = []

    for part in doc.resolved_parts:
        length = to_inches(part.dimensions.length)
        width = to_inches(part.dimensions.width)
        thickness = to_inches(part.dimensions.thickness)
        bf = (length * width * thickness * part.quantity) / 144

        items.append(CutListItem(
            part_id=part.id,
            part_name=part.name or part.id,
            material=part.material or "unspecified",
            length=format_dimension(part.dimensions.length),
            width=format_dimension(part.dimensions.width),
            thickness=format_dimension(part.dimensions.thickness),
            quantity=part.quantity,
            grain=part.grain.value if part.grain else "any",
            board_feet=round(bf, 2),
        ))

    # Sort by material, then by size (largest first)
    items.sort(key=lambda x: (x.material, -x.board_feet))

    return items


def format_cut_list(items: List[CutListItem]) -> str:
    """Format cut list as a string table"""
    headers = ["Part", "Material", "L", "W", "T", "Qty", "BF"]
    rows = [
        [
            item.part_name,
            item.material,
            item.length,
            item.width,
            item.thickness,
            str(item.quantity),
            f"{item.board_feet:.2f}",
        ]
        for item in items
    ]

    # Calculate column widths
    widths = [
        max(len(h), max((len(row[i]) for row in rows), default=0))
        for i, h in enumerate(headers)
    ]

    # Format output
    def format_row(row: List[str]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

    separator = "-+-".join("-" * w for w in widths)
    total_bf = sum(item.board_feet for item in items)

    lines = [
        format_row(headers),
        separator,
        *[format_row(row) for row in rows],
        separator,
        f"Total Board Feet: {total_bf:.2f}",
    ]

    return "\n".join(lines)
