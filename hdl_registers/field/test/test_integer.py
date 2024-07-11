# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from copy import copy

# Third party libraries
import pytest

# First party libraries
from hdl_registers.field.integer import Integer

TEST_FIELD = Integer(
    name="apa",
    base_index=3,
    description="hest",
    min_value=120,
    max_value=456,
    default_value=127,
)


def test_fields():
    assert TEST_FIELD.name == "apa"
    assert TEST_FIELD.base_index == 3
    assert TEST_FIELD.description == "hest"
    assert TEST_FIELD.min_value == 120
    assert TEST_FIELD.max_value == 456
    assert TEST_FIELD.default_value == 127


def test_repr_is_an_actual_representation():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(TEST_FIELD)


def test_repr_is_same_after_copy():
    field = copy(TEST_FIELD)

    assert repr(field) == repr(TEST_FIELD)


def test_repr_should_change_when_name_is_changed():
    field = copy(TEST_FIELD)
    field.name = "zebra"

    assert repr(field) != repr(TEST_FIELD)


def test_repr_should_change_when_default_value_is_changed():
    field = copy(TEST_FIELD)
    field.default_value = 133

    assert repr(field) != repr(TEST_FIELD)


def test_repr_when_static_members_have_different_value():
    original_field = Integer(
        name="apa",
        base_index=0,
        description="",
        min_value=10,
        max_value=10,
        default_value=10,
    )

    # Different base_index
    assert repr(
        Integer(
            name="apa",
            base_index=25,
            description="",
            min_value=10,
            max_value=10,
            default_value=10,
        )
    ) != repr(original_field)

    # Different description
    assert repr(
        Integer(
            name="apa",
            base_index=0,
            description="blah",
            min_value=10,
            max_value=10,
            default_value=10,
        )
    ) != repr(original_field)

    # Different min_value
    assert repr(
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value=5,
            max_value=10,
            default_value=10,
        )
    ) != repr(original_field)

    # Different max_value
    assert repr(
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value=10,
            max_value=15,
            default_value=10,
        )
    ) != repr(original_field)


def test_is_signed():
    def get_is_signed(min_value, max_value):
        return Integer(
            name="",
            base_index=0,
            description="",
            min_value=min_value,
            max_value=max_value,
            default_value=min_value,
        ).is_signed

    assert get_is_signed(min_value=-10, max_value=10)
    assert get_is_signed(min_value=-10, max_value=-5)
    assert not get_is_signed(min_value=0, max_value=10)
    assert not get_is_signed(min_value=5, max_value=10)


def test_non_ascending_range_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Integer(
            name="apa", base_index=0, description="", min_value=10, max_value=0, default_value=0
        )

    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have ascending range. Got: [10, 0].'
    )


def test_non_integer_range_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value="5",
            max_value=10,
            default_value=11,
        )
    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have integer value for "min_value". Got: "5".'
    )

    with pytest.raises(ValueError) as exception_info:
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value=5,
            max_value="X",
            default_value=11,
        )
    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have integer value for "max_value". Got: "X".'
    )


def test_get_value_unsigned():
    integer = Integer(
        name="", base_index=2, min_value=0, max_value=127, description="", default_value=0
    )
    assert integer.width == 7

    register_value = int("0101010_11", base=2)
    assert integer.get_value(register_value) == 42

    register_value = int("1010101_00", base=2)
    assert integer.get_value(register_value) == 85


def test_get_value_signed():
    integer = Integer(
        name="", base_index=3, min_value=-128, max_value=127, description="", default_value=0
    )
    assert integer.width == 8

    register_value = int("10101010_111", base=2)
    assert integer.get_value(register_value) == -86

    register_value = int("01010101_000", base=2)
    assert integer.get_value(register_value) == 85


def test_get_value_should_raise_exception_if_value_out_of_range():
    integer = Integer(
        name="apa", base_index=0, min_value=0, max_value=4, description="", default_value=0
    )
    assert integer.width == 3

    with pytest.raises(ValueError) as exception_info:
        integer.get_value(7)
    assert (
        str(exception_info.value)
        == 'Register field value "7" not inside "apa" field\'s legal range: (0, 4).'
    )


def test_set_value_unsigned():
    integer = Integer(
        name="", base_index=5, min_value=0, max_value=7, description="", default_value=0
    )
    assert integer.width == 3

    assert integer.set_value(5) == int("101_00000", base=2)
    assert integer.set_value(2) == int("010_00000", base=2)


