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

import requests

THIS_DIR = Path(__file__).parent.resolve()
REPO_ROOT = THIS_DIR.parent.parent.parent.parent.resolve()
sys.path.append(str(REPO_ROOT))

# Add path for default location of tsfpga to PYTHONPATH.
sys.path.append(str((REPO_ROOT.parent.parent / "tsfpga" / "tsfpga").resolve()))

# ruff: noqa: E402

from tsfpga.system_utils import create_directory, run_command

from hdl_registers import HDL_REGISTERS_GENERATED
from hdl_registers.generator.systemverilog.axi_lite.register_file import (
    SystemVerilogAxiLiteGenerator,
)
from hdl_registers.generator.systemverilog.axi_lite.test.test_register_file import (
    get_basic_register_list,
)


def test_verilator_lint_on_generated_code_flattened(tmp_path):
    sv_files = _generate_code(output_folder=tmp_path / "generated_register", flatten_axi_lite=True)
    _run_verilator(sv_files)


def test_verilator_lint_on_generated_code(tmp_path):
    sv_files = _generate_code(output_folder=tmp_path / "generated_register", flatten_axi_lite=False)

    interface_file_path = tmp_path / "axi4lite_intf.sv"
    response = requests.get(
        (
            "https://raw.githubusercontent.com/"
            "SystemRDL/PeakRDL-regblock/refs/heads/main/hdl-src/axi4lite_intf.sv"
        ),
        timeout=5,
    )
    interface_file_path.open("wb").write(response.content)

    _run_verilator([interface_file_path, *sv_files])


def _generate_code(output_folder: Path, flatten_axi_lite: bool) -> list[Path]:
    register_list = get_basic_register_list()
    generator = SystemVerilogAxiLiteGenerator(
        register_list=register_list, output_folder=output_folder
    )
    generator.create(flatten_axi_lite=flatten_axi_lite)

    return reversed(list(generator.output_files))


def _run_verilator(sv_files: list[Path]) -> None:
    """
    Basic test that our code is valid SystemVerilog.
    The functionality of the generated code is guaranteed by the exporter from PeakRDL.
    What we want to check is that our parameterization of the PeakRDL objects is correct.
    """
    command = ["verilator", "--lint-only", "-Wno-MULTIDRIVEN", "-Wno-WIDTHTRUNC"] + [
        str(path) for path in sv_files
    ]
    run_command(cmd=command)


if __name__ == "__main__":
    # This file is primarily meant to be run with the 'pytest' runner, but it can also be run
    # manually as a script.
    test_verilator_lint_on_generated_code(
        tmp_path=create_directory(HDL_REGISTERS_GENERATED / "verilator_test_out", empty=True)
    )
