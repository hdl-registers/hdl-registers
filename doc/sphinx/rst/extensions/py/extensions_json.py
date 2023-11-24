# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import json
import sys
from pathlib import Path

# First party libraries
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.parser.parser import RegisterParser
from hdl_registers.register_list import RegisterList

THIS_DIR = Path(__file__).parent


def parse_json() -> RegisterList:
    """
    Create a register list by manually parsing a JSON data file.
    """
    json_path = THIS_DIR.parent / "json" / "extensions_json.json"

    with open(json_path, encoding="utf-8") as file_handle:
        json_data = json.load(file_handle)

    parser = RegisterParser(name="caesar", source_definition_file=json_path)

    return parser.parse(register_data=json_data)


def main(output_folder: Path):
    """
    Create a register list from JSON and create some artifacts.
    """
    register_list = parse_json()

    HtmlPageGenerator(register_list=register_list, output_folder=output_folder).create()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
