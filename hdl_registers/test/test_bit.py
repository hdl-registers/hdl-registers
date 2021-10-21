# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import pytest

from tsfpga.registers.bit import Bit


def test_get_value():
    bit = Bit(name="", index=2, description="", default_value="1")

    register_value = int("1111011", base=2)
    assert bit.get_value(register_value) == 0

    register_value = int("0000100", base=2)
    assert bit.get_value(register_value) == 1


def test_repr():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(Bit(name="apa", index=0, description="", default_value="0"))

    # Different name
    assert repr(Bit(name="apa", index=0, description="", default_value="0")) != repr(
        Bit(name="hest", index=0, description="", default_value="0")
    )

    # Different index
    assert repr(Bit(name="apa", index=0, description="", default_value="0")) != repr(
        Bit(name="apa", index=1, description="", default_value="0")
    )

    # Different description
    assert repr(Bit(name="apa", index=0, description="Blah", default_value="0")) != repr(
        Bit(name="apa", index=0, description="Gaah", default_value="0")
    )

    # Different default_value
    assert repr(Bit(name="apa", index=0, description="", default_value="1")) != repr(
        Bit(name="apa", index=0, description="", default_value="0")
    )


def test_default_value_uint():
    assert Bit(name="apa", index=0, description="", default_value="1").default_value_uint == 1
    assert Bit(name="apa", index=0, description="", default_value="0").default_value_uint == 0


def test_invalid_default_value_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Bit(name="hest", index=0, description="", default_value=1)
    assert str(exception_info.value) == (
        'Bit "hest" should have string value for "default_value". Got "1".'
    )

    with pytest.raises(ValueError) as exception_info:
        Bit(name="hest", index=0, description="", default_value="11")
    assert str(exception_info.value) == (
        'Bit "hest" invalid binary value for "default_value". Got: "11".'
    )

    with pytest.raises(ValueError) as exception_info:
        Bit(name="hest", index=0, description="", default_value="2")
    assert str(exception_info.value) == (
        'Bit "hest" invalid binary value for "default_value". Got: "2".'
    )


def test_can_update_default_value():
    bit = Bit(name="hest", index=0, description="", default_value="1")
    assert bit.default_value == "1"

    bit.default_value = "0"
    assert bit.default_value == "0"


def test_updating_to_invalid_default_value_should_raise_exception():
    # Create with a valid default_value
    bit = Bit(name="hest", index=0, description="", default_value="1")

    # Update to an invalid value
    with pytest.raises(ValueError) as exception_info:
        bit.default_value = "2"
    assert str(exception_info.value) == (
        'Bit "hest" invalid binary value for "default_value". Got: "2".'
    )
