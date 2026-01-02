"""
WoodML Formula Evaluation
Handles variable substitution and arithmetic operations
"""

import re
import math
from typing import Dict, List, Union, Optional
from .types import Dimension, UnitSystem, Formulas
from .units import parse_dimension, to_inches, to_millimeters


# ============================================
# TYPES
# ============================================

FormulaValue = Union[Dimension, float]

class FormulaContext:
    """Context for formula evaluation"""
    def __init__(self, variables: Dict[str, FormulaValue], default_unit: UnitSystem):
        self.variables = variables
        self.default_unit = default_unit


# ============================================
# CONSTANTS
# ============================================

GOLDEN_RATIO = 1.618033988749895

# Wood movement coefficients (tangential, per % MC change)
WOOD_MOVEMENT = {
    "red_oak": 0.00369,
    "white_oak": 0.00365,
    "cherry": 0.00274,
    "walnut": 0.00274,
    "maple": 0.00353,
    "pine": 0.00263,
    "ash": 0.00274,
    "birch": 0.00338,
    "poplar": 0.00289,
    "mahogany": 0.00256,
}


# ============================================
# TOKENIZER
# ============================================

class Token:
    def __init__(self, type_: str, value: str, position: int):
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


def tokenize(expression: str) -> List[Token]:
    """Tokenize a formula expression"""
    tokens = []
    pos = 0

    patterns = [
        ("DIMENSION", r'(\d+(-\d+/\d+)?"|(\d+/\d+)"|(\d+)\'(\d+(-\d+/\d+)?)?"|(\d+(\.\d+)?)(mm|cm|m))'),
        ("FUNCTION", r'(min|max|round|floor|ceil|abs|sqrt|sin|cos|tan|asin|acos|atan|board_feet|square_feet|linear_feet|miter_angle|compound_miter|diagonal|wood_movement|golden_ratio|fibonacci|circle_circumference|circle_area|circle_diameter)\s*(?=\()'),
        ("VARIABLE", r'\$[a-zA-Z_][a-zA-Z0-9_]*'),
        ("NUMBER", r'\d+(\.\d+)?'),
        ("OPERATOR", r'[+\-*/^]'),
        ("LPAREN", r'\('),
        ("RPAREN", r'\)'),
        ("COMMA", r','),
    ]

    while pos < len(expression):
        # Skip whitespace
        ws_match = re.match(r'\s+', expression[pos:])
        if ws_match:
            pos += len(ws_match.group(0))
            continue

        matched = False
        for token_type, pattern in patterns:
            match = re.match(pattern, expression[pos:], re.IGNORECASE)
            if match:
                tokens.append(Token(token_type, match.group(0), pos))
                pos += len(match.group(0))
                matched = True
                break

        if not matched:
            raise ValueError(f'Unexpected character at position {pos}: "{expression[pos]}"')

    return tokens


# ============================================
# PARSER (RECURSIVE DESCENT)
# ============================================

