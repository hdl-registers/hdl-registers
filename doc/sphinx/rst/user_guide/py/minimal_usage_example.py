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

from tsfpga.system_utils import create_file, load_python_module


def main(output_folder: Path) -> None:
    # Handle this as a string rather than its own file to avoid running isort and pylint on in.
    minimal_usage_example = """\
from pathlib import Path

from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.parser.toml import from_toml


this_dir = Path(__file__).parent

register_list = from_toml(name="caesar", toml_file=this_dir / "caesar_registers.toml")
VhdlRegisterPackageGenerator(register_list=register_list, output_folder=this_dir).create_if_needed()
"""
    output_file = create_file(
        file=output_folder / "minimal_usage_example.py", contents=minimal_usage_example
    )

    # Create a very small dummy register file.
    create_file(file=output_folder / "caesar_registers.toml", contents="a.mode = 'r_w'")

    # Test run the code to see that it works.
    # If there is a typo in the code, this will raise an exception.
    load_python_module(file=output_file)


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))
