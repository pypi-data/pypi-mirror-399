"""
Cost estimation for WoodML projects.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .parser import ResolvedDocument, ResolvedPart
from .units import to_inches


# Default lumber prices (USD per board foot)
DEFAULT_LUMBER_PRICES: Dict[str, float] = {
    # Softwoods
    "pine": 3.5,
    "spruce": 3.0,
    "fir": 3.5,
    "cedar": 6.0,
    "redwood": 8.0,
    # Domestic hardwoods
    "oak": 6.0,
    "red oak": 6.0,
    "white oak": 8.0,
    "maple": 7.0,
    "hard maple": 8.0,
    "soft maple": 5.5,
    "cherry": 9.0,
    "walnut": 12.0,
    "ash": 5.5,
    "poplar": 4.0,
    "birch": 6.0,
    "hickory": 7.0,
    "beech": 6.0,
    "alder": 5.0,
    # Exotic hardwoods
    "mahogany": 14.0,
    "teak": 25.0,
    "purpleheart": 15.0,
    "padauk": 12.0,
    "wenge": 18.0,
    "zebrawood": 16.0,
    "bubinga": 20.0,
    "ebony": 80.0,
    "rosewood": 50.0,
    # Sheet goods (per square foot for 3/4")
    "plywood": 2.5,
    "baltic birch": 3.5,
    "mdf": 1.5,
    "particleboard": 1.0,
    "melamine": 2.0,
    # Default for unknown materials
    "default": 6.0,
}

# Default hardware prices
DEFAULT_HARDWARE_PRICES: Dict[str, Any] = {
    "screw": {
        "#6": 0.03,
        "#8": 0.04,
        "#10": 0.05,
        "default": 0.04,
    },
    "bolt": {
        '1/4"': 0.15,
        '5/16"': 0.20,
        '3/8"': 0.25,
        '1/2"': 0.35,
        "default": 0.25,
    },
    "nut": {
        '1/4"': 0.05,
        '5/16"': 0.06,
        '3/8"': 0.08,
        '1/2"': 0.10,
        "default": 0.07,
    },
    "washer": {
        '1/4"': 0.03,
        '5/16"': 0.04,
        '3/8"': 0.05,
        '1/2"': 0.06,
        "default": 0.04,
    },
    "hinge": 3.0,
    "drawer_slide": 15.0,
    "knob": 2.5,
    "pull": 4.0,
    "shelf_pin": 0.25,
    "cam_lock": 0.50,
    "dowel": 0.10,
    "biscuit": 0.05,
    "pocket_screw": 0.08,
    "figure_8": 0.75,
    "tabletop_fastener": 0.50,
}


@dataclass
class LumberCostItem:
    """Cost breakdown for a lumber material."""

    material: str
    board_feet: float
    price_per_bf: float
    cost: float
    parts: List[str] = field(default_factory=list)


@dataclass
class HardwareCostItem:
    """Cost breakdown for a hardware item."""

    name: str
    type: str
    size: Optional[str]
    quantity: int
    unit_price: float
    cost: float


@dataclass
class FinishingCostItem:
    """Cost breakdown for a finishing item."""

    product: str
    coverage: float  # sq ft per unit
    units_needed: int
    unit_price: float
    cost: float


@dataclass
class CostEstimate:
    """Complete cost estimate for a project."""

    lumber_items: List[LumberCostItem] = field(default_factory=list)
    lumber_subtotal: float = 0.0
    hardware_items: List[HardwareCostItem] = field(default_factory=list)
    hardware_subtotal: float = 0.0
    finishing_items: List[FinishingCostItem] = field(default_factory=list)
    finishing_subtotal: float = 0.0
    labor_hours: float = 0.0
    labor_rate: float = 0.0
    labor_subtotal: float = 0.0
    total: float = 0.0
    board_feet_total: float = 0.0
    square_feet_total: float = 0.0
    waste_percentage: float = 0.15
    notes: List[str] = field(default_factory=list)


@dataclass
class CostEstimateOptions:
    """Options for cost estimation."""

    lumber_prices: Optional[Dict[str, float]] = None
    hardware_prices: Optional[Dict[str, Any]] = None
    labor_rate: float = 25.0
    waste_percentage: float = 0.15
    include_labor: bool = False
    labor_hours_per_board_foot: float = 0.5
    finish_price_per_sq_ft: Optional[float] = None


def calculate_board_feet(part: ResolvedPart) -> float:
    """Calculate board feet for a part."""
    length = to_inches(part.dimensions["length"])
    width = to_inches(part.dimensions["width"])
    thickness = to_inches(part.dimensions["thickness"])

    # Board feet = (L x W x T) / 144
    return (length * width * thickness) / 144


def calculate_square_feet(part: ResolvedPart) -> float:
    """Calculate square feet for a part (for sheet goods and finishing)."""
    length = to_inches(part.dimensions["length"])
    width = to_inches(part.dimensions["width"])

    return (length * width) / 144


def get_lumber_price(material: str, prices: Dict[str, float]) -> float:
    """Get lumber price for a material."""
    normalized = material.lower().strip()

    # Direct match
    if normalized in prices:
        return prices[normalized]

    # Partial match
    for key, price in prices.items():
        if normalized in key or key in normalized:
            return price

    return prices.get("default", DEFAULT_LUMBER_PRICES["default"])


def estimate_cost(
    doc: ResolvedDocument, options: Optional[CostEstimateOptions] = None
) -> CostEstimate:
    """
    Estimate project cost.

    Args:
        doc: Resolved WoodML document
        options: Cost estimation options

    Returns:
        CostEstimate with breakdown of all costs
    """
    if options is None:
        options = CostEstimateOptions()

    lumber_prices = {**DEFAULT_LUMBER_PRICES, **(options.lumber_prices or {})}
    hardware_prices = {**DEFAULT_HARDWARE_PRICES, **(options.hardware_prices or {})}
    waste_percentage = options.waste_percentage
    labor_rate = options.labor_rate
    labor_hours_per_bf = options.labor_hours_per_board_foot
    include_labor = options.include_labor

    # Group parts by material
    material_groups: Dict[str, Dict[str, Any]] = {}

    total_board_feet = 0.0
    total_square_feet = 0.0

    for part in doc.resolved_parts:
        material = part.material or "default"
        quantity = part.quantity or 1
        bf = calculate_board_feet(part) * quantity
        sf = calculate_square_feet(part) * quantity

        total_board_feet += bf
        total_square_feet += sf

        if material not in material_groups:
            material_groups[material] = {"parts": [], "board_feet": 0.0}

        group = material_groups[material]
        group["parts"].append(part)
        group["board_feet"] += bf

    # Calculate lumber costs
    lumber_items: List[LumberCostItem] = []
    lumber_subtotal = 0.0

    for material, group in material_groups.items():
        price_per_bf = get_lumber_price(material, lumber_prices)
        board_feet_with_waste = group["board_feet"] * (1 + waste_percentage)
        cost = board_feet_with_waste * price_per_bf

        lumber_items.append(
            LumberCostItem(
                material=material,
                board_feet=group["board_feet"],
                price_per_bf=price_per_bf,
                cost=cost,
                parts=[p.name or p.id for p in group["parts"]],
            )
        )

        lumber_subtotal += cost

    # Calculate hardware costs
    hardware_items: List[HardwareCostItem] = []
    hardware_subtotal = 0.0

    if doc.materials and "hardware" in doc.materials:
        for hw in doc.materials["hardware"]:
            quantity = hw.get("quantity", 1)
            hw_type = hw.get("type", "other")
            hw_size = hw.get("size")
            unit_price = 0.0

            type_price = hardware_prices.get(hw_type)
            if isinstance(type_price, (int, float)):
                unit_price = float(type_price)
            elif isinstance(type_price, dict):
                unit_price = type_price.get(hw_size or "default", type_price.get("default", 1.0))
            else:
                unit_price = 1.0

            cost = quantity * unit_price

            hardware_items.append(
                HardwareCostItem(
                    name=hw.get("name", hw_type),
                    type=hw_type,
                    size=hw_size,
                    quantity=quantity,
                    unit_price=unit_price,
                    cost=cost,
                )
            )

            hardware_subtotal += cost

    # Calculate finishing costs
    finishing_items: List[FinishingCostItem] = []
    finishing_subtotal = 0.0

    if doc.finishing and "steps" in doc.finishing:
        for step in doc.finishing["steps"]:
            step_type = step.get("type", "")
            if step_type in ("stain", "oil", "topcoat", "wax", "other"):
                coverage = 300  # sq ft per gallon (approximate)
                coats = step.get("coats", 1)
                total_coverage = total_square_feet * 2 * coats  # Both sides
                units_needed = int((total_coverage / coverage) + 0.999)  # ceil
                unit_price = (
                    options.finish_price_per_sq_ft * coverage
                    if options.finish_price_per_sq_ft
                    else 35.0
                )

                cost = units_needed * unit_price

                finishing_items.append(
                    FinishingCostItem(
                        product=step.get("product", step_type),
                        coverage=coverage,
                        units_needed=units_needed,
                        unit_price=unit_price,
                        cost=cost,
                    )
                )

                finishing_subtotal += cost

    # Calculate labor
    labor_hours = total_board_feet * labor_hours_per_bf if include_labor else 0.0
    labor_subtotal = labor_hours * labor_rate

    # Notes
    notes: List[str] = []
    notes.append(f"Prices include {int(waste_percentage * 100)}% waste factor")

    if total_board_feet > 50:
        notes.append("Consider bulk pricing for lumber orders over 50 board feet")

    # Calculate total
    total = lumber_subtotal + hardware_subtotal + finishing_subtotal + labor_subtotal

    return CostEstimate(
        lumber_items=lumber_items,
        lumber_subtotal=round(lumber_subtotal, 2),
        hardware_items=hardware_items,
        hardware_subtotal=round(hardware_subtotal, 2),
        finishing_items=finishing_items,
        finishing_subtotal=round(finishing_subtotal, 2),
        labor_hours=round(labor_hours, 1),
        labor_rate=labor_rate,
        labor_subtotal=round(labor_subtotal, 2),
        total=round(total, 2),
        board_feet_total=round(total_board_feet, 2),
        square_feet_total=round(total_square_feet, 2),
        waste_percentage=waste_percentage,
        notes=notes,
    )


def format_cost_estimate(estimate: CostEstimate) -> str:
    """
    Format cost estimate as a text report.

    Args:
        estimate: CostEstimate object

    Returns:
        Formatted string report
    """
    lines: List[str] = []

    lines.append("=" * 60)
    lines.append("PROJECT COST ESTIMATE")
    lines.append("=" * 60)
    lines.append("")

    # Lumber
    lines.append("LUMBER")
    lines.append("-" * 60)

    for item in estimate.lumber_items:
        lines.append(
            f"  {item.material:<20} {item.board_feet:>8.2f} BF @ ${item.price_per_bf:.2f}/BF = ${item.cost:>8.2f}"
        )

    lines.append("-" * 60)
    lines.append(f"  {'Lumber Subtotal':<44} ${estimate.lumber_subtotal:>8.2f}")
    lines.append("")

    # Hardware
    if estimate.hardware_items:
        lines.append("HARDWARE")
        lines.append("-" * 60)

        for item in estimate.hardware_items:
            name = f"{item.name}{' (' + item.size + ')' if item.size else ''}"
            lines.append(
                f"  {name:<30} {item.quantity:>4} @ ${item.unit_price:.2f} = ${item.cost:>8.2f}"
            )

        lines.append("-" * 60)
        lines.append(f"  {'Hardware Subtotal':<44} ${estimate.hardware_subtotal:>8.2f}")
        lines.append("")

    # Finishing
    if estimate.finishing_items:
        lines.append("FINISHING")
        lines.append("-" * 60)

        for item in estimate.finishing_items:
            lines.append(
                f"  {item.product:<30} {item.units_needed:>4} @ ${item.unit_price:.2f} = ${item.cost:>8.2f}"
            )

        lines.append("-" * 60)
        lines.append(f"  {'Finishing Subtotal':<44} ${estimate.finishing_subtotal:>8.2f}")
        lines.append("")

    # Labor
    if estimate.labor_hours > 0:
        lines.append("LABOR")
        lines.append("-" * 60)
        lines.append(
            f"  {estimate.labor_hours:.1f} hours @ ${estimate.labor_rate:.2f}/hr".ljust(46)
            + f"${estimate.labor_subtotal:>8.2f}"
        )
        lines.append("")

    # Total
    lines.append("=" * 60)
    lines.append(f"  {'TOTAL':<44} ${estimate.total:>8.2f}")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append(f"  Total Board Feet: {estimate.board_feet_total:.2f}")
    lines.append(f"  Total Square Feet: {estimate.square_feet_total:.2f}")
    lines.append(f"  Waste Factor: {int(estimate.waste_percentage * 100)}%")
    lines.append("")

    # Notes
    if estimate.notes:
        lines.append("NOTES")
        for note in estimate.notes:
            lines.append(f"  * {note}")

    return "\n".join(lines)
