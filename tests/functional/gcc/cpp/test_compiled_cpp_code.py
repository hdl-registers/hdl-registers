# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import re
import subprocess
from pathlib import Path

import pytest
from tsfpga.system_utils import create_file, run_command

from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    UnsignedFixedPoint,
)
from hdl_registers.generator.cpp.header import CppHeaderGenerator
from hdl_registers.generator.cpp.implementation import CppImplementationGenerator
from hdl_registers.generator.cpp.interface import CppInterfaceGenerator
from hdl_registers.generator.vhdl.test.test_vhdl import (
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
#include <cassert>
#include <iostream>
#include <iomanip>

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
        test_code = f"  assert(fpga_regs::Caesar::num_registers == {22 * test_registers});\n"

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
        "caesar.cpp:1238: Got 'dummies' array index out of range: 3.\n"
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
        "caesar.cpp:290: Got 'plain_bit_vector' value out of range: 16.\n"
    )


def test_setting_bit_vector_signed_field_out_of_range_should_crash(base_cpp_test):
    base_cpp_test.register_list.append_register(
        name="apa", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(
        name="value1",
        description="",
        width=8,
        default_value=0,
        numerical_interpretation=Signed(bit_width=8),
    )
    test_code = """\
  caesar.set_apa_value1(15);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd, capture_output=True)

    test_code = """\
  caesar.set_apa_value1(128);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert re.fullmatch(
        "caesar.cpp:\\d+: Got 'value1' value out of range: 128.\n", exception_info.value.stderr
    )

    test_code = """\
  caesar.set_apa_value1(-129);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert re.fullmatch(
        "caesar.cpp:\\d+: Got 'value1' value out of range: -129.\n", exception_info.value.stderr
    )


def test_setting_bit_vector_unsigned_fixed_point_field_out_of_range_should_crash(base_cpp_test):
    base_cpp_test.register_list.append_register(
        name="apa", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(
        name="value1",
        description="",
        width=8,
        default_value=0,
        numerical_interpretation=UnsignedFixedPoint(max_bit_index=3, min_bit_index=-4),
    )
    test_code = """\
  caesar.set_apa_value1(15.125);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd, capture_output=True)

    test_code = """\
  caesar.set_apa_value1(16);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert re.fullmatch(
        "caesar.cpp:\\d+: Got 'value1' value out of range: 16.\n", exception_info.value.stderr
    )

    test_code = """\
  caesar.set_apa_value1(-0.5);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert re.fullmatch(
        "caesar.cpp:\\d+: Got 'value1' value out of range: -0.5.\n", exception_info.value.stderr
    )


