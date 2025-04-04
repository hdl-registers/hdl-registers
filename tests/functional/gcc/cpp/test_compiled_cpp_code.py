# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import subprocess
from pathlib import Path

import pytest
from tsfpga.system_utils import create_file, run_command

from hdl_registers.generator.cpp.header import CppHeaderGenerator
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.vhdl.test.test_register_vhdl_generator import (
    get_all_doc_register_lists,
    get_strange_register_lists,
)
from hdl_registers.register_modes import REGISTER_MODES
from tests.functional.gcc.compile_and_run_test import CompileAndRunTest

THIS_DIR = Path(__file__).parent.resolve()


class BaseCppTest(CompileAndRunTest):
    @staticmethod
    def get_main(includes="", test_code=""):
        return f"""\
#include <iostream>
#include <cassert>

#include "include/caesar.h"

{includes}

bool register_assert_handler(const std::string *diagnostic_message)
{{
  std::cerr << *diagnostic_message << std::endl;
  std::exit(EXIT_FAILURE);
  return true;
}}

int main()
{{
  uint32_t memory[fpga_regs::Caesar::num_registers];
  uintptr_t base_address = reinterpret_cast<uintptr_t>(memory);
  fpga_regs::Caesar caesar = fpga_regs::Caesar(base_address, register_assert_handler);

{test_code}

  return 0;
}}
"""

    def compile(
        self,
        test_code="",
        include_directories=None,
        source_files=None,
        includes="",
        no_getter_assert=False,
        no_setter_assert=False,
        no_array_index_assert=False,
    ):
        include_directories = [] if include_directories is None else include_directories
        source_files = [] if source_files is None else source_files

        defines = []
        if no_getter_assert:
            defines.append("-DNO_REGISTER_GETTER_ASSERT")
        if no_setter_assert:
            defines.append("-DNO_REGISTER_SETTER_ASSERT")
        if no_array_index_assert:
            defines.append("-DNO_REGISTER_ARRAY_INDEX_ASSERT")

        CppInterfaceGenerator(self.register_list, self.include_dir).create()
        CppHeaderGenerator(self.register_list, self.include_dir).create()
        CppImplementationGenerator(self.register_list, self.working_dir).create()
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
            + defines
        )

        create_file(file=main_file, contents=self.get_main(includes=includes, test_code=test_code))

        try:
            result = run_command(compile_command, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            print(e.stdout)
            raise
        assert result.stderr == ""
        assert result.stdout == ""

        # Return the command that runs the executable.
        return [str(executable)]


@pytest.fixture
def base_cpp_test(tmp_path):
    return BaseCppTest(tmp_path=tmp_path)


class CppTest(BaseCppTest):
    def compile_and_run(self, test_constants, test_registers):
        test_code = f"  assert(fpga_regs::Caesar::num_registers == {21 * test_registers});\n"

        tests = ["test_constants"] if test_constants else []
        tests += ["test_registers"] if test_registers else []

        includes = "\n".join([f'#include "{test}.h"' for test in tests])
        test_code += "\n  ".join([f"{test}(memory, &caesar);" for test in tests])
        source_files = [THIS_DIR / f"{test}.cpp" for test in tests]

        cmd = self.compile(
            test_code=test_code,
            include_directories=[THIS_DIR / "include"],
            source_files=source_files,
            includes=includes,
        )

        try:
            result = run_command(cmd, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            print(e.stdout)
            raise

        assert result.stderr == ""
        assert result.stdout == ""


@pytest.fixture
def cpp_test(tmp_path):
    return CppTest(tmp_path=tmp_path)


def test_registers_and_constants(cpp_test):
    cpp_test.compile_and_run(test_registers=True, test_constants=True)


def test_only_registers(cpp_test):
    cpp_test.register_list.constants = []
    cpp_test.compile_and_run(test_registers=True, test_constants=False)


def test_only_constants(cpp_test):
    cpp_test.register_list.register_objects = []
    cpp_test.compile_and_run(test_registers=False, test_constants=True)


def test_setting_register_array_out_of_bounds_should_crash(base_cpp_test):
    test_code = """\
  // Index 3 is out of bounds (should be less than 3)
  caesar.set_dummies_first_array_integer(3, 1337);
"""
    cmd = base_cpp_test.compile(test_code=test_code)

    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:1277: Got 'dummies' array index out of range: 3.\n"
    )


def test_setting_register_array_out_of_bounds_should_not_crash_if_no_assertion(base_cpp_test):
    test_code = """\
  // Index 3 is out of bounds (should be less than 3)
  caesar.set_dummies_first_array_integer(3, 42);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(cmd=cmd)

    cmd = base_cpp_test.compile(test_code=test_code, no_array_index_assert=True)
    run_command(cmd=cmd)


def test_setting_bit_field_out_of_range_should_crash(base_cpp_test):
    test_code = """\
  caesar.set_conf_plain_bit_a(1);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd, capture_output=True)

    test_code = """\
  caesar.set_conf_plain_bit_a(2);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:282: Got 'plain_bit_a' value too many bits used: 2.\n"
    )


def test_setting_bit_vector_field_out_of_range_should_crash(base_cpp_test):
    test_code = """\
  caesar.set_conf_plain_bit_vector(15);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd, capture_output=True)

    test_code = """\
  caesar.set_conf_plain_bit_vector(16);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:316: Got 'plain_bit_vector' value too many bits used: 16.\n"
    )


def test_setting_integer_field_out_of_range_should_crash(base_cpp_test):
    test_code = """\
  caesar.set_conf_plain_integer(-1024);
