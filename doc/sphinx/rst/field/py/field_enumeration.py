# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import sys
from pathlib import Path

from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES

THIS_DIR = Path(__file__).parent


def parse_toml() -> RegisterList:
    """
    Create the register list by parsing a TOML data file.
    """
    return from_toml(name="caesar", toml_file=THIS_DIR.parent / "toml" / "field_enumeration.toml")


def create_from_api() -> RegisterList:
    """
    Alternative method: Create the register list by using the Python API.
    """
    register_list = RegisterList(name="caesar")

    register = register_list.append_register(
        name="conf", mode=REGISTER_MODES["r_w"], description="Configuration register."
    )

    register.append_enumeration(
        name="severity_level",
        description="Run-time configuration of severity.",
        elements={
            "info": "Informational message. Is not considered an error.",
            "warning": "Warning message. Is not considered an error.",
            "error": "Error message. Is considered an error.",
            "failure": "Failure message. Is considered an error.",
        },
        default_value="warning",
    )

    register.append_enumeration(
        name="packet_source",
        description="Set input mux.",
        elements={
            "streaming": "Process incoming streaming data.",
            "dma": "Read packets from DMA.",
            "disabled": "Don't send anything.",
        },
        default_value="streaming",
    )

    return register_list


def generate(register_list: RegisterList, output_folder: Path) -> None:
    """
    Generate the artifacts that we are interested in.
    """
    CHeaderGenerator(register_list=register_list, output_folder=output_folder).create()

    CppImplementationGenerator(register_list=register_list, output_folder=output_folder).create()
    CppInterfaceGenerator(register_list=register_list, output_folder=output_folder).create()

    HtmlPageGenerator(register_list=register_list, output_folder=output_folder).create()

    VhdlRegisterPackageGenerator(register_list=register_list, output_folder=output_folder).create()
    VhdlRecordPackageGenerator(register_list=register_list, output_folder=output_folder).create()


def main(output_folder: Path) -> None:
    generate(register_list=parse_toml(), output_folder=output_folder / "toml")
    generate(register_list=create_from_api(), output_folder=output_folder / "api")


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
