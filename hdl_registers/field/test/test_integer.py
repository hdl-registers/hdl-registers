# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
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


def test_negative_range_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Integer(
            name="apa",
            base_index=0,
            description="",
            min_value=-10,
            max_value=10,
            default_value=0,
        )

    assert (
        str(exception_info.value)
        == 'Integer field "apa" should have a non-negative range. Got: [-10, 10].'
    )


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


def test_width():
    def get_width(min_value, max_value):
        return Integer(
            name="",
            base_index=0,
            description="",
            min_value=min_value,
            max_value=max_value,
            default_value=min_value,
        ).width

    assert get_width(min_value=0, max_value=127) == 7
    assert get_width(min_value=0, max_value=128) == 8
    assert get_width(min_value=0, max_value=255) == 8
    assert get_width(min_value=0, max_value=256) == 9

    # The lower bound of the range does not affect the width
    # (but it will add checkers in our generated code).
    assert get_width(min_value=255, max_value=255) == 8
