# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import sys
from pathlib import Path

# First party libraries
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.register_list import RegisterList


class TxtRegisterListGenerator(RegisterCodeGenerator):
    """
    Custom code generator that generates a .txt file with all register names.
    """

    SHORT_DESCRIPTION = "text list"
    COMMENT_START = "#"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_registers.txt"

    def get_code(self, **kwargs) -> str:
        """
        Generate a textual list of all registers and register arrays.
        """
        txt = f'{self.header}\nAvailable registers in the "{self.name}" register list:\n\n'

        for register, register_array in self.iterate_registers():
            if register_array:
                # This register is part of a register array.
                txt += f"{register_array.name}[{register_array.length}].{register.name}\n"
            else:
                # This register is a plain register.
                txt += f"{register.name}\n"

        return txt


def main(output_folder: Path):
    """
    Set up some registers and generate text file with our custom generator.
    """
    register_list = RegisterList(name="caesar")

    register_list.append_register(name="config", mode="r_w", description="")
    register_list.append_register(name="status", mode="r", description="")
    register_list.append_register(name="command", mode="wpulse", description="")

    register_array = register_list.append_register_array(name="channels", length=4, description="")
    register_array.append_register(name="read_address", mode="r_w", description="")
    register_array.append_register(name="write_address", mode="r_w", description="")

    TxtRegisterListGenerator(register_list=register_list, output_folder=output_folder).create()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
