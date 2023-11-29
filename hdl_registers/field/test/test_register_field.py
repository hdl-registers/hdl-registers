# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.field.register_field import RegisterField


def test_range_str():
    class MyField(RegisterField):
        base_index = 3
        width = 1
        default_value_str = ""
        default_value_uint = 0

        def __repr__(self) -> str:
            return ""

    assert MyField().range_str == "3"

    class MyOtherField(RegisterField):
        base_index = 4
        width = 8
        default_value_str = ""
        default_value_uint = 0

        def __repr__(self) -> str:
            return ""

    assert MyOtherField().range_str == "11:4"
