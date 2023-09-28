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
import unittest

# Third party libraries
import pytest
from tsfpga.system_utils import create_file, run_command

# First party libraries
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

  assert(TEST_ENABLED);
  assert(!TEST_DISABLED);
  assert(TEST_ENABLED && !TEST_DISABLED);

  assert(TEST_RATE == 3.5);
  assert(TEST_RATE != 3.6);

  assert(TEST_PARAGRAPH == "hello there :)");
  assert(TEST_PARAGRAPH != "-");

  assert(TEST_BASE_ADDRESS_BIN == TEST_BASE_ADDRESS_HEX);
  assert(TEST_BASE_ADDRESS_BIN == 34359738368);
}
"""

        if not test_registers:
            # If no registers, the constant shall be zero
            main_function += "  assert(TEST_NUM_REGS == 0);\n"
        else:
            main_function += """\
  assert(TEST_NUM_REGS == 12);
  test_addresses();
  test_generated_type();
  test_field_indexes();
  test_enumeration_fields();
"""

            functions += """
void test_addresses()
{
  // Assert that indexes are correct
  assert(TEST_PLAIN_DUMMY_REG_INDEX == 0);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(0) == 5);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(0) == 6);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(1) == 7);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(1) == 8);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_INDEX(2) == 9);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_INDEX(2) == 10);

  // Assert that addresses are correct
  assert(TEST_PLAIN_DUMMY_REG_ADDR == 0);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(0) == 20);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(0) == 24);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(1) == 28);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(1) == 32);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ADDR(2) == 36);
  assert(TEST_DUMMY_REGS_SECOND_ARRAY_DUMMY_REG_ADDR(2) == 40);
  assert(TEST_FURTHER_REGS_DUMMY_REG_ADDR(0) == 44);
  // Last register
  assert(TEST_FURTHER_REGS_DUMMY_REG_ADDR(0) == 4 * (TEST_NUM_REGS - 1));
}

void test_generated_type()
{
  // Assert positions within the generated type
  test_regs_t regs;
  assert(sizeof(regs) == 4 * TEST_NUM_REGS);

  assert((void *)&regs == (void *)&regs.plain_dummy_reg);
  assert((void *)&regs + 20 == (void *)&regs.dummy_regs[0].array_dummy_reg);
  assert((void *)&regs + 24 == (void *)&regs.dummy_regs[0].second_array_dummy_reg);
  assert((void *)&regs + 28 == (void *)&regs.dummy_regs[1].array_dummy_reg);
  assert((void *)&regs + 32 == (void *)&regs.dummy_regs[1].second_array_dummy_reg);
  assert((void *)&regs + 36 == (void *)&regs.dummy_regs[2].array_dummy_reg);
  assert((void *)&regs + 40 == (void *)&regs.dummy_regs[2].second_array_dummy_reg);
  assert((void *)&regs + 44 == (void *)&regs.further_regs[0].dummy_reg);

  // Some dummy code that uses the generated type
  regs.plain_dummy_reg = 0;
  regs.dummy_regs[0].array_dummy_reg = TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK;
  regs.dummy_regs[2].second_array_dummy_reg =
    (1 << TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_SHIFT);
}

void test_field_indexes()
{
  // Assert field indexes of plain register
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_SHIFT == 0);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_MASK == 1);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_A_MASK_INVERSE == 0b11111111111111111111111111111110);

  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_SHIFT == 1);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_MASK == 2);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_B_MASK_INVERSE == 0b11111111111111111111111111111101);

  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_SHIFT == 2);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_MASK == 15 << 2);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_BIT_VECTOR_MASK_INVERSE == 0b11111111111111111111111111000011);

  // Assert field indexes of array register
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_A_SHIFT == 0);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_A_MASK == 1);
  assert(
    TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_A_MASK_INVERSE == 0b11111111111111111111111111111110
  );

  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_SHIFT == 1);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_MASK == 2);
  assert(
    TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_MASK_INVERSE == 0b11111111111111111111111111111101
  );

  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_SHIFT == 2);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK == 31 << 2);
  assert(
    TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK_INVERSE
    == 0b11111111111111111111111110000011
  );
}

