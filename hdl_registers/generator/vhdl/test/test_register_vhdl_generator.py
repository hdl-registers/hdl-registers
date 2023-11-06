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
from hdl_registers.field.register_field_type import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.parser import from_toml
from hdl_registers.register_list import RegisterList


class RegisterConfiguration:
    def __init__(self, module_name, source_toml_file):
        self.register_list = from_toml(module_name=module_name, toml_file=source_toml_file)

        self.register_list.add_constant(name="boolean_constant", value=True, description="")
        self.register_list.add_constant(name="integer_constant", value=3, description="")
        self.register_list.add_constant(name="real_constant", value=3.14, description="")
        self.register_list.add_constant(name="string_constant", value="apa", description="")

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
    register = register_list.append_register("number", "r_w", "")

    register.append_bit_vector(
        name="u0", description="", width=2, default_value="11", field_type=Unsigned()
    )

    register.append_bit_vector(
        name="s0", description="", width=2, default_value="11", field_type=Signed()
    )

    register.append_bit_vector(
        name="ufixed0",
        description="",
        width=2,
        default_value="11",
        field_type=UnsignedFixedPoint(-1, -2),
    )
    register.append_bit_vector(
        name="ufixed1",
        description="",
        width=8,
        default_value="1" * 8,
        field_type=UnsignedFixedPoint(5, -2),
    )

    register.append_bit_vector(
        name="sfixed0",
        description="",
        width=2,
        default_value="11",
        field_type=SignedFixedPoint(-1, -2),
    )
    register.append_bit_vector(
        name="sfixed1",
        description="",
        width=6,
        default_value="1" * 6,
        field_type=SignedFixedPoint(5, 0),
    )

    register.append_integer(
        name="integer0", description="", min_value=1, max_value=3, default_value=2
    )

    register_list.create_vhdl_package(tmp_path)
    vhdl = read_file(tmp_path / "test_regs_pkg.vhd")

    assert "subtype test_number_u0_t is u_unsigned(1 downto 0);" in vhdl, vhdl

    assert "subtype test_number_s0_t is u_signed(1 downto 0);" in vhdl, vhdl

    assert "subtype test_number_ufixed0_t is ufixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype test_number_ufixed1_t is ufixed(5 downto -2);" in vhdl, vhdl

    assert "subtype test_number_sfixed0_t is sfixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype test_number_sfixed1_t is sfixed(5 downto 0);" in vhdl, vhdl

    assert "subtype test_number_integer0_t is integer range 1 to 3;" in vhdl, vhdl


def generate_strange_register_maps(output_path):
    """
    Generate register VHDL artifacts for some strange niche cases.
    """

    def create_packages(direction, mode):
        def append_register(data, name):
            """
            Append a register with some fields.
            """
            register = data.append_register(name=f"{name}_{mode}", mode=mode, description="")

            register.append_integer(
                name="int", description="", min_value=-10, max_value=10, default_value=3
            )
            register.append_enumeration(
                name="enum", description="", elements=dict(a="", b=""), default_value="b"
            )

        def append_registers(data):
            """
            Append some registers with some fields, either to a RegisterList or a RegisterArray.
            """
            append_register(data=data, name="first")
            append_register(data=data, name="second")

        # Some plain registers, in one direction only.
        register_list = RegisterList(name=f"plain_only_{direction}")
        append_registers(data=register_list)
        register_list.create_vhdl_package(output_path=output_path)

        # Some register arrays, in one direction only.
        register_list = RegisterList(name=f"array_only_{direction}")
        register_array = register_list.append_register_array(name="apa", length=5, description="")
        append_registers(data=register_array)
        register_array = register_list.append_register_array(name="hest", length=10, description="")
        append_registers(data=register_array)
        register_list.create_vhdl_package(output_path=output_path)

        # Plain registers and some register arrays, in one direction only.
        register_list = RegisterList(name=f"plain_and_array_only_{direction}")
        append_registers(data=register_list)
        register_array = register_list.append_register_array(name="apa", length=5, description="")
        append_registers(data=register_array)
        register_array = register_list.append_register_array(name="hest", length=10, description="")
        append_registers(data=register_array)
        register_list.create_vhdl_package(output_path=output_path)

    # Mode 'Read only' should give registers only in the 'up' direction'
    create_packages(direction="up", mode="r")
    # Mode 'Write only' should give registers only in the 'down' direction'
    create_packages(direction="down", mode="w")


def _get_register_arrays_record_string(direction):
    return (
        f"records for the registers of each register array the are in the '{direction}' direction"
    )


def test_registers_only_in_up_direction_should_give_no_down_type_or_port(tmp_path):
    generate_strange_register_maps(output_path=tmp_path)

    for file_name in ["array_only_up", "plain_and_array_only_up", "plain_only_up"]:
        vhd = read_file(tmp_path / f"{file_name}_regs_pkg.vhd")

        assert f"{file_name}_regs_up_t" in vhd
        assert f"{file_name}_regs_down_t" not in vhd

        # If there are no arrays there should be no records for arrays, and this comment shall not
        # be present.
        string = _get_register_arrays_record_string("up")
        if "array" in file_name:
            assert string in vhd
        else:
            assert string not in vhd

        # The 'down' comment shall never be present since we have no 'down' registers.
        string = _get_register_arrays_record_string("down")
        assert string not in vhd

        vhd = read_file(tmp_path / f"{file_name}_reg_file.vhd")

        assert "regs_up : in" in vhd
        assert "regs_down : out" not in vhd

        assert "reg_was_read : out" in vhd
        assert "reg_was_written : out" not in vhd


def test_registers_only_in_down_direction_should_give_no_down_type_or_port(tmp_path):
    generate_strange_register_maps(output_path=tmp_path)

    for file_name in ["array_only_down", "plain_and_array_only_down", "plain_only_down"]:
        vhd = read_file(tmp_path / f"{file_name}_regs_pkg.vhd")

        assert f"{file_name}_regs_up_t" not in vhd
        assert f"{file_name}_regs_down_t" in vhd

        # If there are no arrays there should be no records for arrays, and this comment shall not
        # be present.
        string = _get_register_arrays_record_string("down")
        if "array" in file_name:
            assert string in vhd
        else:
            assert string not in vhd

        # The 'up' comment shall never be present since we have no 'up' registers.
        string = _get_register_arrays_record_string("up")
        assert string not in vhd

        vhd = read_file(tmp_path / f"{file_name}_reg_file.vhd")

        assert "regs_up : in" not in vhd
        assert "regs_down : out" in vhd

        assert "reg_was_read : out" not in vhd
        assert "reg_was_written : out" in vhd
