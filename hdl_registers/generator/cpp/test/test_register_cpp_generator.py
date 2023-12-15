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

# Third party libraries
import pytest
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers import HDL_REGISTERS_TESTS
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.parser.toml import from_toml


@pytest.fixture
def cpp_test_toml_code(tmp_path):
    registers = from_toml("test", HDL_REGISTERS_TESTS / "regs_test.toml")

    return read_file(
        CppInterfaceGenerator(register_list=registers, output_folder=tmp_path).create()
    )


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_read_only_register_has_no_setters(cpp_test_toml_code):
    assert "get_status" in cpp_test_toml_code
    assert "set_status" not in cpp_test_toml_code


def test_write_only_register_has_no_setters(cpp_test_toml_code):
    assert "set_command" in cpp_test_toml_code
    assert "get_command" not in cpp_test_toml_code
