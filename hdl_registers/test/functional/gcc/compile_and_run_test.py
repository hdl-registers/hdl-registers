# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.parser import from_toml


class CompileAndRunTest:
    def __init__(self, tmp_path):
        self.working_dir = tmp_path
        self.include_dir = self.working_dir / "include"

        self.registers = from_toml(
            module_name="caesar", toml_file=HDL_REGISTERS_TEST / "regs_test.toml"
        )
