# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

"""
Some limited unit tests that check the generated code.

It is also functionally tested in the file tb_generated_vhdl_package.vhd.
That testbench compiles the VHDL package and performs some run-time assertions on the
generated values. That test is considered more meaningful and exhaustive than a unit test would be.
"""

# Third party libraries
import pytest
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.parser import from_toml
from hdl_registers.register_field_type import Signed, SignedFixedPoint, Unsigned, UnsignedFixedPoint
from hdl_registers.register_list import RegisterList


class RegisterConfiguration:
    def __init__(self, module_name, source_toml_file):
        self.register_list = from_toml(module_name=module_name, toml_file=source_toml_file)

        self.register_list.add_constant(name="boolean_constant", value=True)
        self.register_list.add_constant(name="integer_constant", value=3)
        self.register_list.add_constant(name="real_constant", value=3.14)
        self.register_list.add_constant(name="string_constant", value="apa")

    def test_vhdl_package(self, output_path, test_registers, test_constants):
        self.register_list.create_vhdl_package(output_path)
        vhdl = read_file(output_path / "test_regs_pkg.vhd")

        if test_registers:
            assert "constant test_reg_map : " in vhdl, vhdl
        else:
            assert "constant test_reg_map : " not in vhdl, vhdl

        if test_constants:
            assert "constant test_constant_boolean_constant : boolean := true;" in vhdl, vhdl
            assert "constant test_constant_integer_constant : integer := 3;" in vhdl, vhdl
            assert "constant test_constant_real_constant : real := 3.14;" in vhdl, vhdl
            assert 'constant test_constant_string_constant : string := "apa";' in vhdl, vhdl
        else:
            assert "boolean_constant" not in vhdl, vhdl
            assert "integer_constant" not in vhdl, vhdl
            assert "real_constant" not in vhdl, vhdl
            assert "string_constant" not in vhdl, vhdl


@pytest.fixture
def register_configuration():
    return RegisterConfiguration("test", HDL_REGISTERS_TEST / "regs_test.toml")


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
    0 => "00000000000000000000000000000000"
  );
"""
    assert expected in vhdl, vhdl


def test_vhdl_typedef(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    number = register_list.append_register("number", "r_w", "")
    number.append_bit_vector("udata0", "expected u_unsigned(1 downto 0)", 2, "11", Unsigned())
    number.append_bit_vector("sdata0", "expected u_signed(1 downto 0)", 2, "11", Signed())
    number.append_bit_vector(
        "ufixed0", "expected ufixed(1 downto 0)", 2, "11", UnsignedFixedPoint(-1, -2)
    )
    number.append_bit_vector(
        "ufixed1", "expected ufixed(5 downto -2)", 8, "1" * 8, UnsignedFixedPoint(5, -2)
    )
    number.append_bit_vector(
        "ufixed1", "expected ufixed(5 downto -2)", 8, "1" * 8, UnsignedFixedPoint(5, -2)
    )
    number.append_bit_vector(
        "sfixed0", "expected sfixed(-1 downto -2)", 2, "11", SignedFixedPoint(-1, -2)
    )
    number.append_bit_vector(
        "sfixed0", "expected sfixed(5 downto 0)", 6, "1" * 6, SignedFixedPoint(5, 0)
    )

    register_list.create_vhdl_package(tmp_path)
    vhdl = read_file(tmp_path / "test_regs_pkg.vhd")

    assert "subtype test_number_udata0_t is u_unsigned(1 downto 0);" in vhdl, vhdl
    assert "subtype test_number_sdata0_t is u_signed(1 downto 0);" in vhdl, vhdl
    assert "subtype test_number_ufixed0_t is ufixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype test_number_ufixed1_t is ufixed(5 downto -2);" in vhdl, vhdl
    assert "subtype test_number_sfixed0_t is sfixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype test_number_sfixed0_t is sfixed(5 downto 0);" in vhdl, vhdl
