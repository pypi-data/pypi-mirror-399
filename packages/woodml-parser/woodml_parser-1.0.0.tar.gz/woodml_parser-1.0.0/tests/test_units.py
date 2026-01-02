"""Unit Tests for WoodML Units Module"""

import pytest
from woodml.types import UnitSystem
from woodml.units import (
    parse_dimension,
    to_inches,
    to_millimeters,
    convert_to,
    format_imperial,
    format_metric,
    format_dimension,
    decimal_to_fraction,
    parse_dimensional_lumber,
    is_variable_reference,
    extract_variable_name,
)


class TestParseDimension:
    """Tests for parse_dimension function"""

    class TestImperialWholeInches:
        def test_parse_whole_inches(self):
            dim = parse_dimension('24"')
            assert dim.value == 24
            assert dim.unit == UnitSystem.IMPERIAL
            assert dim.original == '24"'

        def test_parse_single_digit_inches(self):
            dim = parse_dimension('6"')
            assert dim.value == 6

    class TestImperialFractionalInches:
        def test_parse_half_inch(self):
            dim = parse_dimension('1/2"')
            assert dim.value == 0.5
            assert dim.unit == UnitSystem.IMPERIAL

        def test_parse_quarter_inch(self):
            dim = parse_dimension('3/4"')
            assert dim.value == 0.75

        def test_parse_eighth_inch(self):
            dim = parse_dimension('5/8"')
            assert dim.value == 0.625

        def test_parse_sixteenth_inch(self):
            dim = parse_dimension('3/16"')
            assert dim.value == 3 / 16

        def test_parse_thirty_second_inch(self):
            dim = parse_dimension('5/32"')
            assert dim.value == 5 / 32

        def test_parse_sixty_fourth_inch(self):
            dim = parse_dimension('17/64"')
            assert dim.value == 17 / 64

        def test_reject_invalid_denominators(self):
            with pytest.raises(ValueError, match="Invalid fraction denominator"):
                parse_dimension('1/3"')
            with pytest.raises(ValueError, match="Invalid fraction denominator"):
                parse_dimension('1/5"')
            with pytest.raises(ValueError, match="Invalid fraction denominator"):
                parse_dimension('1/7"')

    class TestImperialMixedInches:
        def test_parse_mixed_number(self):
            dim = parse_dimension('3-1/2"')
            assert dim.value == 3.5
            assert dim.unit == UnitSystem.IMPERIAL

        def test_parse_larger_mixed_number(self):
            dim = parse_dimension('12-3/4"')
            assert dim.value == 12.75

        def test_parse_mixed_with_small_fraction(self):
            dim = parse_dimension('1-1/16"')
            assert dim.value == 1 + 1 / 16

    class TestImperialFeet:
        def test_parse_feet_only(self):
            dim = parse_dimension("6'")
            assert dim.value == 72
            assert dim.unit == UnitSystem.IMPERIAL

        def test_parse_feet_and_inches(self):
            dim = parse_dimension("6'4\"")
            assert dim.value == 76

        def test_parse_feet_and_mixed_inches(self):
            dim = parse_dimension("6'4-1/2\"")
            assert dim.value == 76.5

    class TestImperialQuarterNotation:
        def test_parse_4_4(self):
            dim = parse_dimension('4/4')
            assert dim.value == 1

        def test_parse_8_4(self):
            dim = parse_dimension('8/4')
            assert dim.value == 2

        def test_parse_12_4(self):
            dim = parse_dimension('12/4')
            assert dim.value == 3

    class TestMetricMillimeters:
        def test_parse_whole_millimeters(self):
            dim = parse_dimension('610mm')
            assert dim.value == 610
            assert dim.unit == UnitSystem.METRIC

        def test_parse_decimal_millimeters(self):
            dim = parse_dimension('19.5mm')
            assert dim.value == 19.5

        def test_case_insensitive(self):
            dim = parse_dimension('100MM')
            assert dim.value == 100
            assert dim.unit == UnitSystem.METRIC

    class TestMetricCentimeters:
        def test_parse_centimeters_to_mm(self):
            dim = parse_dimension('61cm')
            assert dim.value == 610
            assert dim.unit == UnitSystem.METRIC

        def test_parse_decimal_centimeters(self):
            dim = parse_dimension('2.5cm')
            assert dim.value == 25

    class TestMetricMeters:
        def test_parse_meters_to_mm(self):
            dim = parse_dimension('2.4m')
            assert dim.value == 2400
            assert dim.unit == UnitSystem.METRIC

        def test_parse_whole_meters(self):
            dim = parse_dimension('1m')
            assert dim.value == 1000

    class TestWhitespaceHandling:
        def test_trim_leading_whitespace(self):
            dim = parse_dimension('  24"')
            assert dim.value == 24

        def test_trim_trailing_whitespace(self):
            dim = parse_dimension('24"  ')
            assert dim.value == 24

    class TestInvalidInput:
        def test_throw_on_invalid_format(self):
            with pytest.raises(ValueError):
                parse_dimension('invalid')
            with pytest.raises(ValueError):
                parse_dimension('')
            with pytest.raises(ValueError):
                parse_dimension('abc123')