void test_enumeration_fields()
{
  // Assert elements of enumeration fields.
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_ENUMERATION_FIRST == 0);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_ENUMERATION_SECOND == 1);
  assert(TEST_PLAIN_DUMMY_REG_PLAIN_ENUMERATION_FIFTH == 4);

  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_ENUMERATION_ELEMENT0 == 0);
  assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_ENUMERATION_ELEMENT1 == 1);
}
"""

        main_file = self.working_dir / "main.c"
        main = f"""\
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
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

  assert(fpga_regs::Test::enabled);
  assert(!fpga_regs::Test::disabled);
  assert(fpga_regs::Test::enabled && !fpga_regs::Test::disabled);

  assert(fpga_regs::Test::rate == 3.5);
  assert(fpga_regs::Test::rate != 3.6);

  assert(fpga_regs::Test::paragraph == "hello there :)");
  assert(fpga_regs::Test::paragraph != "");

  assert(fpga_regs::Test::base_address_bin == fpga_regs::Test::base_address_hex);
  // This assertions shows that values greater than unsigned 32-bit integer work.
  assert(fpga_regs::Test::base_address_bin == 34359738368);
}

"""

        num_registers = 12 * test_registers
        main_function += f"  assert(fpga_regs::Test::num_registers == {num_registers});\n"

        if test_registers:
            main_function += """\
  assert(fpga_regs::Test::num_registers == 12);
  assert(fpga_regs::Test::dummy_regs_array_length == 3);

  // Allocate memory and instantiate the register class
  uint32_t memory[fpga_regs::Test::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(memory);
  fpga_regs::Test test = fpga_regs::Test(base_address);

  test_read_write_registers(&test, memory);
  test_field_getters(&test);
  test_field_getters_from_value(&test);
  test_field_setters(&test);
  test_field_setter_on_write_only_register(&test, memory);
  test_field_setter_on_write_pulse_register(&test, memory);
  test_field_setter_on_read_write_pulse_register(&test, memory);
"""

            functions += """\
void test_read_write_registers(fpga_regs::Test *test, uint32_t *memory)
{
  // Set data and then check, according to the expected register addresses.
  // Data is a ramp 0-6.
  test->set_plain_dummy_reg(0);
  test->set_dummy_regs_array_dummy_reg(0, 1);
  // second_array_dummy_reg is read only, so set the value in the memory straight away
  memory[6] = 2;
  test->set_dummy_regs_array_dummy_reg(1, 3);
  memory[8] = 4;
  test->set_dummy_regs_array_dummy_reg(2, 5);
  memory[10] = 6;
  test->set_further_regs_dummy_reg(0, 7);

  assert(test->get_plain_dummy_reg() == 0);
  assert(memory[0] == 0);

  assert(test->get_dummy_regs_array_dummy_reg(0) == 1);
  assert(memory[5] == 1);

  assert(test->get_dummy_regs_second_array_dummy_reg(0) == 2);
  assert(memory[6] == 2);

  assert(test->get_dummy_regs_array_dummy_reg(1) == 3);
  assert(memory[7] == 3);

  assert(test->get_dummy_regs_second_array_dummy_reg(1) == 4);
  assert(memory[8] == 4);

  assert(test->get_dummy_regs_array_dummy_reg(2) == 5);
  assert(memory[9] == 5);

  assert(test->get_dummy_regs_second_array_dummy_reg(2) == 6);
  assert(memory[10] == 6);

  assert(test->get_further_regs_dummy_reg(0) == 7);
  assert(memory[11] == 7);
}

void test_field_getters(fpga_regs::Test *test)
{
  // Assert field getters of plain register
  test->set_plain_dummy_reg(
    (0b1010011 << 9) | (0b100 << 6) | (0b1010 << 2) | (0b0  << 1) | (0b1 << 0)
  );
  assert(test->get_plain_dummy_reg_plain_bit_a() == 1);
  assert(test->get_plain_dummy_reg_plain_bit_b() == 0);
  assert(test->get_plain_dummy_reg_plain_bit_vector() == 10);
  assert(
    test->get_plain_dummy_reg_plain_enumeration()
    == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth
  );
  assert(test->get_plain_dummy_reg_plain_integer() == 83);

  test->set_plain_dummy_reg(
    (0b0011100 << 9) | (0b011 << 6) | (0b1011 << 2) | (0b1  << 1) | (0b0 << 0)
  );
  assert(test->get_plain_dummy_reg_plain_bit_a() == 0);
  assert(test->get_plain_dummy_reg_plain_bit_b() == 1);
  assert(test->get_plain_dummy_reg_plain_bit_vector() == 11);
  assert(
    test->get_plain_dummy_reg_plain_enumeration()
    == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fourth
  );
  assert(test->get_plain_dummy_reg_plain_integer() == 28);

  // Assert field getters of array register
  test->set_dummy_regs_array_dummy_reg(
    0, (0b1010011 << 8) | (0b0 << 7) | (0b1010 << 2) | (0b0  << 1) | (0b1 << 0)
  );
  test->set_dummy_regs_array_dummy_reg(
    1, (0b0011100 << 8) | (0b1 << 7) | (0b1011 << 2) | (0b1  << 1) | (0b0 << 0)
  );

  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(0) == 1);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(0) == 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(0) == 10);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration(0)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer(0) == 83);

  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(1) == 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(1) == 1);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(1) == 11);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration(1)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer(1) == 28);
}

