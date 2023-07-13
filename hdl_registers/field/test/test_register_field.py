# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.field.register_field import RegisterField


def test_register_field():
    class MyField(RegisterField):
        base_index = 3
        width = 1
        default_value_str = None
        default_value_uint = None

    assert MyField().range_str == "3"

    class MyOtherField(RegisterField):
        base_index = 4
        width = 8
        default_value_str = None
        default_value_uint = None

    assert MyOtherField().range_str == "11:4"
