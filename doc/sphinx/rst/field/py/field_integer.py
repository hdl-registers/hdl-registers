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
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_list import RegisterList

THIS_DIR = Path(__file__).parent


def parse_toml() -> RegisterList:
    """
    Create the register list by parsing a TOML data file.
    """
    return from_toml(name="caesar", toml_file=THIS_DIR.parent / "toml" / "field_integer.toml")


def create_from_api() -> RegisterList:
    """
    Alternative method: Create the register list by using the Python API.
    """
    register_list = RegisterList(name="caesar")

    register = register_list.append_register(
        name="configuration", mode="r_w", description="Configuration register."
    )

    register.append_integer(
        name="burst_length_bytes",
        description="The number of bytes to request.",
        min_value=1,
        max_value=256,
        default_value=64,
    )

    register.append_integer(
        name="increment",
        description="Offset that will be added to data.",
        min_value=-4,
        max_value=3,
        default_value=0,
    )

    register.append_integer(
        name="retry_count",
        description="Number of retry attempts before giving up.",
        min_value=0,
        max_value=5,
        default_value=0,
    )

    return register_list


def generate(register_list: RegisterList, output_folder: Path):
    """
    Generate the artifacts that we are interested in.
    """
    CHeaderGenerator(register_list=register_list, output_folder=output_folder).create()

    CppImplementationGenerator(register_list=register_list, output_folder=output_folder).create()
    CppInterfaceGenerator(register_list=register_list, output_folder=output_folder).create()

    HtmlPageGenerator(register_list=register_list, output_folder=output_folder).create()

    VhdlRegisterPackageGenerator(register_list=register_list, output_folder=output_folder).create()


def main(output_folder: Path):
    generate(register_list=parse_toml(), output_folder=output_folder / "toml")
    generate(register_list=create_from_api(), output_folder=output_folder / "api")


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