def test_setting_bit_vector_signed_fixed_point_field_out_of_range_should_crash(base_cpp_test):
    base_cpp_test.register_list.append_register(
        name="apa", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(
        name="value1",
        description="",
        width=8,
        default_value=0,
        numerical_interpretation=SignedFixedPoint(max_bit_index=3, min_bit_index=-4),
    )
    test_code = """\
  caesar.set_apa_value1(7.125);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd, capture_output=True)

    test_code = """\
  caesar.set_apa_value1(8);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert re.fullmatch(
        "caesar.cpp:\\d+: Got 'value1' value out of range: 8.\n", exception_info.value.stderr
    )

    test_code = """\
  caesar.set_apa_value1(-9.125);
"""
    cmd = base_cpp_test.compile(test_code=test_code)
    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert re.fullmatch(
        "caesar.cpp:\\d+: Got 'value1' value out of range: -9.125.\n", exception_info.value.stderr
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
        "caesar.cpp:322: Got 'plain_integer' value out of range: -1024.\n"
    )

    test_code = """\
  caesar.set_conf_plain_integer(110);
"""
    cmd = base_cpp_test.compile(test_code=test_code)

    with pytest.raises(subprocess.CalledProcessError) as exception_info:
        run_command(cmd=cmd, capture_output=True)

    assert exception_info.value.output == ""
    assert exception_info.value.stderr == (
        "caesar.cpp:322: Got 'plain_integer' value out of range: 110.\n"
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
        "caesar.cpp:156: Got 'plain_integer' value out of range: 101.\n"
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
        "caesar.cpp:156: Got 'plain_integer' value out of range: -51.\n"
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


def test_bit_field_at_the_top(base_cpp_test):
    register = base_cpp_test.register_list.append_register(
        name="bit_reg", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(name="pad", description="", width=31, default_value=0)
    register.append_bit(name="value", description="", default_value="0")

    register = base_cpp_test.register_list.append_register(
        name="bit_reg2", mode=REGISTER_MODES["w"], description=""
    )
    register.append_bit_vector(name="pad", description="", width=31, default_value=0)
    register.append_bit(name="value", description="", default_value="1")

    test_code = """\
  assert(fpga_regs::caesar::bit_reg::value::mask_at_base == 1);
  assert(fpga_regs::caesar::bit_reg::value::mask_shifted == 0x80000000);
  assert(fpga_regs::caesar::bit_reg::value::default_value == false);
  assert(fpga_regs::caesar::bit_reg::value::default_value_raw == 0);

  assert(fpga_regs::caesar::bit_reg2::value::mask_at_base == 1);
  assert(fpga_regs::caesar::bit_reg2::value::mask_shifted == 0x80000000);
  assert(fpga_regs::caesar::bit_reg2::value::default_value == true);
  assert(fpga_regs::caesar::bit_reg2::value::default_value_raw == 2147483648);

  caesar.set_bit_reg_value(true);
  assert(caesar.get_bit_reg_value() == true);
  caesar.set_bit_reg_value(false);
  assert(caesar.get_bit_reg_value() == false);

  caesar.set_bit_reg2_pad(3);
  assert(memory[fpga_regs::Caesar::num_registers - 1] == 0x80000003);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_very_wide_bit_vector_fields(base_cpp_test):
    base_cpp_test.register_list.append_register(
        name="vector_32", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(name="value", description="", width=32, default_value=0)

    base_cpp_test.register_list.append_register(
        name="vector_31", mode=REGISTER_MODES["r_w"], description=""
    ).append_bit_vector(name="value", description="", width=31, default_value=0)

    test_code = """\
  memory[fpga_regs::Caesar::num_registers - 2] = 0b10000000000000000000000000000001;
  memory[fpga_regs::Caesar::num_registers - 1] = 0b11000000000000000000000000000001;

  assert(caesar.get_vector_32_value() == 2147483649);
  assert(caesar.get_vector_31_value() == 1073741825);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_signed_bit_vector_field(base_cpp_test):
    register = base_cpp_test.register_list.append_register(
        name="apa", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(
        name="value1",
        description="",
        width=14,
        default_value=4111,
        numerical_interpretation=Signed(bit_width=14),
    )
    register.append_bit_vector(
        name="value2",
        description="",
        width=14,
        default_value=-8177,
        numerical_interpretation=Signed(bit_width=14),
    )

    test_code = """\
  assert(fpga_regs::caesar::apa::value1::default_value == 4111);
  assert(fpga_regs::caesar::apa::value1::default_value_raw == 4111);

  assert(fpga_regs::caesar::apa::value2::default_value == -8177);
  assert(fpga_regs::caesar::apa::value2::default_value_raw == 134463488);

  caesar.set_apa({1337, -127});
  assert(caesar.get_apa_value1() == 1337);
  assert(caesar.get_apa_value2() == -127);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_unsigned_fixed_point_bit_vector_field(base_cpp_test):
    register = base_cpp_test.register_list.append_register(
        name="apa", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(
        name="value1",
        description="",
        width=14,
        default_value=16.05859375,
        numerical_interpretation=UnsignedFixedPoint(max_bit_index=5, min_bit_index=-8),
    )
    register.append_bit_vector(
        name="value2",
        description="",
        width=14,
        default_value=15.94140625,
        numerical_interpretation=UnsignedFixedPoint(max_bit_index=5, min_bit_index=-8),
    )

    test_code = """\
  assert(fpga_regs::caesar::apa::value1::default_value == 16.05859375);
  assert(fpga_regs::caesar::apa::value1::default_value_raw == 4111);

  assert(fpga_regs::caesar::apa::value2::default_value == 15.94140625);
  assert(fpga_regs::caesar::apa::value2::default_value_raw == 66863104);

  // Values that fit perfectly with no rounding/truncation.
  caesar.set_apa({21.33203125, 10.6640625});
  assert(caesar.get_apa_value1() == 21.33203125);
  assert(caesar.get_apa_value2() == 10.6640625);
  assert(memory[fpga_regs::Caesar::num_registers - 1] == 44728320 + 5461);

  // One value is truncated, the other is unchanged.
  caesar.set_apa_value1(21.332031251);
  assert(caesar.get_apa_value1() == 21.33203125);
  assert(caesar.get_apa_value2() == 10.6640625);

  // Will round to the same fixed-point value as above.
  caesar.set_apa_value1(21.332031);
  assert(caesar.get_apa_value1() == 21.33203125);
"""

    cmd = base_cpp_test.compile(test_code=test_code)
    run_command(cmd=cmd)


def test_signed_fixed_point_bit_vector_field(base_cpp_test):
    register = base_cpp_test.register_list.append_register(
        name="apa", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(
        name="value1",
        description="",
        width=14,
        default_value=-63.765625,
        numerical_interpretation=SignedFixedPoint(max_bit_index=7, min_bit_index=-6),
    )
    register.append_bit_vector(
        name="value2",
        description="",
        width=14,
        default_value=67.796875,
        numerical_interpretation=SignedFixedPoint(max_bit_index=7, min_bit_index=-6),
    )

    test_code = """\
  assert(fpga_regs::caesar::apa::value1::default_value == -63.765625);
  assert(fpga_regs::caesar::apa::value1::default_value_raw == 12303);

  assert(fpga_regs::caesar::apa::value2::default_value == 67.796875);
  assert(fpga_regs::caesar::apa::value2::default_value_raw == 71090176);

  // Values that fit perfectly with no rounding/truncation.
  caesar.set_apa({-53.390625, 74.859375});
  assert(memory[fpga_regs::Caesar::num_registers - 1] == 78495744 + 12967);
  assert(caesar.get_apa_value1() == -53.390625);
  assert(caesar.get_apa_value2() == 74.859375);

  // One value is truncated, the other is unchanged.
  caesar.set_apa_value1(-53.3906251);
  assert(caesar.get_apa_value1() == -53.390625);
  assert(caesar.get_apa_value2() == 74.859375);

  // Will round to the same fixed-point value as above.
  caesar.set_apa_value1(-53.390624);
  assert(caesar.get_apa_value1() == -53.390625);
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

  memory[fpga_regs::Caesar::num_registers - 4] = 0b10000000000000000000000000000001;
  memory[fpga_regs::Caesar::num_registers - 3] = 0b10000000000000000000000000000001;
  memory[fpga_regs::Caesar::num_registers - 2] = 0b11000000000000000000000000000001;
  memory[fpga_regs::Caesar::num_registers - 1] = 0b11000000000000000000000000000001;

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


def test_wmasked_registers(base_cpp_test):
    # There is already one 'wmasked' register in the base register list.
    # Test an empty 'wmasked' register with also, since that is handled differently in the code.
    base_cpp_test.register_list.append_register(
        name="instruction2", mode=REGISTER_MODES["wmasked"], description=""
    )

    # And one in an array also, since that is handled differently in the code.
    base_cpp_test.register_list.append_register_array(
        name="instructions", length=2, description=""
    ).append_register(
        name="instruction3", mode=REGISTER_MODES["wmasked"], description=""
    ).append_bit(name="hest", description="", default_value="0")

    test_code = """\
  assert(fpga_regs::caesar::instruction::a::width == 5);
  assert(fpga_regs::caesar::instruction::a::shift == 0);
  assert(fpga_regs::caesar::instruction::mask::width == 5);
  assert(fpga_regs::caesar::instruction::mask::shift == 16);

  assert(fpga_regs::caesar::instruction2::mask::width == 16);
  assert(fpga_regs::caesar::instruction2::mask::shift == 16);

  assert(fpga_regs::caesar::instructions::instruction3::hest::width == 1);
  assert(fpga_regs::caesar::instructions::instruction3::hest::shift == 0);
  assert(fpga_regs::caesar::instructions::instruction3::mask::width == 1);
  assert(fpga_regs::caesar::instructions::instruction3::mask::shift == 16);
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
