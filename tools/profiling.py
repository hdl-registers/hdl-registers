# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import cProfile
import json
import pstats
import sys
from pathlib import Path

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH. pylint: disable=unused-import
import tools.tools_pythonpath  # noqa: F401

# Third party libraries
from tsfpga.system_utils import create_directory, run_command

# First party libraries
from hdl_registers import HDL_REGISTERS_GENERATED, HDL_REGISTERS_TESTS
from hdl_registers.generator.vhdl.axi_lite.wrapper import VhdlAxiLiteWrapperGenerator
from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
from hdl_registers.generator.vhdl.simulation.read_write_package import (
    VhdlSimulationReadWritePackageGenerator,
)
from hdl_registers.generator.vhdl.simulation.wait_until_package import (
    VhdlSimulationWaitUntilPackageGenerator,
)
from hdl_registers.parser.json import from_json
from hdl_registers.parser.toml import _load_toml_file, from_toml

NUM_ITERATIONS = 10_000

OUTPUT_FOLDER = create_directory(HDL_REGISTERS_GENERATED / "profiling", empty=False)
TOML_FILE = HDL_REGISTERS_TESTS / "regs_test.toml"
JSON_FILE = OUTPUT_FOLDER / "data.json"


def create_json_data_file() -> None:
    """
    The checked-in source of our register data is in TOML format.
    Save it to a JSON file also.
    """
    toml_dict = _load_toml_file(TOML_FILE)

    with open(JSON_FILE, "w", encoding="utf-8") as file_handle:
        json.dump(obj=toml_dict, fp=file_handle)

    print(f"Created JSON file: {JSON_FILE}")


def profile_parse_toml(output_folder: Path) -> cProfile.Profile:  # pylint: disable=unused-argument
    profiler = cProfile.Profile()

    profiler.enable()
    for _ in range(NUM_ITERATIONS):
        from_toml(name="apa", toml_file=TOML_FILE)
    profiler.disable()

    return profiler


def profile_parse_json(output_folder: Path) -> cProfile.Profile:  # pylint: disable=unused-argument
    profiler = cProfile.Profile()

    profiler.enable()
    for _ in range(NUM_ITERATIONS):
        from_json(name="apa", json_file=JSON_FILE)
    profiler.disable()

    return profiler


def profile_generate(output_folder: Path) -> cProfile.Profile:
    register_list = from_toml(name="apa", toml_file=TOML_FILE)

    profiler = cProfile.Profile()

    profiler.enable()
    for _ in range(NUM_ITERATIONS):
        VhdlRegisterPackageGenerator(
            register_list=register_list, output_folder=output_folder
        ).create_if_needed()

        VhdlRecordPackageGenerator(
            register_list=register_list, output_folder=output_folder
        ).create_if_needed()

        VhdlSimulationReadWritePackageGenerator(
            register_list=register_list, output_folder=output_folder
        ).create_if_needed()

        VhdlSimulationWaitUntilPackageGenerator(
            register_list=register_list, output_folder=output_folder
        ).create_if_needed()

        VhdlAxiLiteWrapperGenerator(
            register_list=register_list, output_folder=output_folder
        ).create_if_needed()
    profiler.disable()

    return profiler


def run_profiling(verbose: bool) -> None:
    for test_function, name in [
        (profile_generate, "generate"),
        (profile_parse_json, "parse_json"),
        (profile_parse_toml, "parse_toml"),
    ]:
        output_folder = create_directory(OUTPUT_FOLDER / name, empty=False)

        profiler = test_function(output_folder=output_folder / "files")

        stats = pstats.Stats(profiler)

        if verbose:
            stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(15)

        stats_file = output_folder / f"{name}.pstats"
        dot_file = output_folder / f"{name}.dot"
        png_file = output_folder / f"{name}.png"

        stats.dump_stats(stats_file)

        command = [
            sys.executable,
            "-m",
            "gprof2dot",
            "--format",
            "pstats",
            "--output",
            str(dot_file),
            str(stats_file),
        ]
        run_command(command)

        command = ["dot", "-T", "png", "-o", str(png_file), str(dot_file)]
        run_command(command)

        print(f"eog {png_file} &")


def main() -> None:
    verbose = True

    create_json_data_file()
    run_profiling(verbose=verbose)


if __name__ == "__main__":
    main()
