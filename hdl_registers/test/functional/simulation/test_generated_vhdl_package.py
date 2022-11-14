# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to be run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path

# Third party libraries
from tsfpga.examples.example_env import get_hdl_modules
from vunit import VUnit

# First party libraries
from hdl_registers import HDL_REGISTERS_DOC
from hdl_registers.parser import from_toml

THIS_FOLDER = Path(__file__).parent.resolve()


def test_running_simulation(tmp_path):
    """
    Run the testbench .vhd file that is next to this file. Contains assertions on the
    VHDL package generated from the example TOML file. Shows that the file can be compiled and
    that (some of) the information is correct.
    """
    register_list = from_toml(
        module_name="example",
        toml_file=HDL_REGISTERS_DOC / "sphinx" / "files" / "regs_example.toml",
    )
    register_list.create_vhdl_package(output_path=tmp_path)

    vunit_proj = VUnit.from_argv(
        argv=["--minimal", "--num-threads", "4", "--output-path", str(tmp_path)]
    )

    library = vunit_proj.add_library(library_name="example")
    library.add_source_file(THIS_FOLDER / "tb_generated_vhdl_package.vhd")
    library.add_source_file(tmp_path / "example_regs_pkg.vhd")

    for module in get_hdl_modules():
        vunit_library = vunit_proj.add_library(library_name=module.library_name)
        for hdl_file in module.get_simulation_files(include_tests=False):
            vunit_library.add_source_file(hdl_file.path)

    try:
        vunit_proj.main()
    except SystemExit as exception:
        assert exception.code == 0
