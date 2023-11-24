# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import sys
from pathlib import Path

# First party libraries
from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.parser.toml import from_toml
from hdl_registers.register import Register
from hdl_registers.register_list import RegisterList

THIS_DIR = Path(__file__).parent


DEFAULT_REGISTERS = [
    Register(
        name="interrupt_status",
        index=0,
        mode="r_wpulse",
        description="Interrupt status. Clear interrupt(s) by writing the corresponding bitmask.",
    ),
    Register(
        name="interrupt_mask",
        index=1,
        mode="r_w",
        description="Enable or disable interrupts by setting bitmask.",
    ),
]


def parse_toml() -> RegisterList:
    """
    Create the register list by parsing a TOML data file.
    """
    return from_toml(
        module_name="caesar",
        toml_file=THIS_DIR.parent / "toml" / "basic_feature_default_registers.toml",
        default_registers=DEFAULT_REGISTERS,
    )


def create_from_api() -> RegisterList:
    """
    Alternative method: Create the register list by using the Python API.
    """
    register_list = RegisterList.from_default_registers(
        name="caesar", source_definition_file=None, default_registers=DEFAULT_REGISTERS
    )

    register_list.append_register(
        name="configuration", mode="r_w", description="Generic configuration register."
    )

    register_list.append_register(name="status", mode="r", description="Generic status register.")

    return register_list


def generate(register_list: RegisterList, output_folder: Path):
    """
    Generate the artifacts that we are interested in.
    """
    CHeaderGenerator(register_list=register_list, output_folder=output_folder).create()
    CppInterfaceGenerator(register_list=register_list, output_folder=output_folder).create()
    HtmlPageGenerator(register_list=register_list, output_folder=output_folder).create()
    VhdlRegisterPackageGenerator(register_list=register_list, output_folder=output_folder).create()


def main(output_folder: Path):
    generate(register_list=parse_toml(), output_folder=output_folder / "toml")
    generate(register_list=create_from_api(), output_folder=output_folder / "api")


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
