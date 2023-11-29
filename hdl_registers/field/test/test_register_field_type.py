# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------
# pylint: disable=protected-access

# Third party libraries
import pytest

# First party libraries
from hdl_registers.field.register_field_type import (
    FieldType,
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)


@pytest.mark.parametrize(
    "field_type, bit_width, min_value, max_value",
    [
        (Unsigned(), 2, 0.0, 3),
        (Unsigned(), 8, 0.0, 255),
        (Signed(), 2, -2, 1),
        (Signed(), 6, -32, 31),
        (Signed(), 8, -128, 127),
        (UnsignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 2, 0.0, 0.75),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=-2), 8, 0.0, 63.75),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=0), 6, 0.0, 63),
        (SignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 2, -0.5, 0.25),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2), 8, -32, 31.75),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=0), 6, -32, 31),
    ],
)
def test_min_max_zero(field_type, bit_width, min_value, max_value):
    assert field_type.min_value(bit_width) == min_value
    assert field_type.max_value(bit_width) == max_value
    assert field_type.convert_to_unsigned_binary(bit_width, 0.0) == 0b0


@pytest.mark.parametrize(
    "field_type, bit_width",
    [
        (Unsigned(), 2),
        (Unsigned(), 8),
        (Signed(), 2),
        (Signed(), 6),
        (Signed(), 8),
        (UnsignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 2),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=-2), 8),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=0), 6),
        (SignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 2),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2), 8),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=0), 6),
    ],
)
def test_zero_min_max_restore(field_type, bit_width):
    value = 0
    field_type._check_value_in_range(bit_width, value)
    unsigned = field_type.convert_to_unsigned_binary(bit_width, value)
    assert unsigned == 0x0
    restored = field_type.convert_from_unsigned_binary(bit_width, unsigned)
    assert restored == value

    value = field_type.min_value(bit_width)
    field_type._check_value_in_range(bit_width, value)
    unsigned = field_type.convert_to_unsigned_binary(bit_width, value)
    restored = field_type.convert_from_unsigned_binary(bit_width, unsigned)
    assert restored == value

    value = field_type.max_value(bit_width)
    field_type._check_value_in_range(bit_width, value)
    unsigned = field_type.convert_to_unsigned_binary(bit_width, value)
    restored = field_type.convert_from_unsigned_binary(bit_width, unsigned)
    assert restored == value


@pytest.mark.parametrize(
    "field_type, bit_width",
    [
        (Unsigned(), 2),
        (Unsigned(), 8),
        (Signed(), 2),
        (Signed(), 6),
        (Signed(), 8),
        (UnsignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 2),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=-2), 8),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=0), 6),
        (SignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 2),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2), 8),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=0), 6),
    ],
)
def test_out_of_range(field_type: FieldType, bit_width: int):
    value = field_type.min_value(bit_width) - 0.00001
    with pytest.raises(ValueError):
        field_type._check_value_in_range(bit_width, value)
    with pytest.raises(ValueError):
        field_type.convert_to_unsigned_binary(bit_width, value)

    value = field_type.max_value(bit_width) + 0.00001
    with pytest.raises(ValueError):
        field_type._check_value_in_range(bit_width, value)
    with pytest.raises(ValueError):
        field_type.convert_to_unsigned_binary(bit_width, value)


@pytest.mark.parametrize(
    "bit_width, value, expected",
    [
        (8, 1, 0b00000001),
        (8, -1, 0b11111111),
        (8, 40, 0b00101000),
        (8, -40, 0b11011000),
        (8, 126, 0b01111110),
        (8, -126, 0b10000010),
    ],
)
def test_singed(bit_width, value, expected):
    field_type = Signed()
    field_type._check_value_in_range(bit_width, value)
    unsigned = field_type.convert_to_unsigned_binary(bit_width, value)
    assert unsigned == expected
    restored = field_type.convert_from_unsigned_binary(bit_width, unsigned)
    assert restored == value


