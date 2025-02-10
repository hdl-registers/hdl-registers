# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import os
import sys
from pathlib import Path

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install.
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH.
import tools.tools_pythonpath  # noqa: F401

from tsfpga.system_utils import load_python_module

import hdl_registers
from hdl_registers.generator.python.accessor import PythonAccessorGenerator
from hdl_registers.generator.python.pickle import PythonPickleGenerator
from hdl_registers.generator.python.register_accessor_interface import (
    PythonRegisterAccessorInterface,
)
from hdl_registers.generator.python.test.accessor.conftest import add_test_registers
from hdl_registers.generator.python.test.accessor.test_accessor_operations import a_value0_int
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


class RegisterAccessor(PythonRegisterAccessorInterface):
    """
    Dummy register accessor that always returns the same read value.
    """

    def read_register(
        self,
        register_list_name: str,  # noqa: ARG002
        register_address: int,  # noqa: ARG002
    ) -> int:
        return a_value0_int()

    def write_register(
        self, register_list_name: str, register_address: int, register_value: int
    ) -> None:
        pass


def main() -> None:
    """
    Try to print the registers with color and without color.
    Print coloring can not be verified in unit tests, so this is for manual testing.
    """
    register_list = RegisterList(name="caesar")

    add_test_registers(register_list_or_array=register_list)
    register_list.append_register(name="reg_r_empty", mode=REGISTER_MODES["r"], description="")

    this_file_name = Path(__file__).stem
    output_folder = hdl_registers.HDL_REGISTERS_GENERATED / this_file_name

    PythonAccessorGenerator(register_list=register_list, output_folder=output_folder).create()
    PythonPickleGenerator(register_list=register_list, output_folder=output_folder).create()

    python_module = load_python_module(output_folder / "caesar_accessor.py")
    accessor = python_module.get_accessor(register_accessor=RegisterAccessor())

    print("Print with color:\n")
    accessor.print_registers()

    print("\n\nPrint without color:\n")
    accessor.print_registers(no_color=True)

    os.environ["NO_COLOR"] = "yes"
    print("\n\nPrint without color:\n")
    accessor.print_registers()


if __name__ == "__main__":
    main()
