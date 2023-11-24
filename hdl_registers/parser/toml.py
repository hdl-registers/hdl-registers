# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Third party libraries
import tomli
from tsfpga.system_utils import read_file

# Local folder libraries
from .parser import RegisterParser

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register import Register
    from hdl_registers.register_list import RegisterList


def load_toml_file(toml_file: Path) -> dict[str, Any]:
    if not toml_file.exists():
        raise FileNotFoundError(f"Requested TOML file does not exist: {toml_file}")

    raw_toml = read_file(toml_file)
    try:
        return tomli.loads(raw_toml)
    except Exception as exception_info:
        message = f"Error while parsing TOML file {toml_file}:\n{exception_info}"
        raise ValueError(message) from exception_info


def from_toml(
    module_name: str, toml_file: Path, default_registers: Optional[list["Register"]] = None
) -> "RegisterList":
    """
    Parse a register TOML file.

    Arguments:
        module_name: The name of the module that these registers belong to.
        toml_file: The TOML file path.
        default_registers: List of default registers.

    Return:
        The resulting register list.
    """
    parser = RegisterParser(
        module_name=module_name,
        source_definition_file=toml_file,
        default_registers=default_registers,
    )
    toml_data = load_toml_file(toml_file)

    return parser.parse(register_data=toml_data)
