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

# Third party libraries
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers.register_modes import REGISTER_MODES


def main(output_folder: Path):
    rst = """
.. list-table:: All available register modes.
   :header-rows: 1

   * - Shorthand
     - Name
     - Description

"""

    for key, mode in REGISTER_MODES.items():
        rst += f"""\
   * - **{key}**
     - {mode.name}
     - {mode.description}
"""

    create_file(file=output_folder / "modes_table.rst", contents=rst)


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
