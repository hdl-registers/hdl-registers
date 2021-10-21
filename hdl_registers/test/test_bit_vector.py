# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import pytest

from tsfpga.registers.bit_vector import BitVector


def test_get_value():
    bit = BitVector(name="", base_index=2, description="", width=4, default_value="0000")

    register_value = int("111000011", base=2)
    assert bit.get_value(register_value) == 0

    register_value = int("000111100", base=2)
    assert bit.get_value(register_value) == 15

    register_value = int("101010101", base=2)
    assert bit.get_value(register_value) == 5


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


def test_invalid_width():
    with pytest.raises(ValueError) as exception_info:
        BitVector(name="foo", base_index=0, width="4", description="", default_value="0000")
    assert (
        str(exception_info.value)
        == 'Bit vector "foo" should have integer value for "width". Got: "4".'
    )

    with pytest.raises(ValueError) as exception_info:
        BitVector(name="foo", base_index=0, width=33, description="", default_value="0")
    assert str(exception_info.value) == 'Invalid bit vector width for "foo". Got: "33".'

    with pytest.raises(ValueError) as exception_info:
        BitVector(name="foo", base_index=0, width=0, description="", default_value="0")
    assert str(exception_info.value) == 'Invalid bit vector width for "foo". Got: "0".'


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
