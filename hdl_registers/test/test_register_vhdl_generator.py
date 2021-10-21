# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

"""
Some limited unit tests that check the generated code.

It is also functionally tested in the file tb_artyz.vhd.
That testbench compiles the VHDL package and performs some run-time assertions on the
generated values. That test is considered more meaningful and exhaustive than a unit test would be.
"""

import pytest

import tsfpga
from tsfpga.system_utils import read_file
from tsfpga.registers.parser import from_toml
from tsfpga.registers.register_list import RegisterList


class RegisterConfiguration:
    def __init__(self, module_name, source_toml_file):
        self.register_list = from_toml(module_name, source_toml_file)
        self.register_list.add_constant("dummy_constant", "3")
        self.register_list.add_constant("flappy_constant", "91")

    def test_vhdl_package(self, output_path, test_registers, test_constants):
        self.register_list.create_vhdl_package(output_path)
        vhdl = read_file(output_path / "artyz7_regs_pkg.vhd")

        if test_registers:
            assert "constant artyz7_reg_map : " in vhdl, vhdl
        else:
            assert "constant artyz7_reg_map : " not in vhdl, vhdl

        if test_constants:
            assert "constant artyz7_constant_dummy_constant : integer := 3;" in vhdl, vhdl
        else:
            assert "constant artyz7_constant_dummy_constant : integer := 3;" not in vhdl, vhdl


@pytest.fixture
def register_configuration():
    return RegisterConfiguration(
        "artyz7", tsfpga.TSFPGA_EXAMPLE_MODULES / "artyz7" / "regs_artyz7.toml"
    )


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_vhdl_package_with_registers_and_constants(tmp_path, register_configuration):
    register_configuration.test_vhdl_package(tmp_path, test_registers=True, test_constants=True)


def test_vhdl_package_with_registers_and_no_constants(tmp_path, register_configuration):
    register_configuration.register_list.constants = []
    register_configuration.test_vhdl_package(tmp_path, test_registers=True, test_constants=False)


def test_vhdl_package_with_constants_and_no_registers(tmp_path, register_configuration):
    register_configuration.register_list.register_objects = []
    register_configuration.test_vhdl_package(tmp_path, test_registers=False, test_constants=True)


def test_vhdl_package_with_only_one_register(tmp_path):
    """
    Test that reg_map constant has valid VHDL syntax even when there is only one register.
    """
    register_list = RegisterList(name="apa", source_definition_file=None)
    register_list.append_register(name="hest", mode="r", description="a single register")
    register_list.create_vhdl_package(tmp_path)
    vhdl = read_file(tmp_path / "apa_regs_pkg.vhd")

    expected = """
  constant apa_reg_map : reg_definition_vec_t(apa_reg_range) := (
    0 => (idx => apa_hest, reg_type => r)
  );

  constant apa_regs_init : apa_regs_t := (
    0 => std_logic_vector(to_signed(0, 32))
  );
"""
    assert expected in vhdl, vhdl
