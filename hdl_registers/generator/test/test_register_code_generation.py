# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

"""
Some happy path tests to show that all register code generation can run without error.
"""

# Third party libraries
import pytest
import tsfpga
from tsfpga.examples.example_env import get_default_registers

# First party libraries
from hdl_registers import HDL_REGISTERS_DOC, HDL_REGISTERS_TESTS
from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.generator.cpp.header import CppHeaderGenerator
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.html.constant_table import HtmlConstantTableGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.html.register_table import HtmlRegisterTableGenerator
from hdl_registers.generator.python.accessor import PythonAccessorGenerator
from hdl_registers.generator.python.pickle import PythonPickleGenerator
from hdl_registers.generator.vhdl.axi_lite.wrapper import VhdlAxiLiteWrapperGenerator
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.generator.vhdl.simulation.read_write_package import (
    VhdlSimulationReadWritePackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.wait_until_package import (
    VhdlSimulationWaitUntilPackageGenerator,
)
from hdl_registers.parser.toml import from_toml

# Test with all the example TOML files that we have available
REGISTER_LISTS = [
    from_toml(
        name="ddr_buffer",
        toml_file=tsfpga.TSFPGA_EXAMPLE_MODULES / "ddr_buffer" / "regs_ddr_buffer.toml",
        default_registers=get_default_registers(),
    ),
    from_toml(name="caesar", toml_file=HDL_REGISTERS_TESTS / "regs_test.toml"),
    from_toml(
        name="example",
        toml_file=HDL_REGISTERS_DOC / "sphinx" / "rst" / "user_guide" / "toml" / "toml_format.toml",
    ),
]


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_vhdl_without_error(tmp_path, register_list):
    VhdlRegisterPackageGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_regs_pkg.vhd").exists()

    VhdlRecordPackageGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_register_record_pkg.vhd").exists()

    VhdlSimulationReadWritePackageGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_register_read_write_pkg.vhd").exists()

    VhdlSimulationWaitUntilPackageGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_register_wait_until_pkg.vhd").exists()

    VhdlAxiLiteWrapperGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_reg_file.vhd").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_c_without_error(tmp_path, register_list):
    CHeaderGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_regs.h").exists()

    CHeaderGenerator(register_list, tmp_path, file_name="apa.h").create()
    assert (tmp_path / "apa.h").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_cpp_without_error(tmp_path, register_list):
    CppInterfaceGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"i_{register_list.name}.h").exists()

    CppHeaderGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}.h").exists()

    CppImplementationGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}.cpp").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_html_without_error(tmp_path, register_list):
    HtmlRegisterTableGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_register_table.html").exists()

    HtmlConstantTableGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_constant_table.html").exists()

    HtmlPageGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_regs.html").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_python_without_error(tmp_path, register_list):
    PythonPickleGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}.py").exists()

    PythonAccessorGenerator(register_list, tmp_path).create()
    assert (tmp_path / f"{register_list.name}_accessor.py").exists()
