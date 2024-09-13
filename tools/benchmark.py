# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import contextlib
import sys
import timeit
from pathlib import Path

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install.
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH. pylint: disable=unused-import
import tools.tools_pythonpath  # noqa: F401

# Third party libraries
from tsfpga.system_utils import create_directory, run_command

# First party libraries
from hdl_registers import HDL_REGISTERS_GENERATED

THIS_FOLDER = Path(__file__).parent.resolve()
BENCHMARK_FOLDER = THIS_FOLDER / "benchmark"

OUTPUT_FOLDER = HDL_REGISTERS_GENERATED / "benchmark"

# Parse and generate this many register maps.
# Similar to a medium-sized FPGA project.
NUM_RUNS = 20


# pylint: disable=import-outside-toplevel


def main():
    print(
        """\
--------------------------------------------------------------------------
                       Tool | Execution time | Relative (lower is better)
----------------------------+----------------+----------------------------\
"""
    )

    relative_baseline = None

    for name, test_function in [
        ("hdl-registers", benchmark_hdl_registers),
        ("cheby", benchmark_cheby),
        ("corsair", benchmark_corsair),
        ("PeakRDL", benchmark_peakrdl),
        ("rggen", benchmark_rggen),
        ("vhdmmio", benchmark_vhdmmio),
    ]:
        time_taken_s, num_iterations, tool_version = test_function()

        # Equivalent time for the pre-defined number of runs.
        time_for_runs_s = time_taken_s * NUM_RUNS / num_iterations

        tool = f"{name} ({tool_version})"

        if time_for_runs_s > 1:
            execution_time = f"{time_for_runs_s:.3g}  s"
        else:
            execution_time = f"{time_for_runs_s * 1000:.3g} ms"

        # Print a relative time measurement, compared to the first tool in the list.
        if relative_baseline is None:
            relative_baseline = time_for_runs_s
            relative = "1x (baseline)"
        else:
            relative_multiplier = time_for_runs_s / relative_baseline
            relative = f"{int(relative_multiplier)}x"

        print(f"{tool:>27} | {execution_time:>14} | {relative}")

        assert 5 < time_taken_s < 15, (
            f"We want representative data and a fast script. "
            f"Adjust count for {name}. "
            f"Got {time_taken_s} s."
        )


def benchmark_hdl_registers() -> tuple[float, int, str]:
    # First party libraries
    from hdl_registers import HDL_REGISTERS_TESTS, __version__
    from hdl_registers.generator.vhdl.axi_lite.wrapper import VhdlAxiLiteWrapperGenerator
    from hdl_registers.generator.vhdl.record_package import VhdlRecordPackageGenerator
    from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
    from hdl_registers.generator.vhdl.simulation.read_write_package import (
        VhdlSimulationReadWritePackageGenerator,
    )
    from hdl_registers.generator.vhdl.simulation.wait_until_package import (
        VhdlSimulationWaitUntilPackageGenerator,
    )
    from hdl_registers.parser.toml import from_toml

    output_folder = OUTPUT_FOLDER / "hdl-registers"

    def run_test():
        # Note that this TOML file has, at the time of writing (2023-11-28):
        # * 21 registers, of 5 different modes.
        #   Some of these are repetitions from register arrays.
        # * 56 fields, of 4 different types.
        #   Some of these are from repetitions from register arrays.
        # * 8 register constants, of 5 different types.
        register_list = from_toml(name="test", toml_file=HDL_REGISTERS_TESTS / "regs_test.toml")

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

    # Run once initially so that artifacts are created.
    # Suppress the printouts, so this script prints only a nice table.
    with contextlib.redirect_stdout(None):
        run_test()

    # A decent number of runs that gives representative data.
    num_iterations = 10_000

    time_taken_s = timeit.timeit(run_test, number=num_iterations)

    return time_taken_s, num_iterations, __version__


