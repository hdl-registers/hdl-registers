# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from tsfpga.system_utils import read_file

from .parser import RegisterParser

if TYPE_CHECKING:
    from pathlib import Path

    from hdl_registers.register import Register
    from hdl_registers.register_list import RegisterList


def from_json(
    name: str, json_file: Path, default_registers: list[Register] | None = None
) -> RegisterList:
    """
    Parse a JSON file with register data.

    Arguments:
        name: The name of the register list.
        json_file: The JSON file path.
        default_registers: List of default registers.

    Return:
        The resulting register list.
    """
    parser = RegisterParser(
        name=name, source_definition_file=json_file, default_registers=default_registers
    )
    json_data = _load_json_file(file_path=json_file)

    return parser.parse(register_data=json_data)


def _load_json_file(file_path: Path) -> dict[str, Any]:
    """
    Load and parse the JSON data into a dictionary. Raise exceptions if things dont work.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Requested JSON file does not exist: {file_path}")

    raw_json = read_file(file_path)
    try:
        return json.loads(raw_json)
    except Exception as exception_info:
        message = f"Error while parsing JSON file {file_path}:\n{exception_info}"
        raise ValueError(message) from exception_info
