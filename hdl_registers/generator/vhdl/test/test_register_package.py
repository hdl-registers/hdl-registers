# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

"""
Some limited unit tests that check the generated code.
Note that the generated VHDL code is also simulated in a functional test.
"""

import pytest
from tsfpga.system_utils import read_file

from hdl_registers import HDL_REGISTERS_TESTS
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


def get_package(register_list, output_folder):
    return read_file(VhdlRegisterPackageGenerator(register_list, output_folder).create())


class RegisterConfigurationTest:
    def __init__(self, name, source_toml_file):
        self.register_list = from_toml(name=name, toml_file=source_toml_file)

        self.register_list.add_constant(name="boolean_constant", value=True, description="")
        self.register_list.add_constant(name="integer_constant", value=3, description="")
        self.register_list.add_constant(name="real_constant", value=3.14, description="")
        self.register_list.add_constant(name="real_big_constant", value=1e20, description="")
        self.register_list.add_constant(name="real_small_constant", value=4e-8, description="")
        self.register_list.add_constant(name="string_constant", value="apa", description="")

    def test_vhdl_package(self, output_path, test_registers, test_constants):
        vhdl = get_package(register_list=self.register_list, output_folder=output_path)

        if test_registers:
            assert "constant test_register_map : " in vhdl, vhdl
        else:
            assert "constant test_register_map : " not in vhdl, vhdl

        if test_constants:
            assert "constant test_constant_boolean_constant : boolean := true;" in vhdl, vhdl
            assert "constant test_constant_integer_constant : integer := 3;" in vhdl, vhdl
            assert "constant test_constant_real_constant : real := 3.14;" in vhdl, vhdl
            assert "constant test_constant_real_big_constant : real := 1.0e+20;" in vhdl, vhdl
            assert "constant test_constant_real_small_constant : real := 4.0e-08;" in vhdl, vhdl
            assert 'constant test_constant_string_constant : string := "apa";' in vhdl, vhdl
            assert (
                "constant test_constant_base_address_hex : "
                'unsigned(36 - 1 downto 0) := x"8_0000_0000";' in vhdl
            ), vhdl
            assert (
                "constant test_constant_base_address_bin : "
                'unsigned(36 - 1 downto 0) := "100000000000000000000000000000000000";' in vhdl
            ), vhdl
        else:
            assert "boolean_constant" not in vhdl, vhdl
            assert "integer_constant" not in vhdl, vhdl
            assert "real_constant" not in vhdl, vhdl
            assert "string_constant" not in vhdl, vhdl


@pytest.fixture
def register_configuration():
    return RegisterConfigurationTest("test", HDL_REGISTERS_TESTS / "regs_test.toml")


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
    Test that register_map constant has valid VHDL syntax even when there is only one register.
    """
    register_list = RegisterList(name="apa", source_definition_file=None)
    register_list.append_register(
        name="hest", mode=REGISTER_MODES["r"], description="a single register"
    )
    vhdl = read_file(VhdlRegisterPackageGenerator(register_list, tmp_path).create())

    expected = """
  constant apa_register_map : register_definition_vec_t(apa_register_range) := (
    0 => (index => apa_hest, mode => r, utilized_width => 32)
  );

  constant apa_regs_init : apa_regs_t := (
    0 => "00000000000000000000000000000000"
  );
"""
    assert expected in vhdl, vhdl


def test_vhdl_typedef(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    register = register_list.append_register("number", REGISTER_MODES["r_w"], "")

    register.append_bit_vector(
        name="u0",
        description="",
        width=2,
        default_value="11",
        numerical_interpretation=Unsigned(bit_width=2),
    )

    register.append_bit_vector(
        name="s0",
        description="",
        width=2,
        default_value="11",
        numerical_interpretation=Signed(bit_width=2),
    )

    register.append_bit_vector(
        name="ufixed0",
        description="",
        width=2,
        default_value="11",
        numerical_interpretation=UnsignedFixedPoint(-1, -2),
    )
    register.append_bit_vector(
        name="ufixed1",
        description="",
        width=8,
        default_value="1" * 8,
        numerical_interpretation=UnsignedFixedPoint(5, -2),
    )

    register.append_bit_vector(
        name="sfixed0",
        description="",
        width=2,
        default_value="11",
        numerical_interpretation=SignedFixedPoint(-1, -2),
    )
    register.append_bit_vector(
        name="sfixed1",
        description="",
        width=6,
        default_value="1" * 6,
        numerical_interpretation=SignedFixedPoint(5, 0),
    )

    register.append_integer(
        name="integer0", description="", min_value=1, max_value=3, default_value=2
    )

    vhdl = read_file(VhdlRegisterPackageGenerator(register_list, tmp_path).create())

    assert "subtype test_number_u0_t is u_unsigned(1 downto 0);" in vhdl, vhdl

    assert "subtype test_number_s0_t is u_signed(1 downto 0);" in vhdl, vhdl

    assert "subtype test_number_ufixed0_t is ufixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype test_number_ufixed1_t is ufixed(5 downto -2);" in vhdl, vhdl

    assert "subtype test_number_sfixed0_t is sfixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype test_number_sfixed1_t is sfixed(5 downto 0);" in vhdl, vhdl

    assert "subtype test_number_integer0_t is integer range 1 to 3;" in vhdl, vhdl


def test_address_width(tmp_path):
    register_list = RegisterList(name="apa", source_definition_file=None)
    constant_name = "apa_address_width"

    def check(num_addressing_bits):
        assert f"{constant_name} : positive := {num_addressing_bits + 2}" in get_package(
            register_list, tmp_path
        )

    assert constant_name not in get_package(register_list, tmp_path)

    register_list.append_register("a", REGISTER_MODES["r"], "")
    check(1)

    register_list.append_register("b", REGISTER_MODES["r"], "")
    check(1)

    register_list.append_register("c", REGISTER_MODES["r"], "")
    check(2)

    register_list.append_register_array("d", 2, "").append_register("e", REGISTER_MODES["r"], "")
    check(3)
