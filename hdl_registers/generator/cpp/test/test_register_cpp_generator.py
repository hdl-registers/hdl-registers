# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Some limited unit tests that check the generated code.
# Note that the generated C++ code is also functionally tested in the
# file 'test_compiled_cpp_code.py'.
# That test generates C++ code from an example register set, compiles it and performs some
# run-time assertions in a C program.
# That test is considered more meaningful and exhaustive than a unit test would be.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from tsfpga.system_utils import read_file

from hdl_registers import HDL_REGISTERS_TESTS
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    UnsignedFixedPoint,
)
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES

if TYPE_CHECKING:
    from hdl_registers.field.register_field import RegisterField


@pytest.fixture
def cpp_test_toml_code(tmp_path):
    registers = from_toml("test", HDL_REGISTERS_TESTS / "regs_test.toml")

    return read_file(
        CppInterfaceGenerator(register_list=registers, output_folder=tmp_path).create()
    )


def test_read_only_register_has_no_setters(cpp_test_toml_code):
    assert "get_status" in cpp_test_toml_code
    assert "set_status" not in cpp_test_toml_code


def test_write_only_register_has_no_setters(cpp_test_toml_code):
    assert "set_command" in cpp_test_toml_code
    assert "get_command" not in cpp_test_toml_code


@pytest.fixture
def cpp_range_test():
    class Checker:
        def __init__(self):
            self.register_list = RegisterList(name="test")
            self.register = self.register_list.append_register(
                name="register", mode=REGISTER_MODES["r_w"], description=""
            )

            # Output folder does not matter.
            self.generator = CppImplementationGenerator(
                register_list=self.register_list,
                output_folder=HDL_REGISTERS_TESTS / "cpp_test",
            )

        def get_cpp(self, field: RegisterField, setter_or_getter: str):
            # It's hard to test this using the public interface.
            # Would be sketchy to find the checker code of the specific field within all the
            # generated code.
            # So we use the private method, bad practice as it may be.
            return self.generator._get_field_checker(  # noqa: SLF001
                field=field, setter_or_getter=setter_or_getter
            )

        def check(
            self,
            field: RegisterField,
            getter: tuple[int | None, int | None],
            setter: tuple[int | None, int | None],
        ):
            def _check(cpp: str, min_check: int | None, max_check: int | None):
                if min_check is None:
                    assert "field_value >=" not in cpp
                else:
                    assert f"field_value >= {min_check}" in cpp

                if max_check is None:
                    assert "field_value <=" not in cpp
                else:
                    assert f"field_value <= {max_check}" in cpp

            getter_code = self.get_cpp(field=field, setter_or_getter="getter")
            _check(cpp=getter_code, min_check=getter[0], max_check=getter[1])

            setter_code = self.get_cpp(field=field, setter_or_getter="setter")
            _check(cpp=setter_code, min_check=setter[0], max_check=setter[1])

    return Checker()


def test_field_range_check_bit(cpp_range_test):
    field = cpp_range_test.register.append_bit(name="a", description="", default_value="0")
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, None))


def test_field_range_check_bit_vector_unsigned(cpp_range_test):
    field = cpp_range_test.register.append_bit_vector(
        name="a", description="", width=4, default_value="0000"
    )
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, 15))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_bit_vector(name="a", description="", width=32, default_value=32 * "0")
    # Width now matches 'uint32_t'.
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, None))


def test_field_range_check_bit_vector_signed(cpp_range_test):
    field = cpp_range_test.register.append_bit_vector(
        name="a",
        description="",
        width=4,
        default_value="0000",
        numerical_interpretation=Signed(bit_width=4),
    )
    cpp_range_test.check(field=field, getter=(None, None), setter=(-8, 7))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_bit_vector(
        name="a",
        description="",
        width=32,
        default_value=32 * "0",
        numerical_interpretation=Signed(bit_width=32),
    )
    # Width now matches 'int32_t'.
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, None))


