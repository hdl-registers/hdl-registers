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
from hdl_registers.constant.bit_vector_constant import BitVectorConstant, UnsignedVectorConstant


def test_unsigned_hexadecimal():
    constant = UnsignedVectorConstant(name="apa", value="0x10a_BCdef", description="hest")

    assert constant.name == "apa"
    assert constant.prefix == "0x"
    assert constant.value == "10a_BCdef"
    assert constant.value_without_separator == "10aBCdef"
    assert constant.description == "hest"
    assert constant.is_hexadecimal_not_binary
    assert constant.width == 32


def test_unsigned_binary():
    constant = UnsignedVectorConstant(name="apa", value="0b10_01", description="hest")

    assert constant.name == "apa"
    assert constant.prefix == "0b"
    assert constant.value == "10_01"
    assert constant.value_without_separator == "1001"
    assert constant.description == "hest"
    assert not constant.is_hexadecimal_not_binary
    assert constant.width == 4


def test_illegal_prefix_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        UnsignedVectorConstant(name="apa", value="123")
    assert (
        str(exception_info.value)
        == 'Constant "apa" value must start with a correct prefix. Value: "123".'
    )

    with pytest.raises(ValueError) as exception_info:
        UnsignedVectorConstant(name="apa", value="0b")
    assert (
        str(exception_info.value)
        == 'Constant "apa" value must start with a correct prefix. Value: "0b".'
    )

    with pytest.raises(ValueError) as exception_info:
        UnsignedVectorConstant(name="apa", value="0x")
    assert (
        str(exception_info.value)
        == 'Constant "apa" value must start with a correct prefix. Value: "0x".'
    )

    # Check also via setter
    constant = UnsignedVectorConstant(name="apa", value="0b11")

    with pytest.raises(ValueError) as exception_info:
        constant.value = "456"
    assert (
        str(exception_info.value)
        == 'Constant "apa" value must start with a correct prefix. Value: "456".'
    )

    with pytest.raises(ValueError) as exception_info:
        constant.value = "0b"
    assert (
        str(exception_info.value)
        == 'Constant "apa" value must start with a correct prefix. Value: "0b".'
    )

    with pytest.raises(ValueError) as exception_info:
        constant.value = "0x"
    assert (
        str(exception_info.value)
        == 'Constant "apa" value must start with a correct prefix. Value: "0x".'
    )


def test_illegal_value_type_should_raise_exception():
    with pytest.raises(TypeError) as exception_info:
        UnsignedVectorConstant(name="apa", value=123)
    assert (
        str(exception_info.value)
        == 'Constant "apa" has invalid data type "<class \'int\'>". Value: "123".'
    )

    constant = UnsignedVectorConstant(name="apa", value="0b11")
    with pytest.raises(TypeError) as exception_info:
        constant.value = 456
    assert (
        str(exception_info.value)
        == 'Constant "apa" has invalid data type "<class \'int\'>". Value: "456".'
    )


def test_illegal_hexadecimal_character_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        UnsignedVectorConstant(name="apa", value="0xABC01X")
    assert (
        str(exception_info.value)
        == 'Constant "apa" contains illegal character "X". Value: "0xABC01X".'
    )

    constant = UnsignedVectorConstant(name="apa", value="0x123")
    with pytest.raises(ValueError) as exception_info:
        constant.value = "0x1230Z"
    assert (
        str(exception_info.value)
        == 'Constant "apa" contains illegal character "Z". Value: "0x1230Z".'
    )


def test_repr():
    data = BitVectorConstant(name="apa", value="0b00")

    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(data)
    assert repr(data) == repr(copy(data))

    # Different name
    other = BitVectorConstant(name="hest", value="0b00")
    assert repr(data) != repr(other)

    # Different value
    other = BitVectorConstant(name="apa", value="0xff")
    assert repr(data) != repr(other)

    # Different prefix
    other = BitVectorConstant(name="apa", value="0x00")
    assert repr(data) != repr(other)

    # Different description
    data = BitVectorConstant(name="apa", value="0b00", description="X")
    assert repr(data) != repr(other)