def benchmark_corsair() -> tuple[float, int, str]:
    """
    Benchmark the "corsair" tool from https://github.com/esynr3z/corsair
    Need to run "python3 -m pip install -U corsair" before.

    Based on the documentation and the code, this tool is intended to be used as a
    command-line program.
    This will always be slower than function calls from a Python script, and the comparison is
    hence unfair.
    However, looking through the source code it was possible with reasonable effort to decode
    how to use the function calls programmatically from a Python script.
    This makes the comparison as fair as possible.
    """
    # Third party libraries
    import corsair

    benchmark_folder = BENCHMARK_FOLDER / "corsair"

    _, targets = corsair.config.read_csrconfig(cfgpath=benchmark_folder / "corsair_config.txt")

    # Set up VHDL generator.
    # Unclear if this should be done only once as a setup, or once for each register map and
    # each generation.
    # It doesn't matter much, result is almost the same, so lets be as fair as possible.
    gen_name = "Vhdl"
    gen_obj = getattr(corsair.generators, gen_name)

    # Generator arguments.
    target_name = "vhdl_module"
    gen_args = targets[target_name]
    gen_args["path"] = str(OUTPUT_FOLDER / "corsair" / "corsair_regs.vhd")

    def run_test():
        # Parse the register map data file.
        register_map = corsair.RegisterMap()
        # The JSON file was use was created by running the template
        #   corsair -t json
        # and then adding dummy registers and fields until it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        register_map.read_file(path=benchmark_folder / "corsair_regs.json")
        # Each register map needs to be validated for user errors.
        register_map.validate()

        # Run generation.
        gen_obj(register_map, **gen_args).generate()

    # A decent number of runs that gives representative data.
    num_iterations = 100

    time_taken_s = timeit.timeit(run_test, number=num_iterations)

    return time_taken_s, num_iterations, corsair.__version__


def benchmark_cheby() -> tuple[float, int, str]:
    """
    Benchmark the "cheby" tool from https://gitlab.cern.ch/be-cem-edl/common/cheby
    Need to run "python setup.py install --user" in the repo root before.

    Based on the documentation and the code, this tool is clearly made to be used as a command-line
    program.
    This will always be slower than function calls from a Python script, and the comparison is
    hence unfair.
    Unlike with e.g. "corsair", it was not possible to re-create the Python function calls for
    parsing and VHDL generation with reasonable effort.
    Hence we have to make the comparison with a command-line call, but if that is how the tool is
    designed then that is the comparison we have to make.
    """
    # The 'cheby' call fails unless the output directory already exists.
    output_folder = create_directory(OUTPUT_FOLDER / "cheby")

    def run_test():
        # The configuration YAML file is based on the example:
        # https://gitlab.cern.ch/be-cem-edl/common/cheby/-/blob/master/doc/srcs/counter.cheby
        # Registers and fields added so it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        command = [
            "cheby",
            "--input",
            str(BENCHMARK_FOLDER / "cheby" / "cheby_regs.yaml"),
            "--gen-hdl",
            str(output_folder / "cheby_regs.vhd"),
        ]
        run_command(command)

    # A decent number of runs that gives representative data.
    num_iterations = 100

    time_taken_s = timeit.timeit(run_test, number=num_iterations)

    # Command will give and output like "cheby 1.6.dev0\n"
    version = run_command(["cheby", "--version"], capture_output=True).stdout.strip().split(" ")[1]

    return time_taken_s, num_iterations, version


def benchmark_vhdmmio() -> tuple[float, int, str]:
    """
    Benchmark the "vhdmmio" tool from https://github.com/abs-tudelft/vhdmmio
    Need to run "python3 -m pip install vhdmmio" before.

    Based on the documentation and the code, this tool is intended to be used as a
    command-line program.
    This will always be slower than function calls from a Python script, and the comparison is
    hence unfair.
    However, looking through the source code it was possible with reasonable effort to decode
    how to use the function calls programmatically from a Python script.
    This makes the comparison as fair as possible.
    """
    # Third party libraries
    from vhdmmio.config import RegisterFileConfig
    from vhdmmio.core import RegisterFile
    from vhdmmio.version import __version__
    from vhdmmio.vhdl import VhdlEntitiesGenerator

    def run_test():
        # YAML file for test based on
        # https://github.com/abs-tudelft/vhdmmio/blob/master/examples/basic/basic.mmio.yaml
        # and https://github.com/abs-tudelft/vhdmmio/blob/master/examples/lpc1313_ssp/
        # Registers and fields added so it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        register_file_config = RegisterFileConfig.load(
            obj=str(BENCHMARK_FOLDER / "vhdmmio" / "vhdmmio_regs.yaml")
        )
        register_file = RegisterFile(cfg=register_file_config, trusted=False)

        generator = VhdlEntitiesGenerator(regfiles=[register_file])
        generator.generate(output_dir=OUTPUT_FOLDER / "vhdmmio")

    # A decent number of runs that gives representative data.
    num_iterations = 10

    # Suppress the printouts from vhdmmio, so this script prints only a nice table.
    with contextlib.redirect_stdout(None):
        time_taken_s = timeit.timeit(run_test, number=num_iterations)

    return time_taken_s, num_iterations, __version__


