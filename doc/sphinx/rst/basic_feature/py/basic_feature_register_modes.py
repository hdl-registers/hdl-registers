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

# Third party libraries
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers.register import REGISTER_MODES


def main(output_path: Path):
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
     - {mode.mode_readable}
     - {mode.description}
"""

    create_file(file=output_path / "modes_table.rst", contents=rst)


if __name__ == "__main__":
    main(output_path=Path(sys.argv[1]))