class FormulaParser:
    def __init__(self, tokens: List[Token], context: FormulaContext):
        self.tokens = tokens
        self.pos = 0
        self.context = context

    def parse(self) -> FormulaValue:
        result = self._parse_expression()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.pos].value}")
        return result

    def _parse_expression(self) -> FormulaValue:
        return self._parse_additive()

    def _parse_additive(self) -> FormulaValue:
        left = self._parse_multiplicative()

        while self._match("+", "-"):
            op = self._previous().value
            right = self._parse_multiplicative()
            left = self._apply_operator(left, op, right)

        return left

    def _parse_multiplicative(self) -> FormulaValue:
        left = self._parse_power()

        while self._match("*", "/"):
            op = self._previous().value
            right = self._parse_power()
            left = self._apply_operator(left, op, right)

        return left

    def _parse_power(self) -> FormulaValue:
        left = self._parse_unary()

        while self._match("^"):
            right = self._parse_unary()
            left = self._apply_operator(left, "^", right)

        return left

    def _parse_unary(self) -> FormulaValue:
        if self._match("-"):
            value = self._parse_unary()
            if isinstance(value, (int, float)):
                return -value
            return Dimension(value=-value.value, unit=value.unit, original=value.original)
        return self._parse_primary()

    def _parse_primary(self) -> FormulaValue:
        # Function call
        if self._check("FUNCTION"):
            return self._parse_function()

        # Parenthesized expression
        if self._match("("):
            expr = self._parse_expression()
            self._consume("RPAREN", "Expected closing parenthesis")
            return expr

        # Variable reference
        if self._check("VARIABLE"):
            token = self._advance()
            var_name = token.value[1:]  # Remove $
            if var_name not in self.context.variables:
                raise ValueError(f"Undefined variable: {var_name}")
            return self.context.variables[var_name]

        # Dimension
        if self._check("DIMENSION"):
            token = self._advance()
            return parse_dimension(token.value, self.context.default_unit)

        # Number
        if self._check("NUMBER"):
            token = self._advance()
            return float(token.value)

        raise ValueError(f"Unexpected token: {self._peek().value if self._peek() else 'end of expression'}")

    def _parse_function(self) -> FormulaValue:
        func_token = self._advance()
        func_name = func_token.value.lower()

        self._consume("LPAREN", "Expected opening parenthesis after function name")

        args: List[FormulaValue] = []
        if not self._check("RPAREN"):
            args.append(self._parse_expression())
            while self._match(","):
                args.append(self._parse_expression())

        self._consume("RPAREN", "Expected closing parenthesis")

        return self._evaluate_function(func_name, args)

    def _evaluate_function(self, name: str, args: List[FormulaValue]) -> FormulaValue:
        def get_number(v: FormulaValue) -> float:
            if isinstance(v, (int, float)):
                return float(v)
            return to_inches(v)

        if name == "min":
            return min(get_number(a) for a in args)

        if name == "max":
            return max(get_number(a) for a in args)

        if name == "abs":
            return abs(get_number(args[0]))

        if name == "sqrt":
            return math.sqrt(get_number(args[0]))

        if name == "round":
            value = get_number(args[0])
            precision = get_number(args[1]) if len(args) > 1 else 1
            return round(value / precision) * precision

        if name == "floor":
            value = get_number(args[0])
            precision = get_number(args[1]) if len(args) > 1 else 1
            return math.floor(value / precision) * precision

        if name == "ceil":
            value = get_number(args[0])
            precision = get_number(args[1]) if len(args) > 1 else 1
            return math.ceil(value / precision) * precision

        if name == "sin":
            return math.sin(math.radians(get_number(args[0])))

        if name == "cos":
            return math.cos(math.radians(get_number(args[0])))

        if name == "tan":
            return math.tan(math.radians(get_number(args[0])))

        if name == "asin":
            return math.degrees(math.asin(get_number(args[0])))

        if name == "acos":
            return math.degrees(math.acos(get_number(args[0])))

        if name == "atan":
            return math.degrees(math.atan(get_number(args[0])))

        if name == "board_feet":
            length = get_number(args[0])
            width = get_number(args[1])
            thickness = get_number(args[2])
            return (length * width * thickness) / 144

        if name == "square_feet":
            length = get_number(args[0])
            width = get_number(args[1])
            return (length * width) / 144

        if name == "miter_angle":
            sides = get_number(args[0])
            return 90 - 180 / sides

        if name == "diagonal":
            width = get_number(args[0])
            height = get_number(args[1])
            result = math.sqrt(width * width + height * height)
            return Dimension(
                value=result,
                unit=self.context.default_unit,
                original=f"diagonal({args[0]}, {args[1]})"
            )

        if name == "golden_ratio":
            return GOLDEN_RATIO

        if name == "fibonacci":
            n = int(get_number(args[0]))
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            return float(a)

        if name == "wood_movement":
            width = get_number(args[0])
            species = str(args[1]).lower().strip("'\"")
            humidity_change = get_number(args[2])
            coefficient = WOOD_MOVEMENT.get(species, 0.003)
            movement = width * coefficient * humidity_change
            return Dimension(
                value=movement,
                unit=self.context.default_unit,
                original=f"wood_movement({width}, {species}, {humidity_change})"
            )

        if name == "circle_circumference":
            diameter = get_number(args[0])
            return Dimension(
                value=math.pi * diameter,
                unit=self.context.default_unit,
                original=f"circle_circumference({diameter})"
            )

        if name == "circle_area":
            diameter = get_number(args[0])
            radius = diameter / 2
            return math.pi * radius * radius

        if name == "circle_diameter":
            circumference = get_number(args[0])
            return Dimension(
                value=circumference / math.pi,
                unit=self.context.default_unit,
                original=f"circle_diameter({circumference})"
            )

        raise ValueError(f"Unknown function: {name}")

    def _apply_operator(self, left: FormulaValue, op: str, right: FormulaValue) -> FormulaValue:
        left_num = left if isinstance(left, (int, float)) else to_inches(left)
        right_num = right if isinstance(right, (int, float)) else to_inches(right)

        if op == "+":
            result = left_num + right_num
        elif op == "-":
            result = left_num - right_num
        elif op == "*":
            result = left_num * right_num
        elif op == "/":
            if right_num == 0:
                raise ValueError("Division by zero")
            result = left_num / right_num
        elif op == "^":
            result = left_num ** right_num
        else:
            raise ValueError(f"Unknown operator: {op}")

        # If either operand was a dimension, result is a dimension
        # Exception: dimension * dimension loses units (area)
        if op == "*" and isinstance(left, Dimension) and isinstance(right, Dimension):
            return result

        if isinstance(left, Dimension):
            return Dimension(value=result, unit=left.unit, original=f"({left.original} {op} {right})")
        if isinstance(right, Dimension):
            return Dimension(value=result, unit=right.unit, original=f"({left} {op} {right.original})")

        return result

    # Parser helpers
    def _match(self, *values: str) -> bool:
        for value in values:
            if self._check("OPERATOR") and self._peek() and self._peek().value == value:
                self._advance()
                return True
            if self._check("LPAREN") and value == "(":
                self._advance()
                return True
            if self._check("COMMA") and value == ",":
                self._advance()
                return True
        return False

    def _check(self, type_: str) -> bool:
        token = self._peek()
        return token is not None and token.type == type_

    def _peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def _advance(self) -> Token:
        if self.pos < len(self.tokens):
            self.pos += 1
        return self._previous()

    def _consume(self, type_: str, message: str) -> Token:
        if self._check(type_):
            return self._advance()
        raise ValueError(message)


