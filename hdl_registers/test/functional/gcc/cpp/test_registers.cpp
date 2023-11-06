// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl_registers project, a HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://gitlab.com/hdl_registers/hdl_registers
// -------------------------------------------------------------------------------------------------

#include "test_registers.h"

void test_register_attributes()
{
    assert(fpga_regs::test::plain_dummy_reg::plain_bit_a::width == 1);
    assert(fpga_regs::test::plain_dummy_reg::plain_bit_a::default_value == 0);
    assert(fpga_regs::test::plain_dummy_reg::plain_bit_b::default_value == 1);

    assert(fpga_regs::test::plain_dummy_reg::plain_bit_vector::width == 4);
    assert(fpga_regs::test::plain_dummy_reg::plain_bit_vector::default_value == 3);

    assert(fpga_regs::Test::dummy_regs_array_length == 3);
    assert(fpga_regs::test::dummy_regs::array_dummy_reg::array_bit_vector::width == 5);
    assert(fpga_regs::test::dummy_regs::array_dummy_reg::array_bit_vector::default_value == 12);
}

void test_read_write_registers(uint32_t *memory, fpga_regs::Test *test)
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
        (0b01010011 << 9) | (0b100 << 6) | (0b1010 << 2) | (0b0 << 1) | (0b1 << 0));
    assert(test->get_plain_dummy_reg_plain_bit_a() == 1);
    assert(test->get_plain_dummy_reg_plain_bit_b() == 0);
    assert(test->get_plain_dummy_reg_plain_bit_vector() == 10);
    assert(
        test->get_plain_dummy_reg_plain_enumeration() == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth);
    assert(test->get_plain_dummy_reg_plain_integer() == 83);

    test->set_plain_dummy_reg(
        (0b11011100 << 9) | (0b011 << 6) | (0b1011 << 2) | (0b1 << 1) | (0b0 << 0));
    assert(test->get_plain_dummy_reg_plain_bit_a() == 0);
    assert(test->get_plain_dummy_reg_plain_bit_b() == 1);
    assert(test->get_plain_dummy_reg_plain_bit_vector() == 11);
    assert(
        test->get_plain_dummy_reg_plain_enumeration() == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fourth);
    assert(test->get_plain_dummy_reg_plain_integer() == -36);

    // Assert field getters of array register
    test->set_dummy_regs_array_dummy_reg(
        0, (0b1010011 << 8) | (0b0 << 7) | (0b1010 << 2) | (0b0 << 1) | (0b1 << 0));
    test->set_dummy_regs_array_dummy_reg(
        1, (0b0011100 << 8) | (0b1 << 7) | (0b1011 << 2) | (0b1 << 1) | (0b0 << 0));

    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(0) == 1);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(0) == 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(0) == 10);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration(0) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer(0) == 83);

    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(1) == 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(1) == 1);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(1) == 11);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration(1) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer(1) == 28);
}

void test_field_getters_from_value(fpga_regs::Test *test)
{
    uint32_t register_value = 0;

    // Assert field getters of plain register

    register_value = (0b01010011 << 9) | (0b100 << 6) | (0b1010 << 2) | (0b0 << 1) | (0b1 << 0);
    assert(test->get_plain_dummy_reg_plain_bit_a_from_value(register_value) == 1);
    assert(test->get_plain_dummy_reg_plain_bit_b_from_value(register_value) == 0);
    assert(test->get_plain_dummy_reg_plain_bit_vector_from_value(register_value) == 10);
    assert(
        test->get_plain_dummy_reg_plain_enumeration_from_value(register_value) == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth);
    assert(test->get_plain_dummy_reg_plain_integer_from_value(register_value) == 83);

    register_value = (0b11011100 << 9) | (0b011 << 6) | (0b1011 << 2) | (0b1 << 1) | (0b0 << 0);
    assert(test->get_plain_dummy_reg_plain_bit_a_from_value(register_value) == 0);
    assert(test->get_plain_dummy_reg_plain_bit_b_from_value(register_value) == 1);
    assert(test->get_plain_dummy_reg_plain_bit_vector_from_value(register_value) == 11);
    assert(
        test->get_plain_dummy_reg_plain_enumeration_from_value(register_value) == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fourth);
    assert(test->get_plain_dummy_reg_plain_integer_from_value(register_value) == -36);

    // Assert field getters of array register

    register_value = (0b1010011 << 8) | (0 & 0 << 7) | (0b01010 << 2) | (0b0 << 1) | (0b1 << 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a_from_value(register_value) == 1);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b_from_value(register_value) == 0);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_bit_vector_from_value(register_value) == 10);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration_from_value(register_value) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer_from_value(register_value) == 83);

    register_value = (0b0011100 << 8) | (0b1 << 7) | (0b11011 << 2) | (0b1 << 1) | (0b0 << 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a_from_value(register_value) == 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b_from_value(register_value) == 1);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_bit_vector_from_value(register_value) == 27);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration_from_value(register_value) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer_from_value(register_value) == 28);
}

