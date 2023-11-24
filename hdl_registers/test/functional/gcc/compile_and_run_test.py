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

# First party libraries
from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.parser.toml import from_toml


class CompileAndRunTest:
    def __init__(self, tmp_path: Path) -> None:
        self.working_dir = tmp_path
        self.include_dir = self.working_dir / "include"

        self.register_list = from_toml(
            module_name="caesar", toml_file=HDL_REGISTERS_TEST / "regs_test.toml"
        )
