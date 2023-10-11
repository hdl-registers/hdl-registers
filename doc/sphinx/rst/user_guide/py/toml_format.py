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
from hdl_registers.parser import from_toml

THIS_DIR = Path(__file__).parent


def main(output_path: Path):
    register_list = from_toml(
        module_name="example", toml_file=THIS_DIR.parent / "toml" / "toml_format.toml"
    )

    register_list.create_vhdl_package(output_path=output_path / "vhdl")

    register_list.create_html_page(output_path=output_path / "html")
    register_list.create_html_register_table(output_path=output_path / "html")
    register_list.create_html_constant_table(output_path=output_path / "html")

    register_list.create_c_header(output_path=output_path / "c")

    register_list.create_cpp_interface(output_path=output_path / "cpp")
    register_list.create_cpp_header(output_path=output_path / "cpp")
    register_list.create_cpp_implementation(output_path=output_path / "cpp")

    register_list.create_python_class(output_path=output_path / "py")


if __name__ == "__main__":
    main(output_path=Path(sys.argv[1]))
