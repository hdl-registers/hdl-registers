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

from tsfpga.system_utils import create_file

from hdl_registers.register_modes import REGISTER_MODES


def main(output_folder: Path) -> None:
    base_rst = """
.. list-table::
   :header-rows: 1

   * - Shorthand
     - Name
     - Description

"""
    typical_rst = base_rst
    special_rst = base_rst

    for shorthand_key, mode in REGISTER_MODES.items():
        rst = f"""\
   * - **{shorthand_key}**
     - {mode.name}
     - {mode.description}
"""
        if shorthand_key in ["r", "w", "r_w"]:
            typical_rst += rst
        else:
            special_rst += rst

    create_file(file=output_folder / "typical_modes.rst", contents=typical_rst)
    create_file(file=output_folder / "special_modes.rst", contents=special_rst)


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