@pytest.mark.parametrize(
    "bit_width, max_bit_index, min_bit_index, value, exp_uint, exp_return",
    [
        (1, -1, -1, 0.00, 0b0, 0.00),
        (1, -1, -1, 0.25, 0b0, 0.00),
        (1, -1, -1, 0.50, 0b1, 0.50),
        (2, -1, -2, 0.00, 0b00, 0.00),
        (2, -1, -2, 0.25, 0b01, 0.25),
        (2, -1, -2, 0.50, 0b10, 0.50),
        (2, -1, -2, 0.75, 0b11, 0.75),
        (2, -1, -2, 0.125, 0b000, 0.00),
        (3, -1, -3, 0.125, 0b001, 0.125),
        (4, 0, -3, 1.125, 0b1001, 1.125),
        (9, 4, -4, 9.75, 0b010011100, 9.75),
        (7, 3, -3, 4.625, 0b0100101, 4.625),
        (2, 9, 8, 256.0, 0b01, 256.0),
        (2, 9, 8, 768.0, 0b11, 768.0),
        (2, -2, -3, 0.375, 0b11, 0.375),
        (2, -3, -4, 0.1875, 0b11, 0.1875),
        (10, 4, -5, 6.5, 0b0011010000, 6.5),
    ],
)
def test_ufixed(bit_width, max_bit_index, min_bit_index, value, exp_uint, exp_return):
    field_type = UnsignedFixedPoint(max_bit_index=max_bit_index, min_bit_index=min_bit_index)
    field_type._check_value_in_range(bit_width, value)
    unsigned = field_type.convert_to_unsigned_binary(bit_width, value)
    assert unsigned == exp_uint
    restored = field_type.convert_from_unsigned_binary(bit_width, unsigned)
    assert restored == exp_return


@pytest.mark.parametrize(
    "bit_width, max_bit_index, min_bit_index, value, expected",
    [
        (2, -1, -2, -0.25, 0b11),
        (2, -1, -2, 0.25, 0b01),
        (9, 4, -4, 9.75, 0b010011100),
        (10, 5, -4, -13.8125, 0b1100100011),
        (2, 9, 8, 256.0, 0b01),
        (2, 9, 8, -256.0, 0b11),
        (2, -2, -3, -0.125, 0b11),
        (2, -3, -4, -0.0625, 0b11),
        (10, 4, -5, -6.5, 0b1100110000),
    ],
)
def test_sfixed(bit_width, max_bit_index, min_bit_index, value, expected):
    field_type = SignedFixedPoint(max_bit_index=max_bit_index, min_bit_index=min_bit_index)
    field_type._check_value_in_range(bit_width, value)
    unsigned = field_type.convert_to_unsigned_binary(bit_width, value)
    assert unsigned == expected
    restored = field_type.convert_from_unsigned_binary(bit_width, unsigned)
    assert restored == value


@pytest.mark.parametrize(
    "field_type_class, integer_bit_width, fraction_bit_width",
    [
        (UnsignedFixedPoint, 9, 2),
        (UnsignedFixedPoint, 11, -8),
        (UnsignedFixedPoint, -1, 3),
        (SignedFixedPoint, 9, 2),
        (SignedFixedPoint, 11, -8),
        (SignedFixedPoint, -1, 3),
    ],
)
def test_via_bit_widths(field_type_class, integer_bit_width, fraction_bit_width):
    field_type = field_type_class.from_bit_widths(
        integer_bit_width=integer_bit_width, fraction_bit_width=fraction_bit_width
    )
    assert field_type.integer_bit_width == integer_bit_width
    assert field_type.fraction_bit_width == fraction_bit_width


def test_repr():
    unsigned0 = Unsigned()
    unsigned1 = Unsigned()
    signed0 = Signed()
    signed1 = Signed()
    ufixed0 = UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    ufixed1 = UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    ufixed2 = UnsignedFixedPoint(max_bit_index=8, min_bit_index=-2)
    sfixed0 = SignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    sfixed1 = SignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    sfixed2 = SignedFixedPoint(max_bit_index=8, min_bit_index=-2)

    assert repr(unsigned0) == repr(unsigned1)
    assert repr(signed0) == repr(signed1)
    assert repr(ufixed0) == repr(ufixed1) != repr(ufixed2)
    assert repr(sfixed0) == repr(sfixed1) != repr(sfixed2)
    assert repr(ufixed0) != repr(sfixed0) != repr(ufixed0) != repr(sfixed0)