# ============================================
# PUBLIC API
# ============================================

def create_context(
    variables: Dict[str, Union[str, float]],
    default_unit: UnitSystem = UnitSystem.IMPERIAL
) -> FormulaContext:
    """Create a formula context with variables"""
    var_map: Dict[str, FormulaValue] = {}

    for name, value in variables.items():
        if isinstance(value, (int, float)):
            var_map[name] = float(value)
        else:
            try:
                var_map[name] = parse_dimension(value, default_unit)
            except ValueError:
                var_map[name] = value  # Store as-is for string values

    return FormulaContext(variables=var_map, default_unit=default_unit)


def evaluate_formula(expression: str, context: FormulaContext) -> FormulaValue:
    """Evaluate a formula expression"""
    tokens = tokenize(expression)
    parser = FormulaParser(tokens, context)
    return parser.parse()


def resolve_formulas(
    formulas: Formulas,
    default_unit: UnitSystem = UnitSystem.IMPERIAL
) -> Dict[str, FormulaValue]:
    """Resolve all formulas in a Formulas object"""
    resolved: Dict[str, FormulaValue] = {}

    # First pass: resolve vars
    if formulas.vars:
        for name, value in formulas.vars.items():
            try:
                resolved[name] = parse_dimension(value, default_unit)
            except ValueError:
                # If not a dimension, try as number
                try:
                    resolved[name] = float(value)
                except ValueError:
                    pass

    # Second pass: resolve computed (may reference vars)
    if formulas.computed:
        context = FormulaContext(variables=resolved, default_unit=default_unit)
        computed = dict(formulas.computed)
        max_passes = 10

        while computed and max_passes > 0:
            remaining = {}

            for name, expression in computed.items():
                try:
                    value = evaluate_formula(expression, context)
                    resolved[name] = value
                    context.variables[name] = value
                except Exception:
                    remaining[name] = expression

            if len(remaining) == len(computed):
                raise ValueError(
                    f"Circular reference or undefined variables in: {', '.join(remaining.keys())}"
                )

            computed = remaining
            max_passes -= 1

    return resolved
