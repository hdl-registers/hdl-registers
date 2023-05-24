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
from pathlib import Path

# Third party libraries
import pytest

# First party libraries
from hdl_registers.constant.float_constant import FloatConstant


def test_constant():
    for value in [3.14, -9.9]:
        constant = FloatConstant(name="apa", value=value, description=f"desc {value}")

        assert constant.name == "apa"
        assert constant.value == value
        assert constant.description == f"desc {value}"


def test_invalid_data_type():
    with pytest.raises(ValueError) as exception_info:
        FloatConstant(name="apa", value=Path())
    assert (
        str(exception_info.value)
        == 'Constant "apa" has invalid data type "<class \'pathlib.PosixPath\'>". Value: ".".'
    )


def test_repr():
    data = FloatConstant(name="apa", value=3.14)

    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(data)
    assert repr(data) == repr(copy(data))

    # Different name
    other = FloatConstant(name="hest", value=3.14)
    assert repr(data) != repr(other)

    # Different value
    other = FloatConstant(name="apa", value=4.2)
    assert repr(data) != repr(other)

    # Different description
    data = FloatConstant(name="apa", value=3.14, description="X")
    assert repr(data) != repr(other)
