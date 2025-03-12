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

from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


def main(output_folder: Path) -> None:
    """
    Set up some dummy registers and fields using the Python API.
    """
    register_list = RegisterList(name="caesar")

    register = register_list.append_register(
        name="conf", mode=REGISTER_MODES["r_w"], description="Configuration register."
    )

    register.append_bit_vector(
        name="tuser",
        description="Value to set for **TUSER** in the data stream.",
        width=4,
        default_value="0101",
    )

    register.append_integer(
        name="increment",
        description="Offset that will be added to data.",
        min_value=-4,
        max_value=3,
        default_value=0,
    )

    register = register_list.append_register(
        name="status", mode=REGISTER_MODES["r"], description="General status register."
    )

    VhdlRegisterPackageGenerator(register_list=register_list, output_folder=output_folder).create()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
