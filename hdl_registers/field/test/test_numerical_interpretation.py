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
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)


@pytest.mark.parametrize(
    "numerical_interpretation, min_value, max_value",
    [
        (Unsigned(bit_width=2), 0.0, 3),
        (Unsigned(bit_width=8), 0.0, 255),
        (Signed(bit_width=2), -2, 1),
        (Signed(bit_width=6), -32, 31),
        (Signed(bit_width=8), -128, 127),
        (UnsignedFixedPoint(max_bit_index=-1, min_bit_index=-2), 0.0, 0.75),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=-2), 0.0, 63.75),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=0), 0.0, 63),
        (SignedFixedPoint(max_bit_index=-1, min_bit_index=-2), -0.5, 0.25),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2), -32, 31.75),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=0), -32, 31),
    ],
)
def test_min_max_zero(numerical_interpretation, min_value, max_value):
    assert numerical_interpretation.min_value == min_value
    assert numerical_interpretation.max_value == max_value
    assert numerical_interpretation.convert_to_unsigned_binary(0.0) == 0b0


@pytest.mark.parametrize(
    "numerical_interpretation",
    [
        (Unsigned(bit_width=2)),
        (Unsigned(bit_width=8)),
        (Signed(bit_width=2)),
        (Signed(bit_width=6)),
        (Signed(bit_width=8)),
        (UnsignedFixedPoint(max_bit_index=-1, min_bit_index=-2)),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=-2)),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=0)),
        (SignedFixedPoint(max_bit_index=-1, min_bit_index=-2)),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2)),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=0)),
    ],
)
def test_zero_min_max_restore(numerical_interpretation):
    value = 0
    numerical_interpretation._check_native_value_in_range(value)
    unsigned = numerical_interpretation.convert_to_unsigned_binary(value)
    assert unsigned == 0x0
    restored = numerical_interpretation.convert_from_unsigned_binary(unsigned)
    assert restored == value

    value = numerical_interpretation.min_value
    numerical_interpretation._check_native_value_in_range(value)
    unsigned = numerical_interpretation.convert_to_unsigned_binary(value)
    restored = numerical_interpretation.convert_from_unsigned_binary(unsigned)
    assert restored == value

    value = numerical_interpretation.max_value
    numerical_interpretation._check_native_value_in_range(value)
    unsigned = numerical_interpretation.convert_to_unsigned_binary(value)
    restored = numerical_interpretation.convert_from_unsigned_binary(unsigned)
    assert restored == value


@pytest.mark.parametrize(
    "numerical_interpretation",
    [
        (Unsigned(bit_width=2)),
        (Unsigned(bit_width=8)),
        (Signed(bit_width=2)),
        (Signed(bit_width=6)),
        (Signed(bit_width=8)),
        (UnsignedFixedPoint(max_bit_index=-1, min_bit_index=-2)),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=-2)),
        (UnsignedFixedPoint(max_bit_index=5, min_bit_index=0)),
        (SignedFixedPoint(max_bit_index=-1, min_bit_index=-2)),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2)),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=0)),
    ],
)
def test_out_of_range(numerical_interpretation):
    value = numerical_interpretation.min_value - 0.00001
    with pytest.raises(ValueError):
        numerical_interpretation._check_native_value_in_range(value)
    with pytest.raises(ValueError):
        numerical_interpretation.convert_to_unsigned_binary(value)

    value = numerical_interpretation.max_value + 0.00001
    with pytest.raises(ValueError):
        numerical_interpretation._check_native_value_in_range(value)
    with pytest.raises(ValueError):
        numerical_interpretation.convert_to_unsigned_binary(value)


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
def test_signed(bit_width, value, expected):
    numerical_interpretation = Signed(bit_width=bit_width)
    numerical_interpretation._check_native_value_in_range(value)

    unsigned = numerical_interpretation.convert_to_unsigned_binary(value)
    assert unsigned == expected

    restored = numerical_interpretation.convert_from_unsigned_binary(unsigned)
    assert restored == value


