"""
WoodML Python Parser
Reference implementation for parsing WoodML files
"""

from .types import (
    Dimension,
    UnitSystem,
    WoodMLDocument,
    Project,
    Materials,
    Lumber,
    Hardware,
    SheetGood,
    Formulas,
    Part,
    Joint,
    CutList,
    AssemblyStep,
    Finishing,
    Tools,
    ResolvedPart,
    ResolvedDocument,
)

from .units import (
    parse_dimension,
    to_inches,
    to_millimeters,
    convert_to,
    format_imperial,
    format_metric,
    format_dimension,
    decimal_to_fraction,
)

from .formulas import (
    create_context,
    evaluate_formula,
    resolve_formulas,
)

from .parser import (
    WoodMLParser,
    parse,
    parse_and_resolve,
    validate_document,
    calculate_board_feet,
    generate_cut_list,
    format_cut_list,
)

from .svg import (
    SVGGenerator,
    SVGOptions,
    ColorScheme,
    DiagramType,
    generate_svg,
    generate_part_svg,
)

from .cost import (
    estimate_cost,
    format_cost_estimate,
    CostEstimate,
    CostEstimateOptions,
    LumberCostItem,
    HardwareCostItem,
    FinishingCostItem,
    DEFAULT_LUMBER_PRICES,
    DEFAULT_HARDWARE_PRICES,
)

__version__ = "1.0.0"
__all__ = [
    # Types
    "Dimension",
    "UnitSystem",
    "WoodMLDocument",
    "Project",
    "Materials",
    "Lumber",
    "Hardware",
    "SheetGood",
    "Formulas",
    "Part",
    "Joint",
    "CutList",
    "AssemblyStep",
    "Finishing",
    "Tools",
    "ResolvedPart",
    "ResolvedDocument",
    # Units
    "parse_dimension",
    "to_inches",
    "to_millimeters",
    "convert_to",
    "format_imperial",
    "format_metric",
    "format_dimension",
    "decimal_to_fraction",
    # Formulas
    "create_context",
    "evaluate_formula",
    "resolve_formulas",
    # Parser
    "WoodMLParser",
    "parse",
    "parse_and_resolve",
    "validate_document",
    "calculate_board_feet",
    "generate_cut_list",
    "format_cut_list",
    # SVG
    "SVGGenerator",
    "SVGOptions",
    "ColorScheme",
    "DiagramType",
    "generate_svg",
    "generate_part_svg",
    # Cost
    "estimate_cost",
    "format_cost_estimate",
    "CostEstimate",
    "CostEstimateOptions",
    "LumberCostItem",
    "HardwareCostItem",
    "FinishingCostItem",
    "DEFAULT_LUMBER_PRICES",
    "DEFAULT_HARDWARE_PRICES",
]
