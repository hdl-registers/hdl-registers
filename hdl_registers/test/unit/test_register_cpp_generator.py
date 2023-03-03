# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import unittest

# Third party libraries
import pytest
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.parser import from_toml


@pytest.mark.usefixtures("fixture_tmp_path")
class TestRegisterCppGenerator(unittest.TestCase):
    """
    Note that there are further tests in test_register_compilation.py.
    """

    tmp_path = None

    def setUp(self):
        toml_file = HDL_REGISTERS_TEST / "regs_test.toml"
        self.registers = from_toml("test", toml_file)

        self.registers.create_cpp_interface(self.tmp_path)
        self.cpp = read_file(self.tmp_path / "i_test.h")

    def test_read_only_register_has_no_setters(self):
        assert "get_status" in self.cpp
        assert "set_status" not in self.cpp

    def test_write_only_register_has_no_setters(self):
        assert "set_command" in self.cpp
        assert "get_command" not in self.cpp
