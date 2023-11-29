# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
import pytest

# First party libraries
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.register_field_type import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)


def test_get_value():
    bit = BitVector(name="", base_index=2, description="", width=4, default_value="0000")

    register_value = int("111000011", base=2)
    assert bit.get_value(register_value) == 0

    register_value = int("000111100", base=2)
    assert bit.get_value(register_value) == 15

    register_value = int("101010101", base=2)
    assert bit.get_value(register_value) == 5

    # Test field_type
    field = BitVector(
        name="",
        base_index=2,
        description="",
        width=16,
        default_value="0" * 16,
        field_type=SignedFixedPoint.from_bit_widths(integer_bit_width=8, fraction_bit_width=8),
    )
    register_value = 0b11111111_00000011_11111111_11111100
    assert field.get_value(register_value) == -0.00390625


def test_max_binary_value():
    bit_vector = BitVector(
        name="", base_index=0, description="", width=2, default_value=format(0, "02b")
    )
    assert bit_vector.max_binary_value == 0b11

    bit_vector = BitVector(
        name="", base_index=0, description="", width=32, default_value=format(0, "032b")
    )
    assert bit_vector.max_binary_value == 0b11111111_11111111_11111111_11111111

    # Test with base_index > 0
    bit_vector = BitVector(
        name="", base_index=4, description="", width=4, default_value=format(0, "04b")
    )
    assert bit_vector.max_binary_value == 0b1111


def test_set_value():
    bit_vector = BitVector(
        name="", base_index=0, description="", width=2, default_value=format(0, "02b")
    )
    assert bit_vector.set_value(0b10) == 0b10
    assert bit_vector.set_value(0b11) == 0b11

    with pytest.raises(ValueError):
        bit_vector.set_value(0b111)

    bit_vector = BitVector(
        name="", base_index=2, description="", width=2, default_value=format(0, "02b")
    )
    assert bit_vector.set_value(0b10) == 0b1000

    bit_vector = BitVector(
        name="", base_index=3, description="", width=4, default_value=format(0, "04b")
    )
    assert bit_vector.set_value(0b1111) == 0b1111000

    bit_vector0 = BitVector(name="", base_index=0, description="", width=2, default_value="00")
    bit_vector1 = BitVector(name="", base_index=2, description="", width=4, default_value="0000")
    bit_vector2 = BitVector(name="", base_index=6, description="", width=3, default_value="000")

    register_value = int("111000011", base=2)
    value0 = bit_vector0.set_value(bit_vector0.get_value(register_value))
    value1 = bit_vector1.set_value(bit_vector1.get_value(register_value))
    value2 = bit_vector2.set_value(bit_vector2.get_value(register_value))
    assert value0 | value1 | value2 == register_value

    register_value = int("000111100", base=2)
    value0 = bit_vector0.set_value(bit_vector0.get_value(register_value))
    value1 = bit_vector1.set_value(bit_vector1.get_value(register_value))
    value2 = bit_vector2.set_value(bit_vector2.get_value(register_value))
    assert value0 | value1 | value2 == register_value

    register_value = int("101010101", base=2)
    value0 = bit_vector0.set_value(bit_vector0.get_value(register_value))
    value1 = bit_vector1.set_value(bit_vector1.get_value(register_value))
    value2 = bit_vector2.set_value(bit_vector2.get_value(register_value))
    assert value0 | value1 | value2 == register_value

    # Test field_type
    field = BitVector(
        name="",
        base_index=2,
        description="",
        width=16,
        default_value="0" * 16,
        field_type=SignedFixedPoint.from_bit_widths(integer_bit_width=8, fraction_bit_width=8),
    )
    assert field.set_value(-0.00390625) == 0b11_11111111_11111100


def test_repr():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(
        BitVector(name="apa", base_index=0, description="", width=1, default_value="0")
    )

    # Different name
    assert repr(
        BitVector(name="apa", base_index=0, description="", width=1, default_value="0")
    ) != repr(BitVector(name="hest", base_index=0, description="", width=1, default_value="0"))

    # Different base_index
    assert repr(
        BitVector(name="apa", base_index=0, description="", width=1, default_value="0")
    ) != repr(BitVector(name="apa", base_index=1, description="", width=1, default_value="0"))

    # Different description
    assert repr(
        BitVector(name="apa", base_index=0, description="Blah", width=1, default_value="0")
    ) != repr(BitVector(name="apa", base_index=0, description="Gaah", width=1, default_value="0"))

    # Different width
    assert repr(
        BitVector(name="apa", base_index=0, description="", width=1, default_value="1")
    ) != repr(BitVector(name="apa", base_index=0, description="", width=2, default_value="11"))

    # Different default_value
    assert repr(
        BitVector(name="apa", base_index=0, description="", width=1, default_value="1")
    ) != repr(BitVector(name="apa", base_index=0, description="", width=1, default_value="0"))

    # Different field_type
    field0 = BitVector(
        name="apa",
        base_index=0,
        description="",
        width=10,
        default_value="0" * 10,
        field_type=UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2),
    )
    field1 = BitVector(
        name="apa",
        base_index=0,
        description="",
        width=10,
        default_value="0" * 10,
        field_type=UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2),
    )
    field2 = BitVector(
        name="apa",
        base_index=0,
        description="",
        width=10,
        default_value="0" * 10,
        field_type=UnsignedFixedPoint(max_bit_index=8, min_bit_index=-1),
    )
    assert repr(field0) == repr(field1) != repr(field2)


