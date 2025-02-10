# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------
# Test script to see that everything from this package is importable.
# I.e. that a working installation is in place, along with all dependencies.
# --------------------------------------------------------------------------------------------------

# ruff: noqa: F401

from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.generator.cpp.header import CppHeaderGenerator
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.python.accessor import PythonAccessorGenerator
from hdl_registers.generator.python.pickle import PythonPickleGenerator
from hdl_registers.generator.vhdl.axi_lite.wrapper import VhdlAxiLiteWrapperGenerator
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.generator.vhdl.simulation.check_package import (
    VhdlSimulationCheckPackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.read_write_package import (
    VhdlSimulationReadWritePackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.wait_until_package import (
    VhdlSimulationWaitUntilPackageGenerator,
)
from hdl_registers.parser.json import from_json
from hdl_registers.parser.toml import from_toml
from hdl_registers.parser.yaml import from_yaml


def main() -> None:
    print("done")


if __name__ == "__main__":
    main()
