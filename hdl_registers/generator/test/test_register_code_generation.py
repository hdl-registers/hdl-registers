# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

"""
Some happy path tests to show that all register code generation can run without error.
"""

# Third party libraries
import pytest
import tsfpga
from tsfpga.examples.example_env import get_default_registers
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers import HDL_REGISTERS_DOC, HDL_REGISTERS_TEST
from hdl_registers.parser import from_toml

# Test with all the example TOML files that we have available
REGISTER_LISTS = [
    from_toml(
        module_name="ddr_buffer",
        toml_file=tsfpga.TSFPGA_EXAMPLE_MODULES / "ddr_buffer" / "regs_ddr_buffer.toml",
        default_registers=get_default_registers(),
    ),
    from_toml(module_name="test", toml_file=HDL_REGISTERS_TEST / "regs_test.toml"),
    from_toml(
        module_name="example",
        toml_file=HDL_REGISTERS_DOC / "sphinx" / "files" / "regs_example.toml",
    ),
]


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_vhdl_package_without_error(tmp_path, register_list):
    register_list.create_vhdl_package(tmp_path)

    assert (tmp_path / f"{register_list.name}_regs_pkg.vhd").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_c_header_without_error(tmp_path, register_list):
    register_list.create_c_header(tmp_path)
    assert (tmp_path / f"{register_list.name}_regs.h").exists()

    register_list.create_c_header(tmp_path, file_name="apa.h")
    assert (tmp_path / "apa.h").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_cpp_without_error(tmp_path, register_list):
    register_list.create_cpp_interface(tmp_path)
    register_list.create_cpp_header(tmp_path)
    register_list.create_cpp_implementation(tmp_path)

    assert (tmp_path / f"i_{register_list.name}.h").exists()
    assert (tmp_path / f"{register_list.name}.h").exists()
    assert (tmp_path / f"{register_list.name}.cpp").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_html_without_error(tmp_path, register_list):
    register_list.create_html_constant_table(tmp_path)
    register_list.create_html_register_table(tmp_path)
    register_list.create_html_page(tmp_path)

    assert (tmp_path / f"{register_list.name}_regs.html").exists()
    assert (tmp_path / f"{register_list.name}_register_table.html").exists()
    assert (tmp_path / f"{register_list.name}_constant_table.html").exists()
    assert (tmp_path / "regs_style.css").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_can_generate_python_class_file_without_error(tmp_path, register_list):
    register_list.create_python_class(tmp_path)

    assert (tmp_path / f"{register_list.name}.py").exists()


@pytest.mark.parametrize("register_list", REGISTER_LISTS)
def test_copy_source_definition(tmp_path, register_list):
    register_list.copy_source_definition(tmp_path)

    assert read_file(tmp_path / f"regs_{register_list.name}.toml") == read_file(
        register_list.source_definition_file
    )


def test_copy_source_definition_with_no_file_defined(tmp_path):
    register_list = REGISTER_LISTS[0]
    register_list.source_definition_file = None

    output_path = tmp_path / "toml"
    register_list.copy_source_definition(output_path)

    assert not output_path.exists()
