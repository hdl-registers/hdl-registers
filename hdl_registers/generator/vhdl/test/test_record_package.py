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

# First party libraries
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
from hdl_registers.register_list import RegisterList


def test_package_is_not_generated_without_registers(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)

    assert not (VhdlRecordPackageGenerator(register_list, tmp_path).create()).exists()

    register_list.add_constant(name="apa", value=True, description="")
    assert not (VhdlRecordPackageGenerator(register_list, tmp_path).create()).exists()

    register_list.append_register(name="hest", mode="r_w", description="")
    assert (VhdlRecordPackageGenerator(register_list, tmp_path).create()).exists()


def test_re_generating_package_without_registers_should_delete_old_file(tmp_path):
    register_list = RegisterList(name="test", source_definition_file=None)
    register_list.append_register(name="apa", mode="r_w", description="")

    assert (VhdlRecordPackageGenerator(register_list, tmp_path).create()).exists()

    register_list.register_objects = []
    assert not (VhdlRecordPackageGenerator(register_list, tmp_path).create()).exists()