@pytest.mark.parametrize(
    "max_bit_index, min_bit_index, value, exp_uint, exp_return",
    [
        (-1, -1, 0.00, 0b0, 0.00),
        (-1, -1, 0.25, 0b0, 0.00),
        (-1, -1, 0.50, 0b1, 0.50),
        (-1, -2, 0.00, 0b00, 0.00),
        (-1, -2, 0.25, 0b01, 0.25),
        (-1, -2, 0.50, 0b10, 0.50),
        (-1, -2, 0.75, 0b11, 0.75),
        (-1, -2, 0.125, 0b000, 0.00),
        (-1, -3, 0.125, 0b001, 0.125),
        (0, -3, 1.125, 0b1001, 1.125),
        (4, -4, 9.75, 0b010011100, 9.75),
        (3, -3, 4.625, 0b0100101, 4.625),
        (9, 8, 256.0, 0b01, 256.0),
        (9, 8, 768.0, 0b11, 768.0),
        (-2, -3, 0.375, 0b11, 0.375),
        (-3, -4, 0.1875, 0b11, 0.1875),
        (4, -5, 6.5, 0b0011010000, 6.5),
    ],
)
def test_ufixed(max_bit_index, min_bit_index, value, exp_uint, exp_return):
    numerical_interpretation = UnsignedFixedPoint(
        max_bit_index=max_bit_index, min_bit_index=min_bit_index
    )

    numerical_interpretation._check_native_value_in_range(value)

    unsigned = numerical_interpretation.convert_to_unsigned_binary(value)
    assert unsigned == exp_uint

    restored = numerical_interpretation.convert_from_unsigned_binary(unsigned)
    assert restored == exp_return


@pytest.mark.parametrize(
    "max_bit_index, min_bit_index, value, expected",
    [
        (-1, -2, -0.25, 0b11),
        (-1, -2, 0.25, 0b01),
        (4, -4, 9.75, 0b010011100),
        (5, -4, -13.8125, 0b1100100011),
        (9, 8, 256.0, 0b01),
        (9, 8, -256.0, 0b11),
        (-2, -3, -0.125, 0b11),
        (-3, -4, -0.0625, 0b11),
        (4, -5, -6.5, 0b1100110000),
    ],
)
def test_sfixed(max_bit_index, min_bit_index, value, expected):
    numerical_interpretation = SignedFixedPoint(
        max_bit_index=max_bit_index, min_bit_index=min_bit_index
    )
    numerical_interpretation._check_native_value_in_range(value)

    unsigned = numerical_interpretation.convert_to_unsigned_binary(value)
    assert unsigned == expected

    restored = numerical_interpretation.convert_from_unsigned_binary(unsigned)
    assert restored == value


@pytest.mark.parametrize(
    "numerical_interpretation_class, integer_bit_width, fraction_bit_width",
    [
        (UnsignedFixedPoint, 9, 2),
        (UnsignedFixedPoint, 11, -8),
        (UnsignedFixedPoint, -1, 3),
        (SignedFixedPoint, 9, 2),
        (SignedFixedPoint, 11, -8),
        (SignedFixedPoint, -1, 3),
    ],
)
def test_via_bit_widths(numerical_interpretation_class, integer_bit_width, fraction_bit_width):
    numerical_interpretation = numerical_interpretation_class.from_bit_widths(
        integer_bit_width=integer_bit_width, fraction_bit_width=fraction_bit_width
    )
    assert numerical_interpretation.integer_bit_width == integer_bit_width
    assert numerical_interpretation.fraction_bit_width == fraction_bit_width


@pytest.mark.parametrize(
    "numerical_interpretation",
    [
        (Unsigned(bit_width=8)),
        (Signed(bit_width=8)),
        (UnsignedFixedPoint(max_bit_index=4, min_bit_index=-3)),
        (SignedFixedPoint(max_bit_index=5, min_bit_index=-2)),
    ],
)
def test_convert_from_unsigned_binary_value_out_of_range_should_raise_exception(
    numerical_interpretation,
):
    assert numerical_interpretation.bit_width == 8

    numerical_interpretation.convert_from_unsigned_binary(0)
    with pytest.raises(ValueError) as exception_info:
        numerical_interpretation.convert_from_unsigned_binary(-1)
    assert str(exception_info.value).startswith("Value: -1 out of range of 8-bit ")

    numerical_interpretation.convert_from_unsigned_binary(255)
    with pytest.raises(ValueError) as exception_info:
        numerical_interpretation.convert_from_unsigned_binary(256)
    assert str(exception_info.value).startswith("Value: 256 out of range of 8-bit ")


def test_repr():
    unsigned0 = Unsigned(2)
    unsigned1 = Unsigned(2)
    unsigned2 = Unsigned(3)
    signed0 = Signed(2)
    signed1 = Signed(2)
    signed2 = Signed(3)
    ufixed0 = UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    ufixed1 = UnsignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    ufixed2 = UnsignedFixedPoint(max_bit_index=8, min_bit_index=-2)
    sfixed0 = SignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    sfixed1 = SignedFixedPoint(max_bit_index=7, min_bit_index=-2)
    sfixed2 = SignedFixedPoint(max_bit_index=8, min_bit_index=-2)

    assert repr(unsigned0) == repr(unsigned1) != repr(unsigned2)
    assert repr(signed0) == repr(signed1) != repr(signed2)
    assert repr(unsigned0) != repr(signed0)

    assert repr(ufixed0) == repr(ufixed1) != repr(ufixed2)
    assert repr(sfixed0) == repr(sfixed1) != repr(sfixed2)
    assert repr(ufixed0) != repr(sfixed0)