def test_set_value_signed():
    integer = Integer(
        name="", base_index=5, min_value=-8, max_value=7, description="", default_value=0
    )
    assert integer.width == 4

    assert integer.set_value(5) == int("0101_00000", base=2)
    assert integer.set_value(-6) == int("1010_00000", base=2)


def test_set_value_should_raise_exception_if_value_out_of_range():
    integer = Integer(
        name="apa", base_index=5, min_value=-1, max_value=7, description="", default_value=0
    )

    with pytest.raises(ValueError) as exception_info:
        integer.set_value(-8)
    assert str(exception_info.value) == 'Value "-8" not inside "apa" field\'s legal range: (-1, 7).'


def test_default_value_uint():
    def _get_default_value_uint(min_value, max_value, default_value):
        return Integer(
            name="",
            base_index=0,
            description="",
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
        ).default_value_uint

    assert _get_default_value_uint(min_value=5, max_value=10, default_value=7) == 7
    assert _get_default_value_uint(min_value=-10, max_value=10, default_value=3) == 3

    # Negative values, converted to positive and sign extended to the width of the field.
    assert _get_default_value_uint(min_value=-10, max_value=10, default_value=-9) == 0b10111
    assert _get_default_value_uint(min_value=-10, max_value=10, default_value=-6) == 0b11010


def test_default_value_of_bad_type_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value=5,
            max_value=10,
            default_value="7",
        )
    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have integer value for "default_value". Got: "7".'
    )

    field = Integer(
        name="apa",
        base_index=0,
        description="",
        min_value=5,
        max_value=10,
        default_value=5,
    )

    with pytest.raises(ValueError) as exception_info:
        field.default_value = "8"
    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have integer value for "default_value". Got: "8".'
    )


def test_default_value_out_of_range_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value=5,
            max_value=10,
            default_value=11,
        )
    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have "default_value" within range [5, 10]. Got: "11".'
    )

    field = Integer(
        name="apa",
        base_index=0,
        description="",
        min_value=5,
        max_value=10,
        default_value=5,
    )

    with pytest.raises(ValueError) as exception_info:
        field.default_value = 120
    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have "default_value" within range [5, 10]. Got: "120".'
    )


def _get_field_width(min_value, max_value):
    return Integer(
        name="",
        base_index=0,
        description="",
        min_value=min_value,
        max_value=max_value,
        default_value=min_value,
    ).width


def test_unsigned_width():
    assert _get_field_width(min_value=0, max_value=127) == 7
    assert _get_field_width(min_value=0, max_value=128) == 8
    assert _get_field_width(min_value=0, max_value=255) == 8
    assert _get_field_width(min_value=0, max_value=256) == 9

    # The lower bound of the range does not affect the width
    # (but it will add checkers in our generated code).
    assert _get_field_width(min_value=255, max_value=255) == 8


def test_signed_width():
    # Positive range has greater demand than negative
    assert _get_field_width(min_value=-4, max_value=16) == 5 + 1
    assert _get_field_width(min_value=-4, max_value=4) == 3 + 1

    # Negative range has greater demand than positive
    assert _get_field_width(min_value=-7, max_value=2) == 4
    assert _get_field_width(min_value=-8, max_value=2) == 4
    assert _get_field_width(min_value=-9, max_value=2) == 5

    assert _get_field_width(min_value=-15, max_value=7) == 5
    assert _get_field_width(min_value=-16, max_value=7) == 5
    assert _get_field_width(min_value=-17, max_value=7) == 6

    # The upper bound of the range here does not affect the width
    # (but it will add checkers in our generated code).
    assert _get_field_width(min_value=-8, max_value=-3) == 4
    assert _get_field_width(min_value=-16, max_value=-4) == 5


def test_width_out_of_range_should_raise_exception():
    def _test_width_out_of_range(min_value, max_value):
        with pytest.raises(ValueError) as exception_info:
            _get_field_width(min_value=min_value, max_value=max_value)
        assert (
            str(exception_info.value)
            == f"Supplied integer range [{min_value}, {max_value}] does not fit in a register."
        )

    # Unsigned. Just within range, should not raise exception.
    _get_field_width(min_value=128, max_value=2**32 - 1)
    # Just outside of range.
    _test_width_out_of_range(min_value=128, max_value=2**32)

    # Signed, limited by negative range. Just within range, should not raise exception.
    _get_field_width(min_value=-(2**31), max_value=128)
    # Just outside of range.
    _test_width_out_of_range(min_value=-(2**31) - 1, max_value=128)

    # Signed, limited by positive range. Just within range, should not raise exception.
    _get_field_width(min_value=-128, max_value=2**31 - 1)
    # Just outside of range.
    _test_width_out_of_range(min_value=-128, max_value=2**31)
