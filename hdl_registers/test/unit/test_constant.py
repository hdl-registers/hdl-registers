# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path

# Third party libraries
import pytest

# First party libraries
from hdl_registers.constant import Constant


def test_boolean():
    for value in [True, False]:
        constant = Constant(name="apa", value=value)

        assert constant.is_boolean
        assert not constant.is_integer
        assert not constant.is_float
        assert not constant.is_string


def test_integer():
    for value in [123, -9]:
        constant = Constant(name="apa", value=value)

        assert not constant.is_boolean
        assert constant.is_integer
        assert not constant.is_float
        assert not constant.is_string


def test_float():
    for value in [3.14, -9.9]:
        constant = Constant(name="apa", value=value)

        assert not constant.is_boolean
        assert not constant.is_integer
        assert constant.is_float
        assert not constant.is_string


def test_string():
    for value in ["", "hello"]:
        constant = Constant(name="apa", value=value)

        assert not constant.is_boolean
        assert not constant.is_integer
        assert not constant.is_float
        assert constant.is_string


def test_invalid_data_type():
    with pytest.raises(ValueError) as exception_info:
        Constant(name="apa", value=Path())
    assert (
        str(exception_info.value)
        == 'Constant "apa" has invalid data type "<class \'pathlib.PosixPath\'>". Value: "."'
    )


def test_repr():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(Constant(name="apa", value=0))

    # Different name
    assert repr(Constant(name="apa", value=0)) != repr(Constant(name="hest", value=0))

    # Different value
    assert repr(Constant(name="apa", value=0)) != repr(Constant(name="apa", value=1))

    # Different description
    assert repr(Constant(name="apa", value=0, description="Blah")) != repr(
        Constant(name="apa", value=0, description="Gaah")
    )
