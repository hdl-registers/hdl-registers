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

# First party libraries
# pylint: disable=unused-import
from hdl_registers.generator.c.header import CHeaderGenerator  # noqa: F401
from hdl_registers.generator.cpp.header import CppHeaderGenerator  # noqa: F401
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator  # noqa: F401
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator  # noqa: F401
from hdl_registers.generator.html.page import HtmlPageGenerator  # noqa: F401
from hdl_registers.generator.python.accessor import PythonAccessorGenerator  # noqa: F401
from hdl_registers.generator.python.pickle import PythonPickleGenerator  # noqa: F401
from hdl_registers.generator.vhdl.axi_lite.wrapper import VhdlAxiLiteWrapperGenerator  # noqa: F401
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator  # noqa: F401
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator  # noqa: F401
from hdl_registers.generator.vhdl.simulation.check_package import (  # noqa: F401
    VhdlSimulationCheckPackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.read_write_package import (  # noqa: F401
    VhdlSimulationReadWritePackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.wait_until_package import (  # noqa: F401
    VhdlSimulationWaitUntilPackageGenerator,
)
from hdl_registers.parser.json import from_json  # noqa: F401
from hdl_registers.parser.toml import from_toml  # noqa: F401
from hdl_registers.parser.yaml import from_yaml  # noqa: F401


def main() -> None:
    print("done")


if __name__ == "__main__":
    main()
