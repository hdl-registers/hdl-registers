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

# First party libraries
from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.generator.cpp.header import CppHeaderGenerator
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.html.constant_table import HtmlConstantTableGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.html.register_table import HtmlRegisterTableGenerator
from hdl_registers.generator.python.python_class_generator import PythonClassGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.parser import from_toml

THIS_DIR = Path(__file__).parent


def main(output_folder: Path):
    register_list = from_toml(
        module_name="example", toml_file=THIS_DIR.parent / "toml" / "toml_format.toml"
    )

    CHeaderGenerator(register_list, output_folder / "c").create()

    CppImplementationGenerator(register_list, output_folder / "cpp").create()
    CppHeaderGenerator(register_list, output_folder / "cpp").create()
    CppInterfaceGenerator(register_list, output_folder / "cpp").create()

    HtmlConstantTableGenerator(register_list, output_folder / "html").create()
    HtmlPageGenerator(register_list, output_folder / "html").create()
    HtmlRegisterTableGenerator(register_list, output_folder / "html").create()

    PythonClassGenerator(register_list, output_folder / "py").create()

    VhdlRegisterPackageGenerator(register_list, output_folder / "vhdl").create()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