class TestToInches:
    def test_return_value_for_imperial(self):
        dim = parse_dimension('24"')
        assert to_inches(dim) == 24

    def test_convert_mm_to_inches(self):
        dim = parse_dimension('25.4mm')
        assert to_inches(dim) == 1

    def test_convert_larger_mm_values(self):
        dim = parse_dimension('254mm')
        assert to_inches(dim) == 10


class TestToMillimeters:
    def test_return_value_for_metric(self):
        dim = parse_dimension('610mm')
        assert to_millimeters(dim) == 610

    def test_convert_inches_to_mm(self):
        dim = parse_dimension('1"')
        assert to_millimeters(dim) == 25.4

    def test_convert_larger_inch_values(self):
        dim = parse_dimension('10"')
        assert to_millimeters(dim) == 254


class TestConvertTo:
    def test_return_same_if_already_target(self):
        dim = parse_dimension('24"')
        result = convert_to(dim, UnitSystem.IMPERIAL)
        assert result.value == 24
        assert result.unit == UnitSystem.IMPERIAL

    def test_convert_imperial_to_metric(self):
        dim = parse_dimension('1"')
        result = convert_to(dim, UnitSystem.METRIC)
        assert result.value == 25.4
        assert result.unit == UnitSystem.METRIC

    def test_convert_metric_to_imperial(self):
        dim = parse_dimension('25.4mm')
        result = convert_to(dim, UnitSystem.IMPERIAL)
        assert result.value == 1
        assert result.unit == UnitSystem.IMPERIAL


class TestDecimalToFraction:
    def test_convert_0_5_to_1_2(self):
        frac = decimal_to_fraction(0.5)
        assert frac.whole == 0
        assert frac.numerator == 1
        assert frac.denominator == 2

    def test_convert_0_75_to_3_4(self):
        frac = decimal_to_fraction(0.75)
        assert frac.whole == 0
        assert frac.numerator == 3
        assert frac.denominator == 4

    def test_convert_3_5_to_3_1_2(self):
        frac = decimal_to_fraction(3.5)
        assert frac.whole == 3
        assert frac.numerator == 1
        assert frac.denominator == 2

    def test_convert_whole_numbers(self):
        frac = decimal_to_fraction(5)
        assert frac.whole == 5
        assert frac.numerator == 0

    def test_handle_near_zero_remainder(self):
        frac = decimal_to_fraction(5.0001)
        assert frac.whole == 5

    def test_simplify_fractions(self):
        frac = decimal_to_fraction(0.25)
        assert frac.numerator == 1
        assert frac.denominator == 4

    def test_respect_max_denominator(self):
        frac = decimal_to_fraction(0.0625, 16)  # 1/16
        assert frac.numerator == 1
        assert frac.denominator == 16