void test_field_getters_from_value(fpga_regs::Test *test)
{
  uint32_t register_value = 0;

  // Assert field getters of plain register

  register_value = (0b1010011 << 9) | (0b100 << 6) | (0b1010 << 2) | (0b0  << 1) | (0b1 << 0);
  assert(test->get_plain_dummy_reg_plain_bit_a_from_value(register_value) == 1);
  assert(test->get_plain_dummy_reg_plain_bit_b_from_value(register_value) == 0);
  assert(test->get_plain_dummy_reg_plain_bit_vector_from_value(register_value) == 10);
  assert(
    test->get_plain_dummy_reg_plain_enumeration_from_value(register_value)
    == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth
  );
  assert(test->get_plain_dummy_reg_plain_integer_from_value(register_value) == 83);

  register_value = (0b0011100 << 9) | (0b011 << 6)| (0b1011 << 2) | (0b1  << 1) | (0b0 << 0);
  assert(test->get_plain_dummy_reg_plain_bit_a_from_value(register_value) == 0);
  assert(test->get_plain_dummy_reg_plain_bit_b_from_value(register_value) == 1);
  assert(test->get_plain_dummy_reg_plain_bit_vector_from_value(register_value) == 11);
  assert(
    test->get_plain_dummy_reg_plain_enumeration_from_value(register_value)
    == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fourth
  );
  assert(test->get_plain_dummy_reg_plain_integer_from_value(register_value) == 28);


  // Assert field getters of array register

  register_value = (0b1010011 << 8) | (0&0 << 7) | (0b01010 << 2) | (0b0  << 1) | (0b1 << 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a_from_value(register_value) == 1);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b_from_value(register_value) == 0);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_bit_vector_from_value(register_value) == 10
  );
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration_from_value(register_value)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer_from_value(register_value) == 83);

  register_value = (0b0011100 << 8) | (0b1 << 7) | (0b11011 << 2) | (0b1  << 1) | (0b0 << 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a_from_value(register_value) == 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b_from_value(register_value) == 1);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_bit_vector_from_value(register_value) == 27
  );
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration_from_value(register_value)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer_from_value(register_value) == 28);
}

void test_field_setters(fpga_regs::Test *test)
{
  // Assert field getters of plain register

  test->set_plain_dummy_reg_plain_bit_a(1);
  test->set_plain_dummy_reg_plain_bit_b(0);
  test->set_plain_dummy_reg_plain_bit_vector(0b1010);
  test->set_plain_dummy_reg_plain_enumeration(
    fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::first
  );
  test->set_plain_dummy_reg_plain_integer(77);
  assert(test->get_plain_dummy_reg_plain_bit_a() == 1);
  assert(test->get_plain_dummy_reg_plain_bit_b() == 0);
  assert(test->get_plain_dummy_reg_plain_bit_vector() == 10);
  assert(
    test->get_plain_dummy_reg_plain_enumeration()
    == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::first
  );
  assert(test->get_plain_dummy_reg_plain_integer() == 77);

  test->set_plain_dummy_reg_plain_bit_a(0);
  test->set_plain_dummy_reg_plain_bit_b(1);
  test->set_plain_dummy_reg_plain_bit_vector(0b1011);
  test->set_plain_dummy_reg_plain_enumeration(
    fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth
  );
  test->set_plain_dummy_reg_plain_integer(99);
  assert(test->get_plain_dummy_reg_plain_bit_a() == 0);
  assert(test->get_plain_dummy_reg_plain_bit_b() == 1);
  assert(test->get_plain_dummy_reg_plain_bit_vector() == 11);
  assert(
    test->get_plain_dummy_reg_plain_enumeration()
    == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth
  );
  assert(test->get_plain_dummy_reg_plain_integer() == 99);

  // Assert field setters of array register

  test->set_dummy_regs_array_dummy_reg_array_bit_a(0, 1);
  test->set_dummy_regs_array_dummy_reg_array_bit_b(0, 0);
  test->set_dummy_regs_array_dummy_reg_array_bit_vector(0, 0b1010);
  test->set_dummy_regs_array_dummy_reg_array_enumeration(
    0, fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0
  );
  test->set_dummy_regs_array_dummy_reg_array_integer(0, 58);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(0) == 1);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(0) == 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(0) == 10);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration(0)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer(0) == 58);

  test->set_dummy_regs_array_dummy_reg_array_bit_a(1, 0);
  test->set_dummy_regs_array_dummy_reg_array_bit_b(1, 1);
  test->set_dummy_regs_array_dummy_reg_array_bit_vector(1, 0b1011);
  test->set_dummy_regs_array_dummy_reg_array_enumeration(
    1, fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1
  );
  test->set_dummy_regs_array_dummy_reg_array_integer(1, 80);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(1) == 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(1) == 1);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(1) == 11);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration(1)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer(1) == 80);

  // Index 0 should not have been affected
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(0) == 1);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(0) == 0);
  assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(0) == 10);
  assert(
    test->get_dummy_regs_array_dummy_reg_array_enumeration(0)
    == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0
  );
  assert(test->get_dummy_regs_array_dummy_reg_array_integer(0) == 58);
}