void test_field_setters(fpga_regs::Test *test)
{
    // Assert field getters of plain register

    test->set_plain_dummy_reg_plain_bit_a(1);
    test->set_plain_dummy_reg_plain_bit_b(0);
    test->set_plain_dummy_reg_plain_bit_vector(0b1010);
    test->set_plain_dummy_reg_plain_enumeration(
        fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::first);
    test->set_plain_dummy_reg_plain_integer(77);
    assert(test->get_plain_dummy_reg_plain_bit_a() == 1);
    assert(test->get_plain_dummy_reg_plain_bit_b() == 0);
    assert(test->get_plain_dummy_reg_plain_bit_vector() == 10);
    assert(
        test->get_plain_dummy_reg_plain_enumeration() == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::first);
    assert(test->get_plain_dummy_reg_plain_integer() == 77);

    test->set_plain_dummy_reg_plain_bit_a(0);
    test->set_plain_dummy_reg_plain_bit_b(1);
    test->set_plain_dummy_reg_plain_bit_vector(0b1011);
    test->set_plain_dummy_reg_plain_enumeration(
        fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth);
    test->set_plain_dummy_reg_plain_integer(-45);
    assert(test->get_plain_dummy_reg_plain_bit_a() == 0);
    assert(test->get_plain_dummy_reg_plain_bit_b() == 1);
    assert(test->get_plain_dummy_reg_plain_bit_vector() == 11);
    assert(
        test->get_plain_dummy_reg_plain_enumeration() == fpga_regs::test::plain_dummy_reg::plain_enumeration::Enumeration::fifth);
    assert(test->get_plain_dummy_reg_plain_integer() == -45);

    // Assert field setters of array register

    test->set_dummy_regs_array_dummy_reg_array_bit_a(0, 1);
    test->set_dummy_regs_array_dummy_reg_array_bit_b(0, 0);
    test->set_dummy_regs_array_dummy_reg_array_bit_vector(0, 0b1010);
    test->set_dummy_regs_array_dummy_reg_array_enumeration(
        0, fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0);
    test->set_dummy_regs_array_dummy_reg_array_integer(0, 58);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(0) == 1);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(0) == 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(0) == 10);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration(0) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer(0) == 58);

    test->set_dummy_regs_array_dummy_reg_array_bit_a(1, 0);
    test->set_dummy_regs_array_dummy_reg_array_bit_b(1, 1);
    test->set_dummy_regs_array_dummy_reg_array_bit_vector(1, 0b1011);
    test->set_dummy_regs_array_dummy_reg_array_enumeration(
        1, fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1);
    test->set_dummy_regs_array_dummy_reg_array_integer(1, 80);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(1) == 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(1) == 1);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(1) == 11);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration(1) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element1);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer(1) == 80);

    // Index 0 should not have been affected
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_a(0) == 1);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_b(0) == 0);
    assert(test->get_dummy_regs_array_dummy_reg_array_bit_vector(0) == 10);
    assert(
        test->get_dummy_regs_array_dummy_reg_array_enumeration(0) == fpga_regs::test::dummy_regs::array_dummy_reg::array_enumeration::Enumeration::element0);
    assert(test->get_dummy_regs_array_dummy_reg_array_integer(0) == 58);
}

void test_field_setter_on_write_only_register(uint32_t *memory, fpga_regs::Test *test)
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

void test_field_setter_on_write_pulse_register(uint32_t *memory, fpga_regs::Test *test)
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

void test_field_setter_on_read_write_pulse_register(uint32_t *memory, fpga_regs::Test *test)
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

void test_registers(uint32_t *memory, fpga_regs::Test *test)
{
    test_register_attributes();
    test_read_write_registers(memory, test);
    test_field_getters(test);
    test_field_getters_from_value(test);
    test_field_setters(test);
    test_field_setter_on_write_only_register(memory, test);
    test_field_setter_on_write_pulse_register(memory, test);
    test_field_setter_on_read_write_pulse_register(memory, test);
}