def test_field_range_check_bit_vector_ufixed(cpp_range_test):
    field = cpp_range_test.register.append_bit_vector(
        name="a",
        description="",
        width=4,
        default_value="0000",
        numerical_interpretation=UnsignedFixedPoint(max_bit_index=1, min_bit_index=-2),
    )
    cpp_range_test.check(field=field, getter=(None, None), setter=(0.0, 3.75))


def test_field_range_check_bit_vector_sfixed(cpp_range_test):
    field = cpp_range_test.register.append_bit_vector(
        name="a",
        description="",
        width=4,
        default_value="0000",
        numerical_interpretation=SignedFixedPoint(max_bit_index=1, min_bit_index=-2),
    )
    cpp_range_test.check(field=field, getter=(None, None), setter=(-2, 1.75))


def test_field_range_check_enumeration(cpp_range_test):
    field = cpp_range_test.register.append_enumeration(
        name="a", description="", elements={"a": "", "b": "", "c": ""}, default_value="a"
    )
    cpp_range_test.check(field=field, getter=(None, 2), setter=(None, 2))

    field = cpp_range_test.register.append_enumeration(
        name="b", description="", elements={"a": "", "b": "", "c": "", "d": ""}, default_value="a"
    )
    # Upper limit is now the native width of the field.
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, 3))


def test_field_range_check_integer_unsigned(cpp_range_test):
    field = cpp_range_test.register.append_integer(
        name="a", description="", min_value=0, max_value=13, default_value=0
    )
    cpp_range_test.check(field=field, getter=(None, 13), setter=(None, 13))

    field = cpp_range_test.register.append_integer(
        name="a", description="", min_value=0, max_value=15, default_value=0
    )
    # Upper limit is now the native width of the field.
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, 15))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_integer(
        name="a", description="", min_value=0, max_value=4294967294, default_value=0
    )
    # Width matches 'uint32_t', but upper limit is not native.
    cpp_range_test.check(field=field, getter=(None, 4294967294), setter=(None, 4294967294))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_integer(
        name="a", description="", min_value=0, max_value=4294967295, default_value=0
    )
    # Upper limit is the native width of the field and matches 'uint32_t'.
    cpp_range_test.check(field=field, getter=(None, None), setter=(None, None))


def test_field_range_check_integer_signed(cpp_range_test):
    field = cpp_range_test.register.append_integer(
        name="a", description="", min_value=-1, max_value=13, default_value=0
    )
    cpp_range_test.check(field=field, getter=(-1, 13), setter=(-1, 13))

    field = cpp_range_test.register.append_integer(
        name="a", description="", min_value=-16, max_value=13, default_value=0
    )
    # Lower limit is now the native width of the field.
    cpp_range_test.check(field=field, getter=(None, 13), setter=(-16, 13))

    field = cpp_range_test.register.append_integer(
        name="a", description="", min_value=-16, max_value=15, default_value=0
    )
    # Upper limit is now the native width of the field.
    cpp_range_test.check(field=field, getter=(None, None), setter=(-16, 15))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_integer(
        name="a", description="", min_value=-2147483647, max_value=13, default_value=0
    )
    # Lower limit matches 'int32_t' but is not native.
    cpp_range_test.check(field=field, getter=(-2147483647, 13), setter=(-2147483647, 13))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_integer(
        name="a", description="", min_value=-2147483648, max_value=13, default_value=0
    )
    # Lower limit is the native width of the field and matches 'int32_t'.
    cpp_range_test.check(field=field, getter=(None, 13), setter=(None, 13))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_integer(
        name="a", description="", min_value=-1, max_value=2147483644, default_value=0
    )
    # Upper limit matches 'int32_t' but is not native.
    cpp_range_test.check(field=field, getter=(-1, 2147483644), setter=(-1, 2147483644))

    register = cpp_range_test.register_list.append_register(
        name="register", mode=REGISTER_MODES["r_w"], description=""
    )
    field = register.append_integer(
        name="a", description="", min_value=-1, max_value=2147483647, default_value=0
    )
    # Upper limit is the native width of the field and matches 'int32_t'.
    cpp_range_test.check(field=field, getter=(-1, None), setter=(-1, None))
