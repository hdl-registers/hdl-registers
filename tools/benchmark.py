# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import argparse
import contextlib
import sys
import timeit
from pathlib import Path
from shutil import copy2

import git

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install.
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH.
import tools.tools_pythonpath  # noqa: F401

from hdl_modules import get_hdl_modules
from tsfpga.examples.vivado.project import TsfpgaExampleVivadoNetlistProject
from tsfpga.module import BaseModule
from tsfpga.system_utils import create_directory, delete, run_command

from hdl_registers import HDL_REGISTERS_GENERATED
from hdl_registers.register import Register

THIS_FOLDER = Path(__file__).parent.resolve()
BENCHMARK_FOLDER = THIS_FOLDER / "benchmark"

OUTPUT_FOLDER = HDL_REGISTERS_GENERATED / "benchmark"

# Parse and generate this many register lists.
# Similar to a medium-sized FPGA project.
NUM_RUNS = 20

# The FPGA part name to use for Vivado synthesis.
PART = "xc7z020clg400-1"


def main() -> None:
    args = arguments()

    # Clean up any previous runs.
    delete(OUTPUT_FOLDER)

    print_intro()

    print(
        """\
-------------------------------------------------------------------------------\
------------------------------
                      Tool | Generate time | Time relative (lower is better) | \
  LUT |   FF | LUT+FF relative
---------------------------+---------------+---------------------------------+-\
------+------+----------------\
"""
    )

    relative_time_baseline = None
    relative_usage_baseline = None

    tests = [
        ("hdl-registers", benchmark_hdl_registers_comparable),
        ("cheby", benchmark_cheby),
        ("corsair", benchmark_corsair),
        ("PeakRDL", benchmark_peakrdl),
        ("vhdmmio", benchmark_vhdmmio),
        ("rggen", benchmark_rggen),
    ]

    if not args.skip_hdl_registers_typical:
        tests.insert(1, ("hdl-registers2", benchmark_hdl_registers_typical))

    for name, test_function in tests:
        tool_version, time_per_run_s, lut, ff = test_function(
            output_folder=OUTPUT_FOLDER / name,
            skip_time=args.skip_time,
            skip_resource_usage=args.skip_resource_usage,
        )

        # Equivalent time for the pre-defined number of runs.
        time_for_runs_s = NUM_RUNS * time_per_run_s

        tool = f"{name} ({tool_version})"

        if time_for_runs_s > 1:
            execution_time = f"{time_for_runs_s:.3g}  s"
        else:
            execution_time = f"{time_for_runs_s * 1000:.3g} ms"

        # Print relative measurements, compared to the first tool in the list.
        if relative_time_baseline is None:
            relative_time_baseline = time_for_runs_s
            relative_time = "1x (baseline)"

            relative_usage_baseline = lut + ff
            relative_usage = "1x (baseline)"
        else:
            relative_multiplier = time_for_runs_s / relative_time_baseline
            relative_time = f"{int(relative_multiplier)}x"

            relative_multiplier = (lut + ff) / relative_usage_baseline
            relative_usage = f"{relative_multiplier:.2g}x"

        print(
            f"{tool:>26} | {execution_time:>13} | {relative_time:>31} | "
            f"{NUM_RUNS * lut:>5} | {NUM_RUNS * ff:>4} | {relative_usage:>15}"
        )


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Compare different register generators",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--skip-hdl-registers-typical",
        action="store_true",
        help=(
            "Run only hdl-registers only on the comparable benchmark. "
            "Set this to produce a nice table."
        ),
    )

    parser.add_argument(
        "--skip-time",
        action="store_true",
        help=("do not benchmark the time take to generate artifacts"),
    )

    parser.add_argument(
        "--skip-resource-usage",
        action="store_true",
        help=("do not run synthesis to compare resource usage"),
    )

    return parser.parse_args()


def print_intro() -> None:
    from hdl_registers.parser.toml import from_toml

    register_list = from_toml(
        name="test", toml_file=BENCHMARK_FOLDER / "hdl_registers" / "regs_benchmark.toml"
    )
    num_registers = register_list.register_objects[-1].index + 1

    num_fields = 0
    num_bits = 0
    for register_object in register_list.register_objects:
        assert isinstance(register_object, Register), (
            "should be no register arrays in this test file"
        )
        for field in register_object.fields:
            num_fields += 1
            num_bits += field.width

    print(
        "Benchmarking a medium-sized FPGA project: "
        f"{NUM_RUNS} register lists, each containing {num_registers} registers "
        f"with {num_fields // num_registers} {num_bits // num_fields}-bit fields."
    )


