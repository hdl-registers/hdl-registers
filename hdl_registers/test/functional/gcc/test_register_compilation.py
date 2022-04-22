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

from hdl_registers.parser import from_toml

import tsfpga
from tsfpga.system_utils import create_file, run_command


@pytest.mark.usefixtures("fixture_tmp_path")
class TestRegisterCompilation(unittest.TestCase):
    """
    Functional test: TOML -> registers -> Code generation -> compilation -> set/check/assert
    """

    tmp_path = None

    def setUp(self):
        self.working_dir = self.tmp_path
        self.include_dir = self.working_dir / "include"

        toml_file = tsfpga.TSFPGA_EXAMPLE_MODULES / "artyz7" / "regs_artyz7.toml"
        self.registers = from_toml("artyz7", toml_file)

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
  assert(ARTYZ7_DATA_WIDTH == 24);
  assert(ARTYZ7_DECREMENT == -8);
}
"""

        if not test_registers:
            # If no registers, the constant shall be zero
            main_function += "  assert(ARTYZ7_NUM_REGS == 0);\n"
        else:
            main_function += """\
  assert(ARTYZ7_NUM_REGS == 8);
  test_addresses();
  test_bit_indexes();
  test_generated_type();
"""

            functions += """
void test_addresses()
{
  // Assert that indexes are correct
  assert(ARTYZ7_PLAIN_DUMMY_REG_INDEX == 0);
  assert(ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(0) == 1);
  assert(ARTYZ7_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(0) == 2);
  assert(ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(1) == 3);
  assert(ARTYZ7_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(1) == 4);
  assert(ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(2) == 5);
  assert(ARTYZ7_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(2) == 6);

  // Assert that addresses are correct
  assert(ARTYZ7_PLAIN_DUMMY_REG_ADDR == 0);
  assert(ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(0) == 4);
  assert(ARTYZ7_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(0) == 8);
  assert(ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(1) == 12);
  assert(ARTYZ7_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(1) == 16);
  assert(ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(2) == 20);
  assert(ARTYZ7_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(2) == 24);
  assert(ARTYZ7_FURTHER_REGS_DUMMY_REG_ADDR(0) == 28);
  // Last register
  assert(ARTYZ7_FURTHER_REGS_DUMMY_REG_ADDR(0) == 4 * (ARTYZ7_NUM_REGS - 1));
}

void test_bit_indexes()
{
  // Assert bit indexes of plain register
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_A_SHIFT == 0);
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_A_MASK == 1);

  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_B_SHIFT == 1);
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_B_MASK == 2);

  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_SHIFT == 2);
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_MASK == 15 << 2);

  // Assert bit indexes of array register
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_A_SHIFT == 0);
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_A_MASK == 1);

  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_B_SHIFT == 1);
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_B_MASK == 2);

  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_SHIFT == 2);
  assert(ARTYZ7_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_MASK == 15 << 2);
}

void test_generated_type()
{
  // Assert positions within the generated type
  artyz7_regs_t regs;
  assert(sizeof(regs) == 4 * ARTYZ7_NUM_REGS);

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
  regs.dummy_regs[0].array_dummy_reg = ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK;
  regs.dummy_regs[2].second_array_dummy_reg =
    (1 << ARTYZ7_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_SHIFT);
}
"""

        main_file = self.working_dir / "main.c"
        main = f"""\
#include <assert.h>
#include <stdint.h>
#include "artyz7_regs.h"

{functions}

