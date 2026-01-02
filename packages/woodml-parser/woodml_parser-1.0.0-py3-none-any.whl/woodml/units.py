"""
WoodML Unit Parsing and Conversion
Handles imperial (fractional inches) and metric measurements
"""

import re
from math import gcd
from typing import Optional, Tuple
from .types import Dimension, FractionalInches, UnitSystem


# ============================================
# CONSTANTS
# ============================================

INCHES_PER_FOOT = 12
MM_PER_INCH = 25.4
MM_PER_CM = 10
MM_PER_METER = 1000

# Common denominators for fractions (must be powers of 2)
VALID_DENOMINATORS = [2, 4, 8, 16, 32, 64]

# Dimensional lumber actual sizes
DIMENSIONAL_LUMBER = {
    "1x2": (1.5, 0.75),
    "1x3": (2.5, 0.75),
    "1x4": (3.5, 0.75),
    "1x6": (5.5, 0.75),
    "1x8": (7.25, 0.75),
    "1x10": (9.25, 0.75),
    "1x12": (11.25, 0.75),
    "2x2": (1.5, 1.5),
    "2x3": (2.5, 1.5),
    "2x4": (3.5, 1.5),
    "2x6": (5.5, 1.5),
    "2x8": (7.25, 1.5),
    "2x10": (9.25, 1.5),
    "2x12": (11.25, 1.5),
    "4x4": (3.5, 3.5),
    "4x6": (5.5, 3.5),
    "6x6": (5.5, 5.5),
}


# ============================================
# PARSING PATTERNS
# ============================================

PATTERNS = {
    "whole_inches": re.compile(r'^(\d+)"$'),
    "fractional_inches": re.compile(r'^(\d+)/(\d+)"$'),
    "mixed_inches": re.compile(r'^(\d+)-(\d+)/(\d+)"$'),
    "feet_only": re.compile(r"^(\d+)'$"),
    "feet_and_inches": re.compile(r'^(\d+)\'(\d+)"$'),
    "feet_and_mixed": re.compile(r'^(\d+)\'(\d+)-(\d+)/(\d+)"$'),
    "quarter_notation": re.compile(r"^(\d+)/4$"),
    "millimeters": re.compile(r"^(\d+(?:\.\d+)?)mm$", re.IGNORECASE),
    "centimeters": re.compile(r"^(\d+(?:\.\d+)?)cm$", re.IGNORECASE),
    "meters": re.compile(r"^(\d+(?:\.\d+)?)m$", re.IGNORECASE),
    "variable": re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)$"),
    "dimensional_lumber": re.compile(r"^(\d+)x(\d+)$"),
}


# ============================================
# PARSING FUNCTIONS
# ============================================

