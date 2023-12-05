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
from hdl_registers.constant.boolean_constant import BooleanConstant


def test_constant():
    for value in [True, False]:
        constant = BooleanConstant(name="apa", value=value, description=f"desc {value}")

        assert constant.name == "apa"
        assert constant.value == value
        assert constant.description == f"desc {value}"


def test_invalid_data_type():
    with pytest.raises(ValueError) as exception_info:
        BooleanConstant(name="apa", value=3.5)
    assert (
        str(exception_info.value)
        == 'Constant "apa" has invalid data type "<class \'float\'>". Value: "3.5".'
    )


def test_repr():
    data = BooleanConstant(name="apa", value=True)

    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(data)
    assert repr(data) == repr(copy(data))

    # Different name
    other = BooleanConstant(name="hest", value=True)
    assert repr(data) != repr(other)

    # Different value
    other = BooleanConstant(name="apa", value=False)
    assert repr(data) != repr(other)

    # Different description
    data = BooleanConstant(name="apa", value=True, description="X")
    assert repr(data) != repr(other)
