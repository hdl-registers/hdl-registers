# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
import pytest

# First party libraries
from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers
from hdl_registers.register import Register
from hdl_registers.register_modes import REGISTER_MODES


def test_field_setter_should_read_modify_write():
    register = Register(name="", index=0, mode=REGISTER_MODES["r_w"], description="")

    register.append_bit(name="", description="", default_value="0")
    assert not RegisterCodeGeneratorHelpers.field_setter_should_read_modify_write(register)

    register.append_bit(name="", description="", default_value="0")
    assert RegisterCodeGeneratorHelpers.field_setter_should_read_modify_write(register)

    register.append_bit(name="", description="", default_value="0")
    assert RegisterCodeGeneratorHelpers.field_setter_should_read_modify_write(register)


def test_field_setter_should_read_modify_write_should_raise_exception_if_there_are_no_fields():
    register = Register(name="", index=0, mode=REGISTER_MODES["r_w"], description="")

    with pytest.raises(AssertionError) as exception_info:
        RegisterCodeGeneratorHelpers.field_setter_should_read_modify_write(register)
    assert str(exception_info.value) == "Should not end up here if the register has no fields."


def test_field_setter_should_read_modify_write_raise_exception_if_the_register_is_not_writable():
    register = Register(name="", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit(name="", description="", default_value="0")

    with pytest.raises(ValueError) as exception_info:
        RegisterCodeGeneratorHelpers.field_setter_should_read_modify_write(register)
    assert str(exception_info.value).startswith("Got non-writeable register:")


def test_to_pascal_case():
    assert RegisterCodeGeneratorHelpers.to_pascal_case("test") == "Test"
    assert RegisterCodeGeneratorHelpers.to_pascal_case("test_two") == "TestTwo"
