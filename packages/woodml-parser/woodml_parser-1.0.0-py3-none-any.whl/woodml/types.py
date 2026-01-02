"""
WoodML Type Definitions
Core types for the WoodML markup language
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal, Union
from enum import Enum


# ============================================
# ENUMS
# ============================================

class UnitSystem(str, Enum):
    IMPERIAL = "imperial"
    METRIC = "metric"


class GrainDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    ANY = "any"


class JointType(str, Enum):
    MORTISE_AND_TENON = "mortise_and_tenon"
    DOVETAIL = "dovetail"
    BOX_JOINT = "box_joint"
    DADO = "dado"
    RABBET = "rabbet"
    GROOVE = "groove"
    TONGUE_AND_GROOVE = "tongue_and_groove"
    BISCUIT = "biscuit"
    DOWEL = "dowel"
    POCKET_HOLE = "pocket_hole"
    MITER = "miter"
    SPLINE = "spline"
    HALF_LAP = "half_lap"
    BRIDLE = "bridle"
    FINGER_JOINT = "finger_joint"
    SCARF = "scarf"
    BUTT = "butt"


# ============================================
# DIMENSION TYPE
# ============================================

@dataclass
class Dimension:
    """Represents a measurement with unit"""
    value: float
    unit: UnitSystem
    original: str

    def __repr__(self) -> str:
        return f"Dimension({self.value}, {self.unit.value}, '{self.original}')"


@dataclass
class FractionalInches:
    """Represents a fractional inch measurement"""
    whole: int
    numerator: int
    denominator: int


# ============================================
# PROJECT TYPES
# ============================================

@dataclass
class Project:
    name: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    units: UnitSystem = UnitSystem.IMPERIAL
    description: Optional[str] = None


# ============================================
# MATERIALS
# ============================================

@dataclass
class Lumber:
    id: str
    species: Optional[str] = None
    thickness: Optional[str] = None
    nominal: Optional[str] = None
    actual: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None
    board_feet: Optional[float] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class Hardware:
    id: str
    type: str
    name: Optional[str] = None
    size: Optional[str] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class SheetGood:
    id: str
    type: str
    thickness: Optional[str] = None
    grade: Optional[str] = None
    size: Optional[str] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class Materials:
    lumber: List[Lumber] = field(default_factory=list)
    hardware: List[Hardware] = field(default_factory=list)
    sheet_goods: List[SheetGood] = field(default_factory=list)


# ============================================
# FORMULAS
# ============================================

@dataclass
class CustomFormula:
    params: List[str]
    formula: str


@dataclass
class Formulas:
    vars: Dict[str, str] = field(default_factory=dict)
    computed: Dict[str, str] = field(default_factory=dict)
    use_library: List[str] = field(default_factory=list)
    custom: Dict[str, CustomFormula] = field(default_factory=dict)


# ============================================
# PARTS
# ============================================

@dataclass
class Dimensions:
    length: Optional[str] = None
    width: Optional[str] = None
    thickness: Optional[str] = None
    depth: Optional[str] = None


@dataclass
class Taper:
    face: Optional[str] = None
    faces: Optional[List[str]] = None
    start: Optional[str] = None
    end_dimension: Optional[str] = None
    taper_per_foot: Optional[str] = None


@dataclass
class Profile:
    edge: Optional[str] = None
    type: str = "ease"
    radius: Optional[str] = None
    size: Optional[str] = None


@dataclass
class Part:
    id: str
    name: Optional[str] = None
    use: Optional[str] = None
    params: Optional[Dict[str, str]] = None
    material: Optional[str] = None
    dimensions: Optional[Dimensions] = None
    grain: Optional[GrainDirection] = None
    quantity: int = 1
    tapers: List[Taper] = field(default_factory=list)
    profiles: List[Profile] = field(default_factory=list)
    notes: Optional[str] = None


# ============================================
# JOINERY
# ============================================

@dataclass
class PositionSpec:
    from_top: Optional[str] = None
    from_bottom: Optional[str] = None
    from_left: Optional[str] = None
    from_right: Optional[str] = None
    from_front: Optional[str] = None
    from_back: Optional[str] = None
    from_outside: Optional[str] = None
    from_inside: Optional[str] = None


@dataclass
class MortiseSpec:
    part: str
    position: Optional[Union[str, PositionSpec]] = None
    dimensions: Optional[Dict[str, str]] = None


@dataclass
class TenonSpec:
    part: str
    position: Optional[Union[str, PositionSpec]] = None
    dimensions: Optional[Dict[str, str]] = None
    shoulder: Optional[Union[str, Dict[str, str]]] = None
    haunch: Optional[Dict[str, str]] = None


@dataclass
class DovetailSpec:
    part: str
    count: Optional[int] = None
    spacing: Optional[str] = None
    half_pin: Optional[str] = None


@dataclass
class Joint:
    type: JointType
    parts: Optional[List[str]] = None
    mortise: Optional[MortiseSpec] = None
    tenon: Optional[TenonSpec] = None
    tails: Optional[DovetailSpec] = None
    pins: Optional[DovetailSpec] = None
    ratio: Optional[str] = None
    style: Optional[str] = None
    housing: Optional[Union[str, Dict[str, Any]]] = None
    insert: Optional[Union[str, Dict[str, Any]]] = None
    connections: Optional[List[List[str]]] = None
    width: Optional[str] = None
    depth: Optional[str] = None
    position: Optional[Union[str, PositionSpec]] = None


# ============================================
# CUT LIST
# ============================================

@dataclass
class CutSpec:
    part: str
    quantity: Optional[int] = None
    grain: Optional[str] = None
    priority: Optional[int] = None


@dataclass
class CutGroup:
    from_material: str
    stock_size: Optional[str] = None
    respect_grain: bool = True
    edge_allowance: Optional[str] = None
    rough_length_add: Optional[str] = None
    rough_width_add: Optional[str] = None
    cuts: List[CutSpec] = field(default_factory=list)


@dataclass
class CutList:
    optimize: bool = True
    kerf: Optional[str] = None
    groups: List[CutGroup] = field(default_factory=list)


# ============================================
# ASSEMBLY
# ============================================

@dataclass
class Subassembly:
    name: str
    parts: List[str]
    clamp_time: Optional[str] = None


@dataclass
class AssemblyStep:
    step: int
    title: str
    parts: List[str] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    subassemblies: List[Subassembly] = field(default_factory=list)


# ============================================
# FINISHING
# ============================================

@dataclass
class FinishStep:
    type: str
    grits: Optional[List[int]] = None
    product: Optional[str] = None
    coats: Optional[int] = None
    dry_time: Optional[str] = None
    sand_between: Optional[Union[int, str]] = None
    notes: Optional[str] = None


@dataclass
class Finishing:
    steps: List[FinishStep] = field(default_factory=list)


# ============================================
# TOOLS
# ============================================

@dataclass
class Tools:
    required: List[Union[str, Dict[str, int]]] = field(default_factory=list)
    optional: List[Union[str, Dict[str, int]]] = field(default_factory=list)


# ============================================
# DOCUMENT
# ============================================

@dataclass
class WoodMLDocument:
    woodml: str
    project: Optional[Project] = None
    imports: List[str] = field(default_factory=list)
    materials: Optional[Materials] = None
    formulas: Optional[Formulas] = None
    parts: List[Part] = field(default_factory=list)
    joinery: List[Joint] = field(default_factory=list)
    cutlist: Optional[CutList] = None
    assembly: List[AssemblyStep] = field(default_factory=list)
    finishing: Optional[Finishing] = None
    tools: Optional[Tools] = None
    notes: Optional[str] = None


# ============================================
# RESOLVED TYPES
# ============================================

@dataclass
class ResolvedDimensions:
    length: Dimension
    width: Dimension
    thickness: Dimension


@dataclass
class ResolvedPart:
    id: str
    name: Optional[str]
    material: Optional[str]
    dimensions: ResolvedDimensions
    grain: Optional[GrainDirection]
    quantity: int
    notes: Optional[str]


@dataclass
class ResolvedDocument:
    woodml: str
    project: Optional[Project]
    materials: Optional[Materials]
    resolved_parts: List[ResolvedPart]
    resolved_variables: Dict[str, Union[Dimension, float]]
    joinery: List[Joint]
    assembly: List[AssemblyStep]
    finishing: Optional[Finishing]
    tools: Optional[Tools]
    notes: Optional[str]
