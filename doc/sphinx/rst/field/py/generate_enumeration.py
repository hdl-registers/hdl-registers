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
from hdl_registers.parser import from_toml
from hdl_registers.register_list import RegisterList

THIS_DIR = Path(__file__).parent


def parse_toml() -> RegisterList:
    """
    Create the register list by parsing a TOML data file.
    """
    return from_toml(
        module_name="caesar", toml_file=THIS_DIR.parent / "toml" / "regs_enumeration.toml"
    )


def create_from_api() -> RegisterList:
    """
    Create the register list by using the Python API.
    """
    register_list = RegisterList(name="caesar")

    register = register_list.append_register(
        name="configuration", mode="r_w", description="Configuration register."
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
        },
        default_value="streaming",
    )

    return register_list


def generate(register_list: RegisterList, output_path: Path):
    """
    Generate the artifacts that we are interested in.
    """
    register_list.create_c_header(output_path)

    register_list.create_cpp_interface(output_path)
    register_list.create_cpp_implementation(output_path)

    register_list.create_vhdl_package(output_path)

    register_list.create_html_page(output_path)


def main(output_path):
    generate(register_list=parse_toml(), output_path=output_path / "toml")
    generate(register_list=create_from_api(), output_path=output_path / "api")


if __name__ == "__main__":
    main(output_path=Path(sys.argv[1]))