def test_invalid_width():
    with pytest.raises(ValueError) as exception_info:
        BitVector(name="foo", base_index=0, width="4", description="", default_value="0000")
    assert (
        str(exception_info.value)
        == 'Bit vector "foo" should have integer value for "width". Got: "4".'
    )

    with pytest.raises(ValueError) as exception_info:
        BitVector(name="foo", base_index=0, width=33, description="", default_value="0")
    assert str(exception_info.value) == 'Invalid width for bit vector "foo". Got: "33".'

    with pytest.raises(ValueError) as exception_info:
        BitVector(name="foo", base_index=0, width=0, description="", default_value="0")
    assert str(exception_info.value) == 'Invalid width for bit vector "foo". Got: "0".'


def test_invalid_default_value_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        BitVector(name="hest", base_index=0, description="", width=4, default_value=1111)
    assert str(exception_info.value) == (
        'Bit vector "hest" should have string value for "default_value". Got: "1111"'
    )

    with pytest.raises(ValueError) as exception_info:
        BitVector(name="hest", base_index=0, description="", width=4, default_value="11")
    assert str(exception_info.value) == (
        'Bit vector "hest" should have "default_value" of length 4. Got: "11".'
    )

    with pytest.raises(ValueError) as exception_info:
        BitVector(name="hest", base_index=0, description="", width=4, default_value="1121")
    assert str(exception_info.value) == (
        'Bit vector "hest" invalid binary value for "default_value". Got: "1121".'
    )


def test_can_update_default_value():
    bit_vector = BitVector(name="hest", base_index=0, description="", width=4, default_value="1111")
    assert bit_vector.default_value == "1111"

    bit_vector.default_value = "0000"
    assert bit_vector.default_value == "0000"


def test_updating_to_invalid_default_value_should_raise_exception():
    # Create with a valid default_value
    bit_vector = BitVector(name="hest", base_index=0, description="", width=4, default_value="1111")

    # Update to an invalid value
    with pytest.raises(ValueError) as exception_info:
        bit_vector.default_value = 1111
    assert str(exception_info.value) == (
        'Bit vector "hest" should have string value for "default_value". Got: "1111"'
    )


def test_default_value_uint():
    bit_vector = BitVector(name="apa", base_index=0, description="", width=4, default_value="0000")
    assert bit_vector.default_value_uint == 0

    bit_vector.default_value = "0010"
    assert bit_vector.default_value_uint == 2

    bit_vector.default_value = "1001"
    assert bit_vector.default_value_uint == 9


def test_field_type():
    bit_vector = BitVector(name="", base_index=0, description="", width=4, default_value="1111")
    assert isinstance(bit_vector.field_type, Unsigned)

    bit_vector = BitVector(
        name="", base_index=0, description="", width=4, default_value="1111", field_type=Unsigned()
    )
    assert isinstance(bit_vector.field_type, Unsigned)

    bit_vector = BitVector(
        name="", base_index=0, description="", width=4, default_value="1111", field_type=Signed()
    )
    assert isinstance(bit_vector.field_type, Signed)

    bit_vector = BitVector(
        name="",
        base_index=0,
        description="",
        width=10,
        default_value="1" * 10,
        field_type=SignedFixedPoint(max_bit_index=7, min_bit_index=-2),
    )
    assert isinstance(bit_vector.field_type, SignedFixedPoint)
    assert bit_vector.field_type.max_bit_index == 7
    assert bit_vector.field_type.min_bit_index == -2

    bit_vector = BitVector(
        name="",
        base_index=0,
        description="",
        width=10,
        default_value="1" * 10,
        field_type=UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2),
    )
    assert isinstance(bit_vector.field_type, UnsignedFixedPoint)
    assert bit_vector.field_type.max_bit_index == 7
    assert bit_vector.field_type.min_bit_index == -2


def test_invalid_field_type_width_should_raise_exception():
    def test(field_type):
        with pytest.raises(ValueError) as exception_info:
            BitVector(
                name="apa",
                base_index=0,
                description="",
                width=4,
                default_value="1111",
                field_type=field_type,
            )

        type_width = field_type.integer_bit_width + field_type.fraction_bit_width
        expected = (
            f'Inconsistent width for bit vector "apa". Field is "4" bits, type is "{type_width}".'
        )
        assert str(exception_info.value) == expected

    test(SignedFixedPoint(max_bit_index=7, min_bit_index=0))
    test(UnsignedFixedPoint(max_bit_index=9, min_bit_index=-3))

    test(SignedFixedPoint(max_bit_index=5, min_bit_index=0))
    test(UnsignedFixedPoint(max_bit_index=3, min_bit_index=-3))
