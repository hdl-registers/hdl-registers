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

# Third party libraries
import yaml

# First party libraries
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.parser.parser import RegisterParser
from hdl_registers.register_list import RegisterList

THIS_DIR = Path(__file__).parent


def parse_yaml() -> RegisterList:
    """
    Create a register list by manually parsing a YAML data file.
    """
    yaml_path = THIS_DIR.parent / "yaml" / "extensions_yaml.yaml"

    with open(yaml_path, encoding="utf-8") as file_handle:
        yaml_data = yaml.safe_load(file_handle)

    parser = RegisterParser(name="caesar", source_definition_file=yaml_path)

    return parser.parse(register_data=yaml_data)


def main(output_folder: Path):
    """
    Create a register list from YAML and create some artifacts.
    """
    register_list = parse_yaml()

    HtmlPageGenerator(register_list=register_list, output_folder=output_folder).create()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