"""
    cmd = base_cpp_test.compile(test_code=test_code)

    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:349: Got 'plain_integer' value too small: -1024.\n"
    )

    test_code = """\
  caesar.set_conf_plain_integer(110);
"""
    cmd = base_cpp_test.compile(test_code=test_code)

    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:353: Got 'plain_integer' value too large: 110.\n"
    )


def test_setting_integer_field_out_of_range_should_not_crash_if_no_assertion(base_cpp_test):
    test_code = """\
  caesar.set_conf_plain_integer(-1024);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(cmd=cmd)

    cmd = base_cpp_test.compile(test_code=test_code, no_setter_assert=True)
    run_command(cmd=cmd)


def test_getting_integer_field_out_of_range_should_crash(base_cpp_test):
    # 'config' register is index 0 and 'plain_integer' field starts at bit 9.
    test_code = """\
  memory[0] = 100 << 5;
  caesar.get_conf_plain_integer();
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd, capture_output=True)

    test_code = """\
  memory[0] = 101 << 5;
  caesar.get_conf_plain_integer();
"""
    cmd = base_cpp_test.compile(test_code=test_code)

    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:186: Got 'plain_integer' value too large: 101.\n"
    )

    test_code = """\
  memory[0] = -51 << 5;
  caesar.get_conf_plain_integer();
"""
    cmd = base_cpp_test.compile(test_code=test_code)

    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:182: Got 'plain_integer' value too small: -51.\n"
    )


def test_getting_integer_field_out_of_range_should_not_crash_if_no_assertion(base_cpp_test):
    test_code = """\
  memory[0] = 101 << 5;
  caesar.get_conf_plain_integer();
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError):
        run_command(cmd=cmd)

    cmd = base_cpp_test.compile(test_code=test_code, no_getter_assert=True)
    run_command(cmd=cmd)


