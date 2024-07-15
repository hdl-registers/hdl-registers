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
from hdl_registers.generator.vhdl.simulation.check_package import (
    VhdlSimulationCheckPackageGenerator,
)
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


def test_package_is_not_generated_without_registers(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)

    assert not VhdlSimulationCheckPackageGenerator(register_list, tmp_path).create().exists()

    register_list.add_constant(name="apa", value=True, description="")
    assert not VhdlSimulationCheckPackageGenerator(register_list, tmp_path).create().exists()

    register_list.append_register(name="hest", mode=REGISTER_MODES["r_w"], description="")
    assert VhdlSimulationCheckPackageGenerator(register_list, tmp_path).create().exists()


def test_re_generating_package_without_registers_should_delete_old_file(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    register_list.append_register(name="apa", mode=REGISTER_MODES["r_w"], description="")

    assert VhdlSimulationCheckPackageGenerator(register_list, tmp_path).create().exists()

    register_list.register_objects = []
    assert not VhdlSimulationCheckPackageGenerator(register_list, tmp_path).create().exists()


def test_only_readable_registers_are_included(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)

    register_list.append_register(
        name="include_r", mode=REGISTER_MODES["r"], description=""
    ).append_bit(name="", description="", default_value="0")
    register_list.append_register(
        name="exclude_w", mode=REGISTER_MODES["w"], description=""
    ).append_bit(name="", description="", default_value="0")
    register_list.append_register(
        name="include_r_w", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit(name="", description="", default_value="0")
    register_list.append_register(
        name="exclude_wpulse", mode=REGISTER_MODES["wpulse"], description=""
    ).append_bit(name="", description="", default_value="0")
    register_list.append_register(
        name="include_r_wpulse", mode=REGISTER_MODES["r_wpulse"], description=""
    ).append_bit(name="", description="", default_value="0")

    vhdl = read_file(VhdlSimulationCheckPackageGenerator(register_list, tmp_path).create())

    assert "include_r" in vhdl
    assert "include_r_w" in vhdl
    assert "include_r_wpulse" in vhdl
    assert "exclude" not in vhdl