void test_field_setter_on_write_pulse_register(fpga_regs::Test *test, uint32_t *memory)
{
  int reg_index = 2;

  test->set_command(1337);
  assert(memory[reg_index] == 1337);

  // All other bits should be zero when writing a field in a "write pulse" register

  test->set_command_a(1);
  assert(memory[reg_index] == 1);

  test->set_command_b(1);
  assert(memory[reg_index] == 1 << 1);
}

void test_field_setter_on_read_write_pulse_register(fpga_regs::Test *test, uint32_t *memory)
{
  int reg_index = 3;

  test->set_irq_status(1337);
  assert(memory[reg_index] == 1337);

  // All other bits should be zero when writing a field in a "read, write pulse" register

  test->set_irq_status_a(1);
  assert(memory[reg_index] == 1);

  test->set_irq_status_b(1);
  assert(memory[reg_index] == 1 << 1);
}

void test_field_setter_on_write_only_register(fpga_regs::Test *test, uint32_t *memory)
{
  int reg_index = 4;

  test->set_address(1337);
  assert(memory[reg_index] == 1337);

  // All other bits should be zero when writing a field in a "write only" register

  test->set_address_a(244);
  assert(memory[reg_index] == 244);

  test->set_address_b(213);
  assert(memory[reg_index] == 213 << 8);
}

"""

        # Test also the register attributes.
        # Keep this test code separate for the sake of readability.
        if test_registers:
            main_function += "  test_register_attributes();\n"

            functions += """\
void test_register_attributes()
{
  assert(fpga_regs::test::plain_dummy_reg::plain_bit_a::width == 1);
  assert(fpga_regs::test::plain_dummy_reg::plain_bit_a::default_value == 0);
  assert(fpga_regs::test::plain_dummy_reg::plain_bit_b::default_value == 1);

  assert(fpga_regs::test::plain_dummy_reg::plain_bit_vector::width == 4);
  assert(fpga_regs::test::plain_dummy_reg::plain_bit_vector::default_value == 3);

  assert(fpga_regs::test::dummy_regs::array_dummy_reg::array_bit_vector::width == 5);
  assert(fpga_regs::test::dummy_regs::array_dummy_reg::array_bit_vector::default_value == 12);
}

"""

        main_file = self.working_dir / "main.cpp"
        main = f"""\
#include <assert.h>
#include <iostream>

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

    def _test_basic(self, test_code: str):
        main_file = self.working_dir / "main.cpp"
        main = f"""\
#include <assert.h>

#include "include/test.h"

int main()
{{
  uint32_t data[fpga_regs::Test::num_registers];
  volatile uint8_t *base_address = reinterpret_cast<volatile uint8_t *>(data);
  fpga_regs::Test test = fpga_regs::Test(base_address);

{test_code}

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

        return executable

    def test_setting_cpp_register_array_out_of_bounds_should_crash(self):
        test_code = """\
  // Index 3 is out of bounds (should be less than 3)
  test.set_dummy_regs_array_dummy_reg(3, 1337);
"""
        executable = self._test_basic(test_code=test_code)

        with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
            stderr = process.communicate()
        assert "Assertion `array_index < dummy_regs_array_length' failed" in str(stderr), stderr

    def test_setting_cpp_integer_field_out_of_range_should_crash(self):
        test_code = """\
  test.set_plain_dummy_reg_plain_integer(20);
"""
        executable = self._test_basic(test_code=test_code)

        with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
            stderr = process.communicate()
        assert "Assertion `field_value >= 50' failed." in str(stderr), stderr

        test_code = """\
  test.set_plain_dummy_reg_plain_integer(110);
"""
        executable = self._test_basic(test_code=test_code)

        with subprocess.Popen([executable], stderr=subprocess.PIPE) as process:
            stderr = process.communicate()
        assert "Assertion `field_value <= 100' failed." in str(stderr), stderr
