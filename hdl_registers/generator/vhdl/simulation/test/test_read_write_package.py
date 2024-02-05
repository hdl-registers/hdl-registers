# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

"""
Some limited unit tests.
Note that the generated VHDL code is also simulated in a functional test.
"""

# Third party libraries
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers.field.register_field_type import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.generator.vhdl.simulation.read_write_package import (
    VhdlSimulationReadWritePackageGenerator,
)
from hdl_registers.register_list import RegisterList


def test_package_is_not_generated_without_registers(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)

    assert not VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create().exists()

    register_list.add_constant(name="apa", value=True, description="")
    assert not VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create().exists()

    register_list.append_register(name="hest", mode="r_w", description="")
    assert VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create().exists()


def test_re_generating_package_without_registers_should_delete_old_file(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    register_list.append_register(name="apa", mode="r_w", description="")

    assert VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create().exists()

    register_list.register_objects = []
    assert not VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create().exists()


def test_read_write_as_integer(tmp_path):
    register_list = RegisterList(name="caesar", source_definition_file=None)

    register_list.append_register(name="empty", mode="r_w", description="")

    register = register_list.append_register(name="full", mode="r_w", description="")
    register.append_bit(name="my_bit", description="", default_value="0")
    register.append_enumeration(
        name="my_enumeration",
        description="",
        elements={"first": "", "second": ""},
        default_value="first",
    )
    register.append_integer(
        name="my_integer", description="", min_value=0, max_value=127, default_value=0
    )
    register.append_bit_vector(
        name="my_signed_bit_vector",
        description="",
        width=4,
        default_value="0000",
        field_type=Signed(),
    )
    register.append_bit_vector(
        name="my_sfixed_bit_vector",
        description="",
        width=4,
        default_value="0000",
        field_type=SignedFixedPoint(1, -2),
    )
    register.append_bit_vector(
        name="my_unsigned_bit_vector",
        description="",
        width=4,
        default_value="0000",
        field_type=Unsigned(),
    )
    register.append_bit_vector(
        name="my_ufixed_bit_vector",
        description="",
        width=4,
        default_value="0000",
        field_type=UnsignedFixedPoint(1, -2),
    )

    vhdl = read_file(VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create())

    def check_access_as_integer(direction: str, name: str) -> None:
        assert direction in ["read", "write"]
        in_or_out = "in" if direction == "write" else "out"
        expected = f"""
  procedure {direction}_caesar_{name}(
    signal net : inout network_t;
    value : {in_or_out} integer;
"""
        return expected in vhdl

    for direction in ["read", "write"]:
        # Empty register should have a method to access it as an integer.
        assert check_access_as_integer(direction=direction, name="empty")
        # Not a registers with fields though.
        assert not check_access_as_integer(direction=direction, name="full")

        # Only non-fractional vector types shall have the possibility of accessing as integer.
        assert check_access_as_integer(direction=direction, name="full_my_signed_bit_vector")
        assert check_access_as_integer(direction=direction, name="full_my_unsigned_bit_vector")
        assert not check_access_as_integer(direction=direction, name="full_my_ufixed_bit_vector")
        assert not check_access_as_integer(direction=direction, name="full_my_sfixed_bit_vector")
        assert not check_access_as_integer(direction=direction, name="full_my_bit")
        assert not check_access_as_integer(direction=direction, name="full_my_enumeration")
        assert not check_access_as_integer(direction=direction, name="full_my_integer")
