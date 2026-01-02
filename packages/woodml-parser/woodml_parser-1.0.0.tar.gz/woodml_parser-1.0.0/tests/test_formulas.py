"""Unit Tests for WoodML Formulas Module"""

import pytest
import math
from woodml.types import Dimension, UnitSystem, Formulas
from woodml.formulas import (
    create_context,
    evaluate_formula,
    resolve_formulas,
)


class TestCreateContext:
    def test_create_context_with_numeric_variables(self):
        ctx = create_context({'quantity': 4, 'multiplier': 2})
        assert ctx.variables['quantity'] == 4
        assert ctx.variables['multiplier'] == 2

    def test_create_context_with_dimension_strings(self):
        ctx = create_context({'width': '24"', 'height': '36"'})
        width = ctx.variables['width']
        assert isinstance(width, Dimension)
        assert width.value == 24
        assert width.unit == UnitSystem.IMPERIAL

    def test_use_specified_default_unit(self):
        ctx = create_context({'size': '100mm'}, UnitSystem.METRIC)
        assert ctx.default_unit == UnitSystem.METRIC


class TestEvaluateFormula:
    class TestBasicArithmetic:
        def test_evaluate_addition(self):
            ctx = create_context({})
            assert evaluate_formula('5 + 3', ctx) == 8

        def test_evaluate_subtraction(self):
            ctx = create_context({})
            assert evaluate_formula('10 - 4', ctx) == 6

        def test_evaluate_multiplication(self):
            ctx = create_context({})
            assert evaluate_formula('6 * 7', ctx) == 42

        def test_evaluate_division(self):
            ctx = create_context({})
            assert evaluate_formula('20 / 4', ctx) == 5

        def test_evaluate_exponentiation(self):
            ctx = create_context({})
            assert evaluate_formula('2 ^ 3', ctx) == 8

        def test_throw_on_division_by_zero(self):
            ctx = create_context({})
            with pytest.raises(ValueError, match="Division by zero"):
                evaluate_formula('10 / 0', ctx)

    class TestOperatorPrecedence:
        def test_respect_multiplication_over_addition(self):
            ctx = create_context({})
            assert evaluate_formula('2 + 3 * 4', ctx) == 14

        def test_respect_parentheses(self):
            ctx = create_context({})
            assert evaluate_formula('(2 + 3) * 4', ctx) == 20

        def test_handle_nested_parentheses(self):
            ctx = create_context({})
            assert evaluate_formula('((2 + 3) * (4 - 1))', ctx) == 15

        def test_handle_complex_expressions(self):
            ctx = create_context({})
            assert evaluate_formula('10 - 2 * 3 + 4 / 2', ctx) == 6

    class TestUnaryOperators:
        def test_handle_negative_numbers(self):
            ctx = create_context({})
            assert evaluate_formula('-5', ctx) == -5

        def test_handle_negative_in_expression(self):
            ctx = create_context({})
            assert evaluate_formula('10 + -3', ctx) == 7

        def test_handle_double_negative(self):
            ctx = create_context({})
            assert evaluate_formula('--5', ctx) == 5

    class TestVariables:
        def test_resolve_numeric_variables(self):
            ctx = create_context({'x': 10, 'y': 5})
            assert evaluate_formula('$x + $y', ctx) == 15

        def test_resolve_dimension_variables(self):
            ctx = create_context({'width': '24"'})
            result = evaluate_formula('$width', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 24

        def test_use_dimensions_in_calculations(self):
            ctx = create_context({'width': '24"', 'depth': '12"'})
            result = evaluate_formula('$width + $depth', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 36

        def test_throw_on_undefined_variable(self):
            ctx = create_context({})
            with pytest.raises(ValueError, match="Undefined variable"):
                evaluate_formula('$undefined', ctx)

    class TestDimensionsInFormulas:
        def test_parse_dimensions_in_expressions(self):
            ctx = create_context({})
            result = evaluate_formula('24" + 12"', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 36

        def test_handle_mixed_units(self):
            ctx = create_context({})
            result = evaluate_formula('24" + 25.4mm', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 25  # 24 + 1 inch

        def test_multiply_dimension_by_number(self):
            ctx = create_context({})
            result = evaluate_formula('12" * 2', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 24

        def test_divide_dimension_by_number(self):
            ctx = create_context({})
            result = evaluate_formula('24" / 2', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 12

        def test_return_number_when_multiplying_two_dimensions(self):
            ctx = create_context({})
            result = evaluate_formula('12" * 12"', ctx)
            assert isinstance(result, (int, float))
            assert result == 144

    class TestMathFunctions:
        def test_evaluate_min(self):
            ctx = create_context({})
            assert evaluate_formula('min(5, 3, 8)', ctx) == 3

        def test_evaluate_max(self):
            ctx = create_context({})
            assert evaluate_formula('max(5, 3, 8)', ctx) == 8

        def test_evaluate_abs(self):
            ctx = create_context({})
            assert evaluate_formula('abs(-5)', ctx) == 5

        def test_evaluate_sqrt(self):
            ctx = create_context({})
            assert evaluate_formula('sqrt(16)', ctx) == 4

        def test_evaluate_round(self):
            ctx = create_context({})
            assert evaluate_formula('round(3.7)', ctx) == 4

        def test_evaluate_round_with_precision(self):
            ctx = create_context({})
            result = evaluate_formula('round(3.14159, 0.01)', ctx)
            assert abs(result - 3.14) < 0.001

        def test_evaluate_floor(self):
            ctx = create_context({})
            assert evaluate_formula('floor(3.9)', ctx) == 3

        def test_evaluate_ceil(self):
            ctx = create_context({})
            assert evaluate_formula('ceil(3.1)', ctx) == 4

    class TestTrigFunctions:
        def test_evaluate_sin_degrees(self):
            ctx = create_context({})
            result = evaluate_formula('sin(90)', ctx)
            assert abs(result - 1) < 0.0001

        def test_evaluate_cos_degrees(self):
            ctx = create_context({})
            result = evaluate_formula('cos(0)', ctx)
            assert abs(result - 1) < 0.0001

        def test_evaluate_tan_degrees(self):
            ctx = create_context({})
            result = evaluate_formula('tan(45)', ctx)
            assert abs(result - 1) < 0.0001

        def test_evaluate_asin_returns_degrees(self):
            ctx = create_context({})
            result = evaluate_formula('asin(1)', ctx)
            assert abs(result - 90) < 0.0001

        def test_evaluate_acos_returns_degrees(self):
            ctx = create_context({})
            result = evaluate_formula('acos(1)', ctx)
            assert abs(result) < 0.0001

        def test_evaluate_atan_returns_degrees(self):
            ctx = create_context({})
            result = evaluate_formula('atan(1)', ctx)
            assert abs(result - 45) < 0.0001

    class TestWoodworkingFunctions:
        def test_calculate_board_feet(self):
            ctx = create_context({})
            # 96" x 6" x 1" = 4 board feet
            result = evaluate_formula('board_feet(96, 6, 1)', ctx)
            assert result == 4

        def test_calculate_square_feet(self):
            ctx = create_context({})
            # 12" x 12" = 1 sq ft
            result = evaluate_formula('square_feet(12, 12)', ctx)
            assert result == 1

        def test_calculate_miter_angle_hexagon(self):
            ctx = create_context({})
            # 6 sides = 60 degree miter
            result = evaluate_formula('miter_angle(6)', ctx)
            assert result == 60

        def test_calculate_miter_angle_octagon(self):
            ctx = create_context({})
            # 8 sides = 67.5 degree miter
            result = evaluate_formula('miter_angle(8)', ctx)
            assert result == 67.5

        def test_calculate_diagonal(self):
            ctx = create_context({})
            # 3-4-5 triangle
            result = evaluate_formula('diagonal(3, 4)', ctx)
            assert isinstance(result, Dimension)
            assert result.value == 5

        def test_return_golden_ratio(self):
            ctx = create_context({})
            result = evaluate_formula('golden_ratio()', ctx)
            assert abs(result - 1.618033988749895) < 0.0001

        def test_calculate_fibonacci(self):
            ctx = create_context({})
            assert evaluate_formula('fibonacci(0)', ctx) == 0
            assert evaluate_formula('fibonacci(1)', ctx) == 1
            assert evaluate_formula('fibonacci(5)', ctx) == 5
            assert evaluate_formula('fibonacci(10)', ctx) == 55

        def test_calculate_circle_circumference(self):
            ctx = create_context({})
            result = evaluate_formula('circle_circumference(10)', ctx)
            assert isinstance(result, Dimension)
            assert abs(result.value - 31.4159) < 0.001

        def test_calculate_circle_area(self):
            ctx = create_context({})
            # Diameter 10, radius 5, area = pi * 25 = 78.54
            result = evaluate_formula('circle_area(10)', ctx)
            assert abs(result - 78.5398) < 0.001

        def test_calculate_circle_diameter(self):
            ctx = create_context({})
            result = evaluate_formula('circle_diameter(31.4159)', ctx)
            assert isinstance(result, Dimension)
            assert abs(result.value - 10) < 0.001

    class TestNestedFunctionCalls:
        def test_handle_nested_functions(self):
            ctx = create_context({})
            assert evaluate_formula('max(min(5, 10), 3)', ctx) == 5

        def test_handle_functions_in_expressions(self):
            ctx = create_context({})
            assert evaluate_formula('sqrt(16) + 2', ctx) == 6

    class TestErrorHandling:
        def test_throw_on_unknown_function(self):
            ctx = create_context({})
            # 'unknown' isn't recognized as a function token, so it fails at tokenization
            with pytest.raises(ValueError, match="Unexpected character"):
                evaluate_formula('unknown(5)', ctx)

        def test_throw_on_unexpected_token(self):
            ctx = create_context({})
            with pytest.raises(ValueError, match="Unexpected character"):
                evaluate_formula('5 @ 3', ctx)

        def test_throw_on_unclosed_parenthesis(self):
            ctx = create_context({})
            with pytest.raises(ValueError, match="Expected closing parenthesis"):
                evaluate_formula('(5 + 3', ctx)


class TestResolveFormulas:
    def test_resolve_simple_vars(self):
        formulas = Formulas(
            vars={'width': '24"', 'height': '36"'}
        )
        resolved = resolve_formulas(formulas)
        width = resolved['width']
        height = resolved['height']
        assert isinstance(width, Dimension)
        assert width.value == 24
        assert isinstance(height, Dimension)
        assert height.value == 36

    def test_resolve_computed_values(self):
        formulas = Formulas(
            vars={'width': '24"'},
            computed={'double_width': '$width * 2'}
        )
        resolved = resolve_formulas(formulas)
        double_width = resolved['double_width']
        assert isinstance(double_width, Dimension)
        assert double_width.value == 48

    def test_resolve_dependent_computed_values(self):
        formulas = Formulas(
            vars={'base': '12"'},
            computed={'double': '$base * 2', 'quadruple': '$double * 2'}
        )
        resolved = resolve_formulas(formulas)
        quadruple = resolved['quadruple']
        assert isinstance(quadruple, Dimension)
        assert quadruple.value == 48

    def test_handle_numeric_vars(self):
        formulas = Formulas(
            vars={'quantity': '4', 'multiplier': '2.5'}
        )
        resolved = resolve_formulas(formulas)
        assert resolved['quantity'] == 4
        assert resolved['multiplier'] == 2.5

    def test_throw_on_circular_references(self):
        formulas = Formulas(
            computed={'a': '$b + 1', 'b': '$a + 1'}
        )
        with pytest.raises(ValueError, match="Circular reference"):
            resolve_formulas(formulas)

    def test_use_default_unit_system(self):
        formulas = Formulas(
            vars={'size': '100mm'}
        )
        resolved = resolve_formulas(formulas, UnitSystem.METRIC)
        size = resolved['size']
        assert isinstance(size, Dimension)
        assert size.unit == UnitSystem.METRIC
