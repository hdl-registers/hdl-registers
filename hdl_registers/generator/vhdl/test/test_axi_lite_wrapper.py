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

# First party libraries
from hdl_registers.generator.vhdl.axi_lite_wrapper import VhdlAxiLiteWrapperGenerator
from hdl_registers.register_list import RegisterList


def test_generating_a_register_list_with_no_registers_should_give_no_file(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    register_list.add_constant(name="value", value=123, description="")

    VhdlAxiLiteWrapperGenerator(register_list, tmp_path).create()
    assert not (tmp_path / "test_reg_file.vhd").exists()


def test_regenerating_a_register_list_with_no_registers_should_delete_file(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    register_list.append_register(name="value", mode="r_w", description="")

    VhdlAxiLiteWrapperGenerator(register_list, tmp_path).create()
    assert (tmp_path / "test_reg_file.vhd").exists()

    register_list = RegisterList(name="test", source_definition_file=None)
    VhdlAxiLiteWrapperGenerator(register_list, tmp_path).create()
    assert not (tmp_path / "test_reg_file.vhd").exists()
