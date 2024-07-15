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

# Standard libraries
from pathlib import Path

# Third party libraries
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers.generator.vhdl.axi_lite.wrapper import VhdlAxiLiteWrapperGenerator
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.generator.vhdl.simulation.check_package import (
    VhdlSimulationCheckPackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.read_write_package import (
    VhdlSimulationReadWritePackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.wait_until_package import (
    VhdlSimulationWaitUntilPackageGenerator,
)
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


def generate_all_vhdl_artifacts(register_list: RegisterList, output_folder: Path) -> None:
    VhdlRegisterPackageGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()

    VhdlRecordPackageGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()

    VhdlAxiLiteWrapperGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()

    VhdlSimulationReadWritePackageGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()

    VhdlSimulationCheckPackageGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()

    VhdlSimulationWaitUntilPackageGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()


def generate_strange_register_maps(output_path):
    """
    Generate register VHDL artifacts for some strange niche cases.
    """

    def create_packages(direction, mode):
        def append_register(data, name):
            """
            Append a register with some fields.
            """
            register = data.append_register(
                name=f"{name}_{mode.shorthand}", mode=mode, description=""
            )

            register.append_integer(
                name="integer", description="", min_value=-10, max_value=10, default_value=3
            )
            register.append_enumeration(
                name="enumeration", description="", elements=dict(a="", b=""), default_value="b"
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
        generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)

        # Some register arrays, in one direction only.
        register_list = RegisterList(name=f"array_only_{direction}")
        register_array = register_list.append_register_array(name="apa", length=5, description="")
        append_registers(data=register_array)
        register_array = register_list.append_register_array(name="hest", length=10, description="")
        append_registers(data=register_array)
        generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)

        # Plain registers and some register arrays, in one direction only.
        register_list = RegisterList(name=f"plain_and_array_only_{direction}")
        append_registers(data=register_list)
        register_array = register_list.append_register_array(name="apa", length=5, description="")
        append_registers(data=register_array)
        register_array = register_list.append_register_array(name="hest", length=10, description="")
        append_registers(data=register_array)
        generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)

    # Mode 'Read only' should give registers only in the 'up' direction'
    create_packages(direction="up", mode=REGISTER_MODES["r"])
    # Mode 'Write only' should give registers only in the 'down' direction'
    create_packages(direction="down", mode=REGISTER_MODES["w"])

    register_list = RegisterList(name="only_constants")
    register_list.add_constant(name="first", value=123, description="")
    register_list.add_constant(name="second", value=True, description="")
    generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)

    register_list = RegisterList(name="empty")
    generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)


def _get_register_arrays_record_string(direction):
    return (
        f"records for the registers of each register array the are in the '{direction}' direction"
    )


def test_registers_only_in_up_direction_should_give_no_down_type_or_port(tmp_path):
    generate_strange_register_maps(output_path=tmp_path)

    for file_name in ["array_only_up", "plain_and_array_only_up", "plain_only_up"]:
        vhd = read_file(tmp_path / f"{file_name}_register_record_pkg.vhd")

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
        vhd = read_file(tmp_path / f"{file_name}_register_record_pkg.vhd")

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