def parse_dimension(input_str: str, default_unit: UnitSystem = UnitSystem.IMPERIAL) -> Dimension:
    """Parse a dimension string into a Dimension object"""
    trimmed = input_str.strip()

    # Whole inches: 24"
    match = PATTERNS["whole_inches"].match(trimmed)
    if match:
        return Dimension(
            value=int(match.group(1)),
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Fractional inches: 3/4"
    match = PATTERNS["fractional_inches"].match(trimmed)
    if match:
        num = int(match.group(1))
        denom = int(match.group(2))
        _validate_denominator(denom)
        return Dimension(
            value=num / denom,
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Mixed inches: 3-1/2"
    match = PATTERNS["mixed_inches"].match(trimmed)
    if match:
        whole = int(match.group(1))
        num = int(match.group(2))
        denom = int(match.group(3))
        _validate_denominator(denom)
        return Dimension(
            value=whole + num / denom,
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Feet only: 6'
    match = PATTERNS["feet_only"].match(trimmed)
    if match:
        return Dimension(
            value=int(match.group(1)) * INCHES_PER_FOOT,
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Feet and inches: 6'4"
    match = PATTERNS["feet_and_inches"].match(trimmed)
    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        return Dimension(
            value=feet * INCHES_PER_FOOT + inches,
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Feet and mixed inches: 6'4-1/2"
    match = PATTERNS["feet_and_mixed"].match(trimmed)
    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        num = int(match.group(3))
        denom = int(match.group(4))
        _validate_denominator(denom)
        return Dimension(
            value=feet * INCHES_PER_FOOT + inches + num / denom,
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Quarter notation: 4/4
    match = PATTERNS["quarter_notation"].match(trimmed)
    if match:
        quarters = int(match.group(1))
        return Dimension(
            value=quarters / 4,
            unit=UnitSystem.IMPERIAL,
            original=trimmed
        )

    # Millimeters: 610mm
    match = PATTERNS["millimeters"].match(trimmed)
    if match:
        return Dimension(
            value=float(match.group(1)),
            unit=UnitSystem.METRIC,
            original=trimmed
        )

    # Centimeters: 61cm
    match = PATTERNS["centimeters"].match(trimmed)
    if match:
        return Dimension(
            value=float(match.group(1)) * MM_PER_CM,
            unit=UnitSystem.METRIC,
            original=trimmed
        )

    # Meters: 2.4m
    match = PATTERNS["meters"].match(trimmed)
    if match:
        return Dimension(
            value=float(match.group(1)) * MM_PER_METER,
            unit=UnitSystem.METRIC,
            original=trimmed
        )

    raise ValueError(f'Invalid dimension format: "{input_str}"')


def _validate_denominator(denom: int) -> None:
    """Validate that denominator is a power of 2"""
    if denom not in VALID_DENOMINATORS:
        raise ValueError(
            f"Invalid fraction denominator: {denom}. "
            f"Must be one of: {', '.join(map(str, VALID_DENOMINATORS))}"
        )


# ============================================
# CONVERSION FUNCTIONS
# ============================================

def to_inches(dim: Dimension) -> float:
    """Convert dimension to inches"""
    if dim.unit == UnitSystem.IMPERIAL:
        return dim.value
    return dim.value / MM_PER_INCH


def to_millimeters(dim: Dimension) -> float:
    """Convert dimension to millimeters"""
    if dim.unit == UnitSystem.METRIC:
        return dim.value
    return dim.value * MM_PER_INCH


def convert_to(dim: Dimension, target_unit: UnitSystem) -> Dimension:
    """Convert dimension to the specified unit system"""
    if dim.unit == target_unit:
        return dim

    if target_unit == UnitSystem.IMPERIAL:
        return Dimension(
            value=to_inches(dim),
            unit=UnitSystem.IMPERIAL,
            original=dim.original
        )
    else:
        return Dimension(
            value=to_millimeters(dim),
            unit=UnitSystem.METRIC,
            original=dim.original
        )


# ============================================
# FORMATTING FUNCTIONS
# ============================================

def decimal_to_fraction(decimal: float, max_denominator: int = 64) -> FractionalInches:
    """Convert decimal inches to fractional representation"""
    whole = int(decimal)
    remainder = decimal - whole

    if remainder < 0.001:
        return FractionalInches(whole=whole, numerator=0, denominator=1)

    # Find closest fraction
    best_numerator = 0
    best_denominator = 1
    best_error = remainder

    for denom in VALID_DENOMINATORS:
        if denom > max_denominator:
            break

        num = round(remainder * denom)
        error = abs(remainder - num / denom)

        if error < best_error:
            best_error = error
            best_numerator = num
            best_denominator = denom

    # Simplify fraction
    common = gcd(best_numerator, best_denominator)
    best_numerator //= common
    best_denominator //= common

    # Handle case where fraction rounds to 1
    if best_numerator == best_denominator:
        return FractionalInches(whole=whole + 1, numerator=0, denominator=1)

    return FractionalInches(
        whole=whole,
        numerator=best_numerator,
        denominator=best_denominator
    )


def format_imperial(dim: Dimension, precision: int = 64) -> str:
    """Format dimension as imperial string"""
    inches = to_inches(dim)

    # Check if we should use feet
    if inches >= 12:
        feet = int(inches // 12)
        remaining_inches = inches % 12

        if remaining_inches < 0.01:
            return f"{feet}'"

        frac = decimal_to_fraction(remaining_inches, precision)
        if frac.numerator == 0:
            return f"{feet}'{frac.whole}\""
        if frac.whole == 0:
            return f"{feet}'{frac.numerator}/{frac.denominator}\""
        return f"{feet}'{frac.whole}-{frac.numerator}/{frac.denominator}\""

    # Format as inches
    frac = decimal_to_fraction(inches, precision)

    if frac.numerator == 0:
        return f'{frac.whole}"'
    if frac.whole == 0:
        return f'{frac.numerator}/{frac.denominator}"'
    return f'{frac.whole}-{frac.numerator}/{frac.denominator}"'


def format_metric(dim: Dimension, decimals: int = 1) -> str:
    """Format dimension as metric string"""
    mm = to_millimeters(dim)

    if mm >= 1000:
        return f"{mm / 1000:.{decimals}f}m"
    if mm >= 100 and mm % 10 == 0:
        return f"{int(mm / 10)}cm"
    return f"{mm:.{decimals}f}mm"


def format_dimension(dim: Dimension) -> str:
    """Format dimension in its native unit"""
    if dim.unit == UnitSystem.IMPERIAL:
        return format_imperial(dim)
    return format_metric(dim)


# ============================================
# UTILITY FUNCTIONS
# ============================================

def parse_dimensional_lumber(notation: str) -> Optional[Tuple[Dimension, Dimension]]:
    """Parse dimensional lumber notation (e.g., '2x4')"""
    match = PATTERNS["dimensional_lumber"].match(notation)
    if not match:
        return None

    key = f"{match.group(1)}x{match.group(2)}"
    actual = DIMENSIONAL_LUMBER.get(key)

    if not actual:
        return None

    width, thickness = actual
    return (
        Dimension(value=width, unit=UnitSystem.IMPERIAL, original=f'{width}"'),
        Dimension(value=thickness, unit=UnitSystem.IMPERIAL, original=f'{thickness}"')
    )


def is_variable_reference(input_str: str) -> bool:
    """Check if a string is a variable reference"""
    return bool(PATTERNS["variable"].match(input_str.strip()))


def extract_variable_name(input_str: str) -> Optional[str]:
    """Extract variable name from reference"""
    match = PATTERNS["variable"].match(input_str.strip())
    return match.group(1) if match else None
