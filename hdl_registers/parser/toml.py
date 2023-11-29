# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Third party libraries
import rtoml

# Local folder libraries
from .parser import RegisterParser

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register import Register
    from hdl_registers.register_list import RegisterList


def from_toml(
    name: str, toml_file: Path, default_registers: Optional[list["Register"]] = None
) -> "RegisterList":
    """
    Parse a TOML file with register data.

    Arguments:
        name: The name of the register list.
        toml_file: The TOML file path.
        default_registers: List of default registers.

    Return:
        The resulting register list.
    """
    parser = RegisterParser(
        name=name, source_definition_file=toml_file, default_registers=default_registers
    )
    toml_data = _load_toml_file(file_path=toml_file)

    return parser.parse(register_data=toml_data)


def _load_toml_file(file_path: Path) -> dict[str, Any]:
    """
    Load and parse the TOML data into a dictionary. Raise exceptions if things dont work.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Requested TOML file does not exist: {file_path}")

    try:
        return rtoml.load(file_path)
    except Exception as exception_info:
        message = f"Error while parsing TOML file {file_path}:\n{exception_info}"
        raise ValueError(message) from exception_info