def check_time(time_taken_s: float) -> None:
    if time_taken_s < 5 or time_taken_s > 15:
        print(
            "Bad execution time. "
            f"We want representative data and a fast script. Got {time_taken_s} s."
        )


def build(registers_folder: Path, build_folder: Path, top: str) -> tuple[int, int]:
    modules = get_hdl_modules(names_avoid={"hard_fifo"})
    modules.append(BaseModule(path=registers_folder, library_name=top))

    project = TsfpgaExampleVivadoNetlistProject(name=top, modules=modules, part=PART, top=top)
    with contextlib.redirect_stdout(None):
        assert project.create(project_path=build_folder)

    with contextlib.redirect_stdout(None):
        build_result = project.build(project_path=build_folder)

    assert build_result.success

    return build_result.synthesis_size["Total LUTs"], build_result.synthesis_size["FFs"]


def benchmark_hdl_registers(
    toml_file: Path,
    output_folder: Path,
    test_comparable: bool,
    skip_time: bool,
    skip_resource_usage: bool,
) -> tuple[str, float, int, int]:
    from hdl_registers import __version__
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

    registers_folder = output_folder / "hdl-registers"
    build_folder = output_folder / "vivado_project"

    def run_test_all() -> None:
        # Produce all outputs that we would produce before a simulation/synthesis run.
        register_list = from_toml(name="test", toml_file=toml_file)

        VhdlRegisterPackageGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

        VhdlRecordPackageGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

        VhdlSimulationReadWritePackageGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

        VhdlSimulationWaitUntilPackageGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

        VhdlAxiLiteWrapperGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

    def run_test_comparable() -> None:
        # Produce only roughly the same output as the other tools.
        register_list = from_toml(name="test", toml_file=toml_file)

        VhdlRegisterPackageGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

        VhdlRecordPackageGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

        VhdlAxiLiteWrapperGenerator(
            register_list=register_list, output_folder=registers_folder
        ).create_if_needed()

    run_test = run_test_comparable if test_comparable else run_test_all

    # Run once initially so that artifacts are created.
    # Suppress the printouts, so this script prints only a nice table.
    with contextlib.redirect_stdout(None):
        run_test()

    if skip_time:
        time_s = 1
    else:
        # A decent number of runs that gives representative data.
        num_iterations = 10_000

        time_taken_s = timeit.timeit(run_test, number=num_iterations)
        check_time(time_taken_s=time_taken_s)

        time_s = time_taken_s / num_iterations

    if skip_resource_usage:
        (lut, ff) = (1, 1)
    else:
        if test_comparable:
            # Use a register file wrapper that does not route the 'reg_was_read' and
            # 'reg_was_written' signals.
            # Since (most of) the other tools do not have this feature, excluding these
            # signals makes the comparison more fair.
            top = "test_register_file_axi_lite_wrapper"
            copy2(
                BENCHMARK_FOLDER / "hdl_registers" / f"{top}.vhd", registers_folder / f"{top}.vhd"
            )
        else:
            top = "test_register_file_axi_lite"

        lut, ff = build(registers_folder=registers_folder, build_folder=build_folder, top=top)

    return __version__, time_s, lut, ff