def test_very_wide_bit_vector_fields(base_cpp_test):
    base_cpp_test.register_list.append_register(
        name="vector_32", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(name="value", description="", width=32, default_value=0)

    base_cpp_test.register_list.append_register(
        name="vector_31", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(name="value", description="", width=31, default_value=0)

    test_code = """\
  memory[21] = 0b10000000000000000000000000000001;
  memory[22] = 0b11000000000000000000000000000001;

  assert(caesar.get_vector_32_value() == 2147483649);
  assert(caesar.get_vector_31_value() == 1073741825);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_very_wide_integer_fields(base_cpp_test):
    base_cpp_test.register_list.append_register(
        name="signed_32", mode=REGISTER_MODES["r_w"], description=""
    ).append_integer(
        name="value", description="", min_value=-2147483648, max_value=3, default_value=-25
    )

    base_cpp_test.register_list.append_register(
        name="unsigned_32", mode=REGISTER_MODES["r_w"], description=""
    ).append_integer(
        name="value", description="", min_value=7, max_value=2147483649, default_value=2147483648
    )

    base_cpp_test.register_list.append_register(
        name="signed_31", mode=REGISTER_MODES["r_w"], description=""
    ).append_integer(
        name="value", description="", min_value=-1073741824, max_value=3, default_value=-25
    )

    base_cpp_test.register_list.append_register(
        name="unsigned_31", mode=REGISTER_MODES["r_w"], description=""
    ).append_integer(
        name="value", description="", min_value=7, max_value=1073741825, default_value=1073741824
    )

    test_code = """\
  assert(fpga_regs::caesar::signed_32::value::mask_at_base == 0xFFFFFFFF);
  assert(fpga_regs::caesar::signed_32::value::mask_shifted == 0xFFFFFFFF);
  assert(fpga_regs::caesar::signed_32::value::default_value == -25);
  assert(fpga_regs::caesar::signed_32::value::default_value_raw == 4294967271);

  assert(fpga_regs::caesar::unsigned_32::value::mask_at_base == 0xFFFFFFFF);
  assert(fpga_regs::caesar::unsigned_32::value::mask_shifted == 0xFFFFFFFF);
  assert(fpga_regs::caesar::unsigned_32::value::default_value == 2147483648);
  assert(fpga_regs::caesar::unsigned_32::value::default_value_raw == 2147483648);

  assert(fpga_regs::caesar::signed_31::value::mask_at_base == 0x7FFFFFFF);
  assert(fpga_regs::caesar::signed_31::value::mask_shifted == 0x7FFFFFFF);
  assert(fpga_regs::caesar::signed_31::value::default_value == -25);
  assert(fpga_regs::caesar::signed_31::value::default_value_raw == 2147483623);

  assert(fpga_regs::caesar::unsigned_31::value::mask_at_base == 0x7FFFFFFF);
  assert(fpga_regs::caesar::unsigned_31::value::mask_shifted == 0x7FFFFFFF);
  assert(fpga_regs::caesar::unsigned_31::value::default_value == 1073741824);
  assert(fpga_regs::caesar::unsigned_31::value::default_value_raw == 1073741824);

  memory[21] = 0b10000000000000000000000000000001;
  memory[22] = 0b10000000000000000000000000000001;
  memory[23] = 0b11000000000000000000000000000001;
  memory[24] = 0b11000000000000000000000000000001;

  assert(caesar.get_signed_32_value() == -2147483647);
  assert(caesar.get_unsigned_32_value() == 2147483649);
  assert(caesar.get_signed_31_value() == -1073741823);
  assert(caesar.get_unsigned_31_value() == 1073741825);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_very_wide_integer_field_slightly_offset(base_cpp_test):
    register = base_cpp_test.register_list.append_register(
        name="signed_31", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit(name="pad", description="", default_value="0")
    register.append_integer(
        name="value", description="", min_value=-1073741824, max_value=3, default_value=-1073741809
    )

    register = base_cpp_test.register_list.append_register(
        name="unsigned_31", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit(name="pad", description="", default_value="0")
    register.append_integer(
        name="value", description="", min_value=0, max_value=2147483647, default_value=1073741839
    )

    register = base_cpp_test.register_list.append_register(
        name="signed_30", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit(name="pad", description="", default_value="0")
    register.append_integer(
        name="value", description="", min_value=-536870912, max_value=3, default_value=-536870897
    )
    register.append_bit(name="pad2", description="", default_value="0")

    register = base_cpp_test.register_list.append_register(
        name="unsigned_30", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit(name="pad", description="", default_value="0")
    register.append_integer(
        name="value", description="", min_value=0, max_value=1073741823, default_value=536870927
    )
    register.append_bit(name="pad2", description="", default_value="1")

    test_code = """\
  assert(fpga_regs::caesar::signed_31::value::mask_at_base == 0x7FFFFFFF);
  assert(fpga_regs::caesar::signed_31::value::mask_shifted == 0xFFFFFFFE);
  assert(fpga_regs::caesar::signed_31::value::default_value == -1073741809);
  assert(fpga_regs::caesar::signed_31::value::default_value_raw == 2147483678);

  assert(fpga_regs::caesar::unsigned_31::value::mask_at_base == 0x7FFFFFFF);
  assert(fpga_regs::caesar::unsigned_31::value::mask_shifted == 0xFFFFFFFE);
  assert(fpga_regs::caesar::unsigned_31::value::default_value == 1073741839);
  assert(fpga_regs::caesar::unsigned_31::value::default_value_raw == 2147483678);

  assert(fpga_regs::caesar::signed_30::value::mask_at_base == 0x3FFFFFFF);
  assert(fpga_regs::caesar::signed_30::value::mask_shifted == 0x7FFFFFFE);
  assert(fpga_regs::caesar::signed_30::value::default_value == -536870897);
  assert(fpga_regs::caesar::signed_30::value::default_value_raw == 1073741854);

  assert(fpga_regs::caesar::unsigned_30::value::mask_at_base == 0x3FFFFFFF);
  assert(fpga_regs::caesar::unsigned_30::value::mask_shifted == 0x7FFFFFFE);
  assert(fpga_regs::caesar::unsigned_30::value::default_value == 536870927);
  assert(fpga_regs::caesar::unsigned_30::value::default_value_raw == 1073741854);

  caesar.set_unsigned_31_value(0b1010101010101010101010101010101);
  assert(caesar.get_unsigned_31_value() == 0b1010101010101010101010101010101);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_compile_all_register_lists(base_cpp_test):
    """
    Test that all available register lists compile.
    """
    includes = ""

    for register_list in get_strange_register_lists() + get_all_doc_register_lists():
        CppImplementationGenerator(
            register_list=register_list, output_folder=base_cpp_test.working_dir
        ).create()
        CppHeaderGenerator(
            register_list=register_list, output_folder=base_cpp_test.include_dir
        ).create()
        CppInterfaceGenerator(
            register_list=register_list, output_folder=base_cpp_test.include_dir
        ).create()

        includes += f'#include "include/{register_list.name}.h"\n'

    cmd = base_cpp_test.compile(includes=includes)
    run_command(cmd=cmd)