def benchmark_rggen() -> tuple[float, int, str]:
    """
    Benchmark the "rggen" tool from https://github.com/rggen/rggen
    Uses the "rggen-vhdl" generator from: https://github.com/rggen/rggen-vhdl
    This is a tool written in Ruby, so from a Python-based build flow it needs to be run
    via system calls.

    Need to install ruby from your OS package manager.
    Need to run "gem install --user rggen" and "gem install --user rggen-vhdl".
    Also need to add "~/.gem/ruby/3.0.0/bin" to PATH.
    """

    def run_test():
        # Configuration files adapted from
        # https://github.com/rggen/rggen-sample/blob/master/config.yml
        # https://github.com/rggen/rggen-sample/blob/master/uart_csr.yml
        # Registers and fields added so it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        command = [
            "rggen",
            "--plugin",
            "rggen-vhdl",
            "--configuration",
            str(BENCHMARK_FOLDER / "rggen" / "rggen_config.yml"),
            "--output",
            str(OUTPUT_FOLDER / "rggen"),
            str(BENCHMARK_FOLDER / "rggen" / "rggen_regs.yml"),
        ]
        run_command(command)

    # A decent number of runs that gives representative data.
    num_iterations = 20

    time_taken_s = timeit.timeit(run_test, number=num_iterations)

    # Command will give and output like "RgGen 0.31\n"
    version = run_command(["rggen", "--version"], capture_output=True).stdout.strip().split(" ")[1]

    return time_taken_s, num_iterations, version


def benchmark_peakrdl() -> tuple[float, int, str]:
    """
    Benchmark the "PeakRDL" tool from https://github.com/SystemRDL/PeakRDL
    Uses the "PeakRDL-regblock" SystemVerilog generator
    from https://github.com/SystemRDL/PeakRDL-regblock
    Need to run "python3 -m pip install peakrdl" before.

    Based on the documentation and the code, this tool is clearly made to be used as a command-line
    program.
    This will always be slower than function calls from a Python script, and the comparison is
    hence unfair.
    Unlike with e.g. "corsair", it was not possible to re-create the Python function calls for
    parsing and code generation with reasonable effort.
    Hence we have to make the comparison with a command-line call, but if that is how the tool is
    designed then that is the comparison we have to make.

    There is no (official) VHDL generator in PeakRDL, so we generate SystemVerilog code instead.
    This is not a one-to-one comparison, but it gives a hint at the speed of the tool.
    """

    def run_test():
        # Configuration file adapted from
        # https://github.com/SystemRDL/PeakRDL/blob/main/examples/atxmega_spi.rdl
        # Registers and fields added so it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        command = [
            "peakrdl",
            "regblock",
            str(BENCHMARK_FOLDER / "peakrdl" / "peakrdl_config.rdl"),
            "-o",
            str(OUTPUT_FOLDER / "peakrdl"),
            "--cpuif",
            "axi4-lite-flat",
        ]
        run_command(command)

    # A decent number of runs that gives representative data.
    num_iterations = 20

    time_taken_s = timeit.timeit(run_test, number=num_iterations)

    # Command will give and output like "1.1.0\n"
    version = run_command(["peakrdl", "--version"], capture_output=True).stdout.strip()

    return time_taken_s, num_iterations, version


if __name__ == "__main__":
    main()