class TestFormatImperial:
    def test_format_whole_inches(self):
        dim = parse_dimension('10"')
        assert format_imperial(dim) == '10"'

    def test_format_large_inches_as_feet(self):
        dim = parse_dimension('24"')
        assert format_imperial(dim) == "2'"

    def test_format_fractional_inches(self):
        from woodml.types import Dimension
        dim = Dimension(value=0.5, unit=UnitSystem.IMPERIAL, original='')
        assert format_imperial(dim) == '1/2"'

    def test_format_mixed_inches(self):
        from woodml.types import Dimension
        dim = Dimension(value=3.5, unit=UnitSystem.IMPERIAL, original='')
        assert format_imperial(dim) == '3-1/2"'

    def test_format_feet_for_large_values(self):
        from woodml.types import Dimension
        dim = Dimension(value=24, unit=UnitSystem.IMPERIAL, original='')
        assert format_imperial(dim) == "2'"

    def test_format_exactly_12_inches_as_1_foot(self):
        from woodml.types import Dimension
        dim = Dimension(value=12, unit=UnitSystem.IMPERIAL, original='')
        assert format_imperial(dim) == "1'"

    def test_format_feet_and_inches(self):
        from woodml.types import Dimension
        dim = Dimension(value=30, unit=UnitSystem.IMPERIAL, original='')
        assert format_imperial(dim) == "2'6\""

    def test_convert_metric_to_imperial_for_formatting(self):
        dim = parse_dimension('254mm')  # 10 inches
        assert format_imperial(dim) == '10"'


class TestFormatMetric:
    def test_format_millimeters(self):
        dim = parse_dimension('610mm')
        # 610mm = 61cm since it's divisible by 10 and >= 100
        assert format_metric(dim) == '61cm'

    def test_format_small_mm_values(self):
        dim = parse_dimension('95mm')
        assert format_metric(dim) == '95.0mm'

    def test_format_centimeters_for_round_values(self):
        dim = parse_dimension('100mm')
        assert format_metric(dim) == '10cm'

    def test_format_meters_for_large_values(self):
        dim = parse_dimension('2400mm')
        assert format_metric(dim) == '2.4m'

    def test_convert_imperial_to_metric_for_formatting(self):
        dim = parse_dimension('1"')
        assert format_metric(dim) == '25.4mm'


class TestFormatDimension:
    def test_use_imperial_format_for_imperial(self):
        dim = parse_dimension('12"')
        assert format_dimension(dim) == "1'"

    def test_use_metric_format_for_metric(self):
        dim = parse_dimension('500mm')
        assert format_dimension(dim) == '50cm'


class TestParseDimensionalLumber:
    def test_parse_2x4(self):
        result = parse_dimensional_lumber('2x4')
        assert result is not None
        width, thickness = result
        assert thickness.value == 1.5
        assert width.value == 3.5

    def test_parse_1x6(self):
        result = parse_dimensional_lumber('1x6')
        assert result is not None
        width, thickness = result
        assert thickness.value == 0.75
        assert width.value == 5.5

    def test_parse_4x4(self):
        result = parse_dimensional_lumber('4x4')
        assert result is not None
        width, thickness = result
        assert thickness.value == 3.5
        assert width.value == 3.5

    def test_return_none_for_invalid_notation(self):
        assert parse_dimensional_lumber('invalid') is None
        assert parse_dimensional_lumber('3x3') is None  # Not a standard size


class TestIsVariableReference:
    def test_return_true_for_variable_references(self):
        assert is_variable_reference('$width') is True
        assert is_variable_reference('$my_var') is True
        assert is_variable_reference('$var123') is True

    def test_return_false_for_non_variables(self):
        assert is_variable_reference('24"') is False
        assert is_variable_reference('width') is False
        assert is_variable_reference('$') is False

    def test_handle_whitespace(self):
        assert is_variable_reference('  $width  ') is True


class TestExtractVariableName:
    def test_extract_variable_name(self):
        assert extract_variable_name('$width') == 'width'
        assert extract_variable_name('$my_var') == 'my_var'

    def test_return_none_for_non_variables(self):
        assert extract_variable_name('24"') is None
        assert extract_variable_name('width') is None

    def test_handle_whitespace(self):
        assert extract_variable_name('  $width  ') == 'width'
