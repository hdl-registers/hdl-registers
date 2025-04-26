# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import pytest

from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers
from hdl_registers.register import Register
from hdl_registers.register_modes import REGISTER_MODES


def test_register_utilized_width():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")

    assert RegisterCodeGeneratorHelpers.register_utilized_width(register) == 32

    register.append_bit(name="a", description="", default_value="1")
    assert RegisterCodeGeneratorHelpers.register_utilized_width(register) == 1

    register.append_bit_vector(name="b", description="", width=2, default_value="11")
    assert RegisterCodeGeneratorHelpers.register_utilized_width(register) == 3

    register.append_enumeration(
        name="c", description="", elements={"d": "", "e": "", "f": ""}, default_value="d"
    )
    assert RegisterCodeGeneratorHelpers.register_utilized_width(register) == 5

    register.append_integer(name="g", description="", min_value=0, max_value=10, default_value=0)
    assert RegisterCodeGeneratorHelpers.register_utilized_width(register) == 9


def test_register_default_value_uint():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit(name="foo", description="", default_value="1")
    register.append_bit(name="foo", description="", default_value="0")
    register.append_bit(name="foo", description="", default_value="1")
    register.append_bit_vector(name="foo", description="", width=4, default_value="0110")
    register.append_bit_vector(name="foo", description="", width=4, default_value="0101")

    assert (
        RegisterCodeGeneratorHelpers.register_default_value_uint(register)
        == 1 * 2**0 + 1 * 2**2 + 6 * 2**3 + 5 * 2**7
    )


def test_default_value_can_be_updated():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit(name="foo", description="", default_value="1")

    assert RegisterCodeGeneratorHelpers.register_default_value_uint(register) == 1

    register.fields[0].default_value = "0"
    assert RegisterCodeGeneratorHelpers.register_default_value_uint(register) == 0


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

    with pytest.raises(ValueError) as exception_info:
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
