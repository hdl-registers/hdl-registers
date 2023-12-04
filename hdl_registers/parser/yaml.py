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
import yaml

# Local folder libraries
from .parser import RegisterParser

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register import Register
    from hdl_registers.register_list import RegisterList


def from_yaml(
    name: str, yaml_file: Path, default_registers: Optional[list["Register"]] = None
) -> "RegisterList":
    """
    Parse a YAML file with register data.

    Arguments:
        name: The name of the register list.
        yaml_file: The YAML file path.
        default_registers: List of default registers.

    Return:
        The resulting register list.
    """
    parser = RegisterParser(
        name=name, source_definition_file=yaml_file, default_registers=default_registers
    )
    yaml_data = _load_yaml_file(file_path=yaml_file)

    return parser.parse(register_data=yaml_data)


def _load_yaml_file(file_path: Path) -> dict[str, Any]:
    """
    Load and parse the YAML data into a dictionary. Raise exceptions if things dont work.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Requested YAML file does not exist: {file_path}")

    with open(file_path, encoding="utf-8") as file_handle:
        try:
            yaml_dict: dict[str, Any] = yaml.safe_load(file_handle)
            return yaml_dict
        except Exception as exception_info:
            message = f"Error while parsing YAML file {file_path}:\n{exception_info}"
            raise ValueError(message) from exception_info
