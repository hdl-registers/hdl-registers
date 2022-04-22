# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

import subprocess
import unittest

import pytest

from tsfpga.system_utils import create_file, run_command

from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.parser import from_toml


@pytest.mark.usefixtures("fixture_tmp_path")
class TestRegisterCompilation(unittest.TestCase):
    """
    Functional test: TOML -> registers -> Code generation -> compilation -> set/check/assert
    """

    tmp_path = None

    def setUp(self):
        self.working_dir = self.tmp_path
        self.include_dir = self.working_dir / "include"

        toml_file = HDL_REGISTERS_TEST / "regs_test.toml"
        self.registers = from_toml("test", toml_file)

        self.registers.add_constant("data_width", 24)
        self.registers.add_constant("decrement", -8)

    def _compile_and_test_c_header(self, test_constants, test_registers):
        main_function = ""
        functions = ""
        if test_constants:
            main_function += "  test_constants();\n"

            functions += """
void test_constants()
{
  assert(TEST_DATA_WIDTH == 24);
  assert(TEST_DECREMENT == -8);
}
"""

        if not test_registers:
            # If no registers, the constant shall be zero
            main_function += "  assert(TEST_NUM_REGS == 0);\n"
        else:
            main_function += """\
  assert(TEST_NUM_REGS == 8);
  test_addresses();
  test_bit_indexes();
  test_generated_type();
"""

            functions += """
void test_addresses()
{
  // Assert that indexes are correct
  assert(TEST_PLAIN_DUMMY_REG_INDEX == 0);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(0) == 1);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(0) == 2);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(1) == 3);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(1) == 4);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(2) == 5);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(2) == 6);

  // Assert that addresses are correct
  assert(TEST_PLAIN_DUMMY_REG_ADDR == 0);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(0) == 4);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(0) == 8);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(1) == 12);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(1) == 16);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(2) == 20);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(2) == 24);
  assert(TEST_FURTHER_REGS_DUMMY_REG_ADDR(0) == 28);
  // Last register
  assert(TEST_FURTHER_REGS_DUMMY_REG_ADDR(0) == 4 * (TEST_NUM_REGS - 1));
}

void test_bit_indexes()
{
  // Assert bit indexes of plain register
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_SHIFT == 0);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_MASK == 1);

  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_SHIFT == 1);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_MASK == 2);

  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_SHIFT == 2);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_MASK == 15 << 2);

  // Assert bit indexes of array register
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_SHIFT == 0);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_MASK == 1);

  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_SHIFT == 1);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_MASK == 2);

  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_SHIFT == 2);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_MASK == 15 << 2);
}

void test_generated_type()
{
  // Assert positions within the generated type
  test_regs_t regs;
  assert(sizeof(regs) == 4 * TEST_NUM_REGS);

  assert((void *)&regs == (void *)&regs.plain_dummy_reg);
  assert((void *)&regs + 4 == (void *)&regs.dummy_regs[0].array_dummy_reg);
  assert((void *)&regs + 8 == (void *)&regs.dummy_regs[0].second_array_dummy_reg);
  assert((void *)&regs + 12 == (void *)&regs.dummy_regs[1].array_dummy_reg);
  assert((void *)&regs + 16 == (void *)&regs.dummy_regs[1].second_array_dummy_reg);
  assert((void *)&regs + 20 == (void *)&regs.dummy_regs[2].array_dummy_reg);
  assert((void *)&regs + 24 == (void *)&regs.dummy_regs[2].second_array_dummy_reg);
  assert((void *)&regs + 28 == (void *)&regs.further_regs[0].dummy_reg);

  // Some dummy code that uses the generated type
  regs.plain_dummy_reg = 0;
  regs.dummy_regs[0].array_dummy_reg = TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK;
  regs.dummy_regs[2].second_array_dummy_reg =
    (1 << TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_SHIFT);
}
"""

        main_file = self.working_dir / "main.c"
        main = f"""\
#include <assert.h>
#include <stdint.h>
#include "test_regs.h"

{functions}

int main()
{{
{main_function}

  return 0;
}}
"""
        create_file(main_file, main)
        self.registers.create_c_header(self.include_dir)

        executable = self.working_dir / "test.o"
        cmd = ["gcc", main_file, f"-o{executable}", f"-I{self.include_dir}"]
        run_command(cmd)
        run_command([executable])

    def test_c_header_with_registers_and_constants(self):
        self._compile_and_test_c_header(test_registers=True, test_constants=True)

    def test_c_header_with_only_registers(self):
        self.registers.constants = []
        self._compile_and_test_c_header(test_registers=True, test_constants=False)

    def test_c_header_with_only_constants(self):
        self.registers.register_objects = []
        self._compile_and_test_c_header(test_registers=False, test_constants=True)

    def _compile_and_test_cpp(self, test_registers, test_constants):
        main_function = ""
        functions = ""
        if test_constants:
            main_function += "  test_constants();\n"

            functions += """\
void test_constants()
{
  assert(fpga_regs::Test::data_width == 24);
  assert(fpga_regs::Test::decrement == -8);
}

"""

        if not test_registers:
            # If no registers, the constant shall be zero
            main_function += "  assert(fpga_regs::Test::num_registers == 0);\n"
        else:
            main_function += """\
  assert(fpga_regs::Test::num_registers == 8);
  assert(fpga_regs::Test::dummy_regs_array_length == 3);

  // Allocate memory and instantiate the register class
  uint32_t memory[fpga_regs::Test::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(memory);
  fpga_regs::Test test = fpga_regs::Test(base_address);

  test_read_write_registers(&test, memory);
  test_bit_indexes();
"""

            functions += """\
void test_read_write_registers(fpga_regs::Test *test, uint32_t *memory)
{
  // Set data and then check, according to the expected register addresses.
  // Data is a ramp 0-6.
  test->set_plain_dummy_reg(0);
  test->set_dummy_regs_array_dummy_reg(0, 1);
  // second_array_dummy_reg is read only, so set the value in the memory straight away
  memory[2] = 2;
  test->set_dummy_regs_array_dummy_reg(1, 3);
  memory[4] = 4;
  test->set_dummy_regs_array_dummy_reg(2, 5);
  memory[6] = 6;
  test->set_further_regs_dummy_reg(0, 7);

  assert(test->get_plain_dummy_reg() == 0);
  assert(memory[0] == 0);

  assert(test->get_dummy_regs_array_dummy_reg(0) == 1);
  assert(memory[1] == 1);

  assert(test->get_dummy_regs_second_array_dummy_reg(0) == 2);
  assert(memory[2] == 2);

  assert(test->get_dummy_regs_array_dummy_reg(1) == 3);
  assert(memory[3] == 3);

  assert(test->get_dummy_regs_second_array_dummy_reg(1) == 4);
  assert(memory[4] == 4);

  assert(test->get_dummy_regs_array_dummy_reg(2) == 5);
  assert(memory[5] == 5);

  assert(test->get_dummy_regs_second_array_dummy_reg(2) == 6);
  assert(memory[6] == 6);

  assert(test->get_further_regs_dummy_reg(0) == 7);
  assert(memory[7] == 7);
}

void test_bit_indexes()
{
  // Assert bit indexes of plain register
  assert(fpga_regs::Test::plain_dummy_reg_plain_bit_a_shift == 0);
  assert(fpga_regs::Test::plain_dummy_reg_plain_bit_a_mask == 1);
  assert(fpga_regs::Test::plain_dummy_reg_plain_bit_b_shift == 1);
  assert(fpga_regs::Test::plain_dummy_reg_plain_bit_b_mask == 2);
  assert(fpga_regs::Test::plain_dummy_reg_plain_bit_vector_shift == 2);
  assert(fpga_regs::Test::plain_dummy_reg_plain_bit_vector_mask == 15 << 2);

  // Assert bit indexes of array register
  assert(fpga_regs::Test::dummy_regs_array_dummy_reg_array_bit_a_shift == 0);
  assert(fpga_regs::Test::dummy_regs_array_dummy_reg_array_bit_a_mask == 1);
  assert(fpga_regs::Test::dummy_regs_array_dummy_reg_array_bit_b_shift == 1);
  assert(fpga_regs::Test::dummy_regs_array_dummy_reg_array_bit_b_mask == 2);
  assert(fpga_regs::Test::dummy_regs_array_dummy_reg_array_bit_vector_shift == 2);
  assert(fpga_regs::Test::dummy_regs_array_dummy_reg_array_bit_vector_mask == 31 << 2);
}

"""

        main_file = self.working_dir / "main.cpp"
        main = f"""\
#include <assert.h>

#include "include/test.h"

{functions}
int main()
{{
{main_function}
  return 0;
}}
"""
        create_file(main_file, main)
        self.registers.create_cpp_interface(self.include_dir)
        self.registers.create_cpp_header(self.include_dir)
        self.registers.create_cpp_implementation(self.working_dir)
        cpp_class_file = self.working_dir / "test.cpp"

        executable = self.working_dir / "test.o"
        cmd = ["g++", main_file, cpp_class_file, f"-o{executable}", f"-I{self.include_dir}"]
        run_command(cmd)
        run_command([executable])

    def test_cpp_with_registers_and_constants(self):
        self._compile_and_test_cpp(test_registers=True, test_constants=True)

    def test_cpp_with_only_registers(self):
        self.registers.constants = []
        self._compile_and_test_cpp(test_registers=True, test_constants=False)

    def test_cpp_with_only_constants(self):
        self.registers.register_objects = []
        self._compile_and_test_cpp(test_registers=False, test_constants=True)

    def test_setting_cpp_register_array_out_of_bounds_should_crash(self):
        main_file = self.working_dir / "main.cpp"
        main = """\
#include <assert.h>

#include "include/test.h"

int main()
{
  uint32_t data[fpga_regs::Test::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(data);
  fpga_regs::Test test = fpga_regs::Test(base_address);

  // Index 3 is out of bounds (should be less than 3)
  test.set_dummy_regs_array_dummy_reg(3, 1337);

  return 0;
}
"""
        create_file(main_file, main)
        self.registers.create_cpp_interface(self.include_dir)
        self.registers.create_cpp_header(self.include_dir)
        self.registers.create_cpp_implementation(self.working_dir)
        cpp_class_file = self.working_dir / "test.cpp"

        executable = self.working_dir / "test.o"
        cmd = ["g++", main_file, cpp_class_file, f"-o{executable}", f"-I{self.include_dir}"]
        run_command(cmd)

        with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
            stderr = process.communicate()
        assert "Assertion `array_index < dummy_regs_array_length' failed" in str(stderr), stderr