def benchmark_hdl_registers_comparable(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
    """
    Test the performance on a dummy register file with the same configuration as the others.
    """
    return benchmark_hdl_registers(
        toml_file=BENCHMARK_FOLDER / "hdl_registers" / "regs_benchmark.toml",
        output_folder=output_folder,
        test_comparable=True,
        skip_time=skip_time,
        skip_resource_usage=skip_resource_usage,
    )


def benchmark_hdl_registers_typical(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
    """
    Test the performance of a more typical register file.
    Something that contains all different modes, register arrays, fields, constants, etc.
    It also generates all the artifacts that we would generate in real time before a e.g
    a simulation run.
    Hence this one is way more relevant for us to keep track of during development.
    But it is not possible to use this data to compare with the others.
    """
    from hdl_registers import HDL_REGISTERS_TESTS

    return benchmark_hdl_registers(
        toml_file=HDL_REGISTERS_TESTS / "regs_test.toml",
        output_folder=output_folder,
        test_comparable=False,
        skip_time=skip_time,
        skip_resource_usage=skip_resource_usage,
    )


def benchmark_corsair(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
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
    import corsair

    benchmark_folder = BENCHMARK_FOLDER / "corsair"
    registers_folder = output_folder / "corsair"
    build_folder = output_folder / "vivado_project"

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
    gen_args["path"] = str(registers_folder / "corsair_regs.vhd")

    def run_test() -> None:
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

    # Run once initially so that artifacts are created.
    run_test()

    if skip_time:
        time_s = 1
    else:
        # A decent number of runs that gives representative data.
        num_iterations = 100

        time_taken_s = timeit.timeit(run_test, number=num_iterations)
        check_time(time_taken_s=time_taken_s)

        time_s = time_taken_s / num_iterations

    if skip_resource_usage:
        (lut, ff) = (1, 1)
    else:
        lut, ff = build(
            registers_folder=registers_folder, build_folder=build_folder, top="corsair_regs"
        )

    return corsair.__version__, time_s, lut, ff


def benchmark_cheby(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
    """
    Benchmark the "cheby" tool from https://gitlab.cern.ch/be-cem-edl/common/cheby
    Need to run "python3 setup.py install --user" in the repo root before.

    Based on the documentation and the code, this tool is clearly made to be used as a command-line
    program.
    This will always be slower than function calls from a Python script, and the comparison is
    hence unfair.
    Unlike with e.g. "corsair", it was not possible to re-create the Python function calls for
    parsing and VHDL generation with reasonable effort.
    Hence we have to make the comparison with a command-line call, but if that is how the tool is
    designed then that is the comparison we have to make.
    """
    # Command will give and output like "cheby 1.6.dev0\n"
    version = run_command(["cheby", "--version"], capture_output=True).stdout.strip().split(" ")[1]

    # The 'cheby' call fails unless the output directory already exists.
    registers_folder = create_directory(output_folder / "cheby")
    build_folder = output_folder / "vivado_project"

    def run_test() -> None:
        # The configuration YAML file is based on the example:
        # https://gitlab.cern.ch/be-cem-edl/common/cheby/-/blob/master/doc/srcs/counter.cheby
        # Registers and fields added so it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        command = [
            "cheby",
            "--input",
            str(BENCHMARK_FOLDER / "cheby" / "cheby_regs.yaml"),
            "--gen-hdl",
            str(registers_folder / "counter.vhd"),
        ]
        run_command(command)

    # Run once initially so that artifacts are created.
    run_test()

    if skip_time:
        time_s = 1
    else:
        # A decent number of runs that gives representative data.
        num_iterations = 100

        time_taken_s = timeit.timeit(run_test, number=num_iterations)
        check_time(time_taken_s=time_taken_s)

        time_s = time_taken_s / num_iterations

    if skip_resource_usage:
        (lut, ff) = (1, 1)
    else:
        lut, ff = build(registers_folder=registers_folder, build_folder=build_folder, top="counter")

    return version, time_s, lut, ff


def benchmark_vhdmmio(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
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
    registers_folder = output_folder / "vhdmmio"
    build_folder = output_folder / "vivado_project"

    from vhdmmio.config import RegisterFileConfig
    from vhdmmio.core import RegisterFile
    from vhdmmio.version import __version__
    from vhdmmio.vhdl import VhdlEntitiesGenerator

    def run_test() -> None:
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
        generator.generate(output_dir=registers_folder)

    # Run once initially so that artifacts are created.
    # Suppress the printouts so this script prints only a nice table.
    with contextlib.redirect_stdout(None):
        run_test()

    if skip_time:
        time_s = 1
    else:
        # A decent number of runs that gives representative data.
        num_iterations = 15

        # Suppress the printouts so this script prints only a nice table.
        with contextlib.redirect_stdout(None):
            time_taken_s = timeit.timeit(run_test, number=num_iterations)

        check_time(time_taken_s=time_taken_s)

        time_s = time_taken_s / num_iterations

    if skip_resource_usage:
        (lut, ff) = (1, 1)
    else:
        git.Repo.clone_from(
            "git@github.com:abs-tudelft/vhdmmio.git",
            str(output_folder.resolve() / "repo"),
            branch="master",
        )
        copy2(
            output_folder / "repo" / "vhdmmio" / "vhdl" / "vhdmmio_pkg.template.vhd",
            registers_folder / "vhdmmio_pkg.vhd",
        )
        lut, ff = build(registers_folder=registers_folder, build_folder=build_folder, top="basic")

    return __version__, time_s, lut, ff


def benchmark_rggen(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
    """
    Benchmark the "rggen" tool from https://github.com/rggen/rggen
    Uses the "rggen-vhdl" generator from: https://github.com/rggen/rggen-vhdl
    This is a tool written in Ruby, so from a Python-based build flow it needs to be run
    via system calls.

    Need to install ruby from your OS package manager.
    Need to run "gem install --user rggen" and "gem install --user rggen-vhdl".
    Also need to add "~/.gem/ruby/3.0.0/bin" to PATH.
    """
    # Command will give and output like "RgGen 0.31\n"
    version = run_command(["rggen", "--version"], capture_output=True).stdout.strip().split(" ")[1]

    benchmark_folder = BENCHMARK_FOLDER / "rggen"
    registers_folder = output_folder / "rggen"
    build_folder = output_folder / "vivado_project"

    # Create the VHDL files in the source alongside the other VHDL files they require.
    git.Repo.clone_from(
        "git@github.com:rggen/rggen-vhdl-rtl.git", str(registers_folder.resolve()), branch="master"
    )

    def run_test() -> None:
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
            str(benchmark_folder / "rggen_config.yml"),
            "--output",
            str(registers_folder),
            str(benchmark_folder / "rggen_regs.yml"),
        ]
        run_command(command)

    # Run once initially so that artifacts are created.
    run_test()

    if skip_time:
        time_s = 1
    else:
        # A decent number of runs that gives representative data.
        num_iterations = 20

        time_taken_s = timeit.timeit(run_test, number=num_iterations)
        check_time(time_taken_s=time_taken_s)

        time_s = time_taken_s / num_iterations

    if skip_resource_usage:
        (lut, ff) = (1, 1)
    else:
        # Delete the SystemVerilog file, so the generated VHDL is used.
        # So the comparison is as relevant as possible.
        # The VHDL file also has slightly lower resource utilization, so it is also more fair.
        delete(registers_folder / "test.sv")
        lut, ff = build(registers_folder=registers_folder, build_folder=build_folder, top="test")

    return version, time_s, lut, ff


def benchmark_peakrdl(
    output_folder: Path, skip_time: bool, skip_resource_usage: bool
) -> tuple[str, float, int, int]:
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
    # Command will give and output like "1.1.0\n"
    version = run_command(["peakrdl", "--version"], capture_output=True).stdout.strip()

    registers_folder = output_folder / "peakrdl"
    build_folder = output_folder / "vivado_project"

    def run_test() -> None:
        # Configuration file adapted from
        # https://github.com/SystemRDL/PeakRDL/blob/main/examples/atxmega_spi.rdl
        # Registers and fields added so it has 21 registers and 56 fields.
        # So that comparison is fair with the others.
        command = [
            "peakrdl",
            "regblock",
            str(BENCHMARK_FOLDER / "peakrdl" / "peakrdl_config.rdl"),
            "-o",
            str(registers_folder),
            "--cpuif",
            "axi4-lite-flat",
        ]
        run_command(command)

    # Run once initially so that artifacts are created.
    run_test()

    if skip_time:
        time_s = 1
    else:
        # A decent number of runs that gives representative data.
        num_iterations = 20

        time_taken_s = timeit.timeit(run_test, number=num_iterations)
        check_time(time_taken_s=time_taken_s)

        time_s = time_taken_s / num_iterations

    if skip_resource_usage:
        (lut, ff) = (1, 1)
    else:
        lut, ff = build(
            registers_folder=registers_folder, build_folder=build_folder, top="atxmega_spi"
        )

    return version, time_s, lut, ff


if __name__ == "__main__":
    main()
