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

from hdl_registers.generator.systemverilog.axi_lite.register_file import (
    SystemVerilogAxiLiteGenerator,
)
from hdl_registers.parser.toml import from_toml

THIS_DIR = Path(__file__).parent


def main(output_folder: Path) -> None:
    """
    Create SystemVerilog register artifacts for an example module.
    """
    register_list = from_toml(
        name="basic", toml_file=THIS_DIR.parent / "example_basic" / "regs_basic.toml"
    )

    SystemVerilogAxiLiteGenerator(
        register_list=register_list, output_folder=output_folder
    ).create_if_needed()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
