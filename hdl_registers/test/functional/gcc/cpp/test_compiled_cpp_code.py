# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import subprocess
from pathlib import Path

# Third party libraries
import pytest
from tsfpga.system_utils import create_file, run_command

# First party libraries
from hdl_registers.test.functional.gcc.compile_and_run_test import CompileAndRunTest

THIS_DIR = Path(__file__).parent.resolve()


class BaseCppTest(CompileAndRunTest):
    @staticmethod
    def get_main(includes="", test_code=""):
        return f"""\
#include <assert.h>

#include "include/caesar.h"

{includes}

int main()
{{
  uint32_t memory[fpga_regs::Caesar::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(memory);
  fpga_regs::Caesar caesar = fpga_regs::Caesar(base_address);

  {test_code}

  return 0;
}}
"""

    def compile(self, test_code, include_directories=None, source_files=None, includes=""):
        include_directories = [] if include_directories is None else include_directories
        source_files = [] if source_files is None else source_files

        self.registers.create_cpp_interface(self.include_dir)
        self.registers.create_cpp_header(self.include_dir)
        self.registers.create_cpp_implementation(self.working_dir)
        cpp_class_file = self.working_dir / "caesar.cpp"

        main_file = self.working_dir / "main.cpp"

        executable = self.working_dir / "test.o"

        compile_command = (
            [
                "g++",
                f"-o{executable}",
                f"-I{self.include_dir}",
                main_file,
                cpp_class_file,
            ]
            + [f"-I{path}" for path in include_directories]
            + source_files
        )

        create_file(file=main_file, contents=self.get_main(includes=includes, test_code=test_code))

        run_command(compile_command)

        return executable


@pytest.fixture
def base_cpp_test(tmp_path):
    return BaseCppTest(tmp_path=tmp_path)


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


class CppTest(BaseCppTest):
    def compile_and_run(self, test_constants, test_registers):
        test_code = f"  assert(fpga_regs::Caesar::num_registers == {19 * test_registers});\n"

        tests = ["test_constants"] if test_constants else []
        tests += ["test_registers"] if test_registers else []

        includes = "\n".join([f'#include "{test}.h"' for test in tests])
        test_code += "\n  ".join([f"{test}(memory, &caesar);" for test in tests])
        source_files = [THIS_DIR / f"{test}.cpp" for test in tests]

        executable = self.compile(
            test_code=test_code,
            include_directories=[THIS_DIR / "include"],
            source_files=source_files,
            includes=includes,
        )

        run_command([executable])


@pytest.fixture
def cpp_test(tmp_path):
    return CppTest(tmp_path=tmp_path)


def test_cpp_with_registers_and_constants(cpp_test):
    cpp_test.compile_and_run(test_registers=True, test_constants=True)


def test_cpp_with_only_registers(cpp_test):
    cpp_test.registers.constants = []
    cpp_test.compile_and_run(test_registers=True, test_constants=False)


def test_cpp_with_only_constants(cpp_test):
    cpp_test.registers.register_objects = []
    cpp_test.compile_and_run(test_registers=False, test_constants=True)


def test_setting_cpp_register_array_out_of_bounds_should_crash(base_cpp_test):
    test_code = """\
  // Index 3 is out of bounds (should be less than 3)
  caesar.set_dummies_first(3, 1337);
"""
    executable = base_cpp_test.compile(test_code=test_code)

    with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
        stderr = process.communicate()
    assert "Assertion `array_index < dummies_array_length' failed" in str(stderr), stderr


def test_setting_cpp_integer_field_out_of_range_should_crash(base_cpp_test):
    test_code = """\
  caesar.set_config_plain_integer(-1024);
"""
    executable = base_cpp_test.compile(test_code=test_code)

    with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
        stderr = process.communicate()
    assert "Assertion `field_value >= -50' failed." in str(stderr), stderr

    test_code = """\
  caesar.set_config_plain_integer(110);
"""
    executable = base_cpp_test.compile(test_code=test_code)

    with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
        stderr = process.communicate()
    assert "Assertion `field_value <= 100' failed." in str(stderr), stderr