int main()
{{
{main_function}

  return 0;
}}
"""
        create_file(main_file, main)
        self.registers.create_c_header(self.include_dir)

        executable = self.working_dir / "artyz7.o"
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
  assert(fpga_regs::Artyz7::data_width == 24);
  assert(fpga_regs::Artyz7::decrement == -8);
}

"""

        if not test_registers:
            # If no registers, the constant shall be zero
            main_function += "  assert(fpga_regs::Artyz7::num_registers == 0);\n"
        else:
            main_function += """\
  assert(fpga_regs::Artyz7::num_registers == 8);
  assert(fpga_regs::Artyz7::dummy_regs_array_length == 3);

  // Allocate memory and instantiate the register class
  uint32_t memory[fpga_regs::Artyz7::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(memory);
  fpga_regs::Artyz7 artyz7 = fpga_regs::Artyz7(base_address);

  test_read_write_registers(&artyz7, memory);
  test_bit_indexes();
"""

            functions += """\
void test_read_write_registers(fpga_regs::Artyz7 *artyz7, uint32_t *memory)
{
  // Set data and then check, according to the expected register addresses.
  // Data is a ramp 0-6.
  artyz7->set_plain_dummy_reg(0);
  artyz7->set_dummy_regs_array_dummy_reg(0, 1);
  // second_array_dummy_reg is read only, so set the value in the memory straight away
  memory[2] = 2;
  artyz7->set_dummy_regs_array_dummy_reg(1, 3);
  memory[4] = 4;
  artyz7->set_dummy_regs_array_dummy_reg(2, 5);
  memory[6] = 6;
  artyz7->set_further_regs_dummy_reg(0, 7);

  assert(artyz7->get_plain_dummy_reg() == 0);
  assert(memory[0] == 0);

  assert(artyz7->get_dummy_regs_array_dummy_reg(0) == 1);
  assert(memory[1] == 1);

  assert(artyz7->get_dummy_regs_second_array_dummy_reg(0) == 2);
  assert(memory[2] == 2);

  assert(artyz7->get_dummy_regs_array_dummy_reg(1) == 3);
  assert(memory[3] == 3);

  assert(artyz7->get_dummy_regs_second_array_dummy_reg(1) == 4);
  assert(memory[4] == 4);

  assert(artyz7->get_dummy_regs_array_dummy_reg(2) == 5);
  assert(memory[5] == 5);

  assert(artyz7->get_dummy_regs_second_array_dummy_reg(2) == 6);
  assert(memory[6] == 6);

  assert(artyz7->get_further_regs_dummy_reg(0) == 7);
  assert(memory[7] == 7);
}

void test_bit_indexes()
{
  // Assert bit indexes of plain register
  assert(fpga_regs::Artyz7::plain_dummy_reg_plain_bit_a_shift == 0);
  assert(fpga_regs::Artyz7::plain_dummy_reg_plain_bit_a_mask == 1);
  assert(fpga_regs::Artyz7::plain_dummy_reg_plain_bit_b_shift == 1);
  assert(fpga_regs::Artyz7::plain_dummy_reg_plain_bit_b_mask == 2);
  assert(fpga_regs::Artyz7::plain_dummy_reg_plain_bit_vector_shift == 2);
  assert(fpga_regs::Artyz7::plain_dummy_reg_plain_bit_vector_mask == 15 << 2);

  // Assert bit indexes of array register
  assert(fpga_regs::Artyz7::dummy_regs_array_dummy_reg_array_bit_a_shift == 0);
  assert(fpga_regs::Artyz7::dummy_regs_array_dummy_reg_array_bit_a_mask == 1);
  assert(fpga_regs::Artyz7::dummy_regs_array_dummy_reg_array_bit_b_shift == 1);
  assert(fpga_regs::Artyz7::dummy_regs_array_dummy_reg_array_bit_b_mask == 2);
  assert(fpga_regs::Artyz7::dummy_regs_array_dummy_reg_array_bit_vector_shift == 2);
  assert(fpga_regs::Artyz7::dummy_regs_array_dummy_reg_array_bit_vector_mask == 31 << 2);
}

"""

        main_file = self.working_dir / "main.cpp"
        main = f"""\
#include <assert.h>

#include "include/artyz7.h"

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
        cpp_class_file = self.working_dir / "artyz7.cpp"

        executable = self.working_dir / "artyz7.o"
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

#include "include/artyz7.h"

int main()
{
  uint32_t data[fpga_regs::Artyz7::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(data);
  fpga_regs::Artyz7 artyz7 = fpga_regs::Artyz7(base_address);

  // Index 3 is out of bounds (should be less than 3)
  artyz7.set_dummy_regs_array_dummy_reg(3, 1337);

  return 0;
}
"""
        create_file(main_file, main)
        self.registers.create_cpp_interface(self.include_dir)
        self.registers.create_cpp_header(self.include_dir)
        self.registers.create_cpp_implementation(self.working_dir)
        cpp_class_file = self.working_dir / "artyz7.cpp"

        executable = self.working_dir / "artyz7.o"
        cmd = ["g++", main_file, cpp_class_file, f"-o{executable}", f"-I{self.include_dir}"]
        run_command(cmd)

        with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
            stderr = process.communicate()
        assert "Assertion `array_index < dummy_regs_array_length' failed" in str(stderr), stderr
