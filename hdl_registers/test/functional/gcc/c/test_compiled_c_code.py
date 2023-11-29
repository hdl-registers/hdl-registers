# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path

# Third party libraries
import pytest
from tsfpga.system_utils import create_file, run_command

# First party libraries
from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.test.functional.gcc.compile_and_run_test import CompileAndRunTest

THIS_DIR = Path(__file__).parent.resolve()


class CTest(CompileAndRunTest):
    def compile_and_run(self, test_constants, test_registers):
        CHeaderGenerator(self.register_list, self.include_dir).create()

        main_file = self.working_dir / "main.c"

        executable = self.working_dir / "test.o"

        compile_command = [
            "gcc",
            f"-o{executable}",
            f"-I{THIS_DIR / 'include'}",
            f"-I{self.include_dir}",
            str(main_file),
        ]

        tests = ["test_constants"] if test_constants else []
        tests += ["test_registers"] if test_registers else []

        includes = "\n  ".join([f'#include "{test}.h"' for test in tests])
        main_function = "\n  ".join([f"{test}();" for test in tests])
        compile_command += [str(THIS_DIR / f"{test}.c") for test in tests]

        main_file = self.working_dir / "main.c"
        main = f"""\
#include <assert.h>
#include <stdint.h>

#include "caesar_regs.h"

{includes}

int main()
{{
  assert(CAESAR_NUM_REGS == {21 * test_registers});

{main_function}

  return 0;
}}
"""
        create_file(main_file, main)

        run_command(compile_command)

        run_command([executable])


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


@pytest.fixture
def c_test(tmp_path):
    return CTest(tmp_path=tmp_path)


def test_c_header_with_registers_and_constants(c_test):
    c_test.compile_and_run(test_registers=True, test_constants=True)


def test_c_header_with_only_registers(c_test):
    c_test.register_list.constants = []
    c_test.compile_and_run(test_registers=True, test_constants=False)


def test_c_header_with_only_constants(c_test):
    c_test.register_list.register_objects = []
    c_test.compile_and_run(test_registers=False, test_constants=True)
