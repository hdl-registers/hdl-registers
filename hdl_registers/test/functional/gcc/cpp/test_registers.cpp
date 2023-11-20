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
    assert(fpga_regs::caesar::config::plain_bit_a::width == 1);
    assert(fpga_regs::caesar::config::plain_bit_a::default_value == 0);
    assert(fpga_regs::caesar::config::plain_bit_b::default_value == 1);

    assert(fpga_regs::caesar::config::plain_bit_vector::width == 4);
    assert(fpga_regs::caesar::config::plain_bit_vector::default_value == 3);

    assert(fpga_regs::caesar::dummies::array_length == 3);
    assert(fpga_regs::caesar::dummies::first::array_bit_vector::width == 5);
    assert(fpga_regs::caesar::dummies::first::array_bit_vector::default_value == 12);
}

void test_read_write_registers(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    // Set data and then check, according to the expected register addresses.
    // Data is a ramp 0-6.
    caesar->set_config(0);
    caesar->set_dummies_first(0, 1);
    // second is read only, so set the value in the memory straight away
    memory[8] = 2;
    caesar->set_dummies_first(1, 3);
    memory[10] = 4;
    caesar->set_dummies_first(2, 5);
    memory[12] = 6;
    caesar->set_dummies2_dummy(0, 7);

    assert(caesar->get_config() == 0);
    assert(memory[0] == 0);

    assert(caesar->get_dummies_first(0) == 1);
    assert(memory[7] == 1);

    assert(caesar->get_dummies_second(0) == 2);
    assert(memory[8] == 2);

    assert(caesar->get_dummies_first(1) == 3);
    assert(memory[9] == 3);

    assert(caesar->get_dummies_second(1) == 4);
    assert(memory[10] == 4);

    assert(caesar->get_dummies_first(2) == 5);
    assert(memory[11] == 5);

    assert(caesar->get_dummies_second(2) == 6);
    assert(memory[12] == 6);

    assert(caesar->get_dummies2_dummy(0) == 7);
    assert(memory[13] == 7);
}

void test_field_getters(fpga_regs::Caesar *caesar)
{
    // Assert field getters of plain register
    caesar->set_config(
        (0b01010011 << 9) | (0b100 << 6) | (0b1010 << 2) | (0b0 << 1) | (0b1 << 0));
    assert(caesar->get_config_plain_bit_a() == 1);
    assert(caesar->get_config_plain_bit_b() == 0);
    assert(caesar->get_config_plain_bit_vector() == 10);
    assert(
        caesar->get_config_plain_enumeration() == fpga_regs::caesar::config::plain_enumeration::Enumeration::fifth);
    assert(caesar->get_config_plain_integer() == 83);

    caesar->set_config(
        (0b11011100 << 9) | (0b011 << 6) | (0b1011 << 2) | (0b1 << 1) | (0b0 << 0));
    assert(caesar->get_config_plain_bit_a() == 0);
    assert(caesar->get_config_plain_bit_b() == 1);
    assert(caesar->get_config_plain_bit_vector() == 11);
    assert(
        caesar->get_config_plain_enumeration() == fpga_regs::caesar::config::plain_enumeration::Enumeration::fourth);
    assert(caesar->get_config_plain_integer() == -36);

    // Assert field getters of array register
    caesar->set_dummies_first(
        0, (0b1010011 << 8) | (0b0 << 7) | (0b1010 << 2) | (0b0 << 1) | (0b1 << 0));
    caesar->set_dummies_first(
        1, (0b0011100 << 8) | (0b1 << 7) | (0b1011 << 2) | (0b1 << 1) | (0b0 << 0));

    assert(caesar->get_dummies_first_array_bit_a(0) == 1);
    assert(caesar->get_dummies_first_array_bit_b(0) == 0);
    assert(caesar->get_dummies_first_array_bit_vector(0) == 10);
    assert(
        caesar->get_dummies_first_array_enumeration(0) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element0);
    assert(caesar->get_dummies_first_array_integer(0) == 83);

    assert(caesar->get_dummies_first_array_bit_a(1) == 0);
    assert(caesar->get_dummies_first_array_bit_b(1) == 1);
    assert(caesar->get_dummies_first_array_bit_vector(1) == 11);
    assert(
        caesar->get_dummies_first_array_enumeration(1) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element1);
    assert(caesar->get_dummies_first_array_integer(1) == 28);
}

void test_field_getters_from_value(fpga_regs::Caesar *caesar)
{
    uint32_t register_value = 0;

    // Assert field getters of plain register

    register_value = (0b01010011 << 9) | (0b100 << 6) | (0b1010 << 2) | (0b0 << 1) | (0b1 << 0);
    assert(caesar->get_config_plain_bit_a_from_value(register_value) == 1);
    assert(caesar->get_config_plain_bit_b_from_value(register_value) == 0);
    assert(caesar->get_config_plain_bit_vector_from_value(register_value) == 10);
    assert(
        caesar->get_config_plain_enumeration_from_value(register_value) == fpga_regs::caesar::config::plain_enumeration::Enumeration::fifth);
    assert(caesar->get_config_plain_integer_from_value(register_value) == 83);

    register_value = (0b11011100 << 9) | (0b011 << 6) | (0b1011 << 2) | (0b1 << 1) | (0b0 << 0);
    assert(caesar->get_config_plain_bit_a_from_value(register_value) == 0);
    assert(caesar->get_config_plain_bit_b_from_value(register_value) == 1);
    assert(caesar->get_config_plain_bit_vector_from_value(register_value) == 11);
    assert(
        caesar->get_config_plain_enumeration_from_value(register_value) == fpga_regs::caesar::config::plain_enumeration::Enumeration::fourth);
    assert(caesar->get_config_plain_integer_from_value(register_value) == -36);

    // Assert field getters of array register

    register_value = (0b1010011 << 8) | (0 & 0 << 7) | (0b01010 << 2) | (0b0 << 1) | (0b1 << 0);
    assert(caesar->get_dummies_first_array_bit_a_from_value(register_value) == 1);
    assert(caesar->get_dummies_first_array_bit_b_from_value(register_value) == 0);
    assert(
        caesar->get_dummies_first_array_bit_vector_from_value(register_value) == 10);
    assert(
        caesar->get_dummies_first_array_enumeration_from_value(register_value) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element0);
    assert(caesar->get_dummies_first_array_integer_from_value(register_value) == 83);

    register_value = (0b0011100 << 8) | (0b1 << 7) | (0b11011 << 2) | (0b1 << 1) | (0b0 << 0);
    assert(caesar->get_dummies_first_array_bit_a_from_value(register_value) == 0);
    assert(caesar->get_dummies_first_array_bit_b_from_value(register_value) == 1);
    assert(
        caesar->get_dummies_first_array_bit_vector_from_value(register_value) == 27);
    assert(
        caesar->get_dummies_first_array_enumeration_from_value(register_value) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element1);
    assert(caesar->get_dummies_first_array_integer_from_value(register_value) == 28);
}

void test_field_setters(fpga_regs::Caesar *caesar)
{
    // Assert field getters of plain register

    caesar->set_config_plain_bit_a(1);
    caesar->set_config_plain_bit_b(0);
    caesar->set_config_plain_bit_vector(0b1010);
    caesar->set_config_plain_enumeration(
        fpga_regs::caesar::config::plain_enumeration::Enumeration::first);
    caesar->set_config_plain_integer(77);
    assert(caesar->get_config_plain_bit_a() == 1);
    assert(caesar->get_config_plain_bit_b() == 0);
    assert(caesar->get_config_plain_bit_vector() == 10);
    assert(
        caesar->get_config_plain_enumeration() == fpga_regs::caesar::config::plain_enumeration::Enumeration::first);
    assert(caesar->get_config_plain_integer() == 77);

    caesar->set_config_plain_bit_a(0);
    caesar->set_config_plain_bit_b(1);
    caesar->set_config_plain_bit_vector(0b1011);
    caesar->set_config_plain_enumeration(
        fpga_regs::caesar::config::plain_enumeration::Enumeration::fifth);
    caesar->set_config_plain_integer(-45);
    assert(caesar->get_config_plain_bit_a() == 0);
    assert(caesar->get_config_plain_bit_b() == 1);
    assert(caesar->get_config_plain_bit_vector() == 11);
    assert(
        caesar->get_config_plain_enumeration() == fpga_regs::caesar::config::plain_enumeration::Enumeration::fifth);
    assert(caesar->get_config_plain_integer() == -45);

    // Assert field setters of array register

    caesar->set_dummies_first_array_bit_a(0, 1);
    caesar->set_dummies_first_array_bit_b(0, 0);
    caesar->set_dummies_first_array_bit_vector(0, 0b1010);
    caesar->set_dummies_first_array_enumeration(
        0, fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element0);
    caesar->set_dummies_first_array_integer(0, 58);
    assert(caesar->get_dummies_first_array_bit_a(0) == 1);
    assert(caesar->get_dummies_first_array_bit_b(0) == 0);
    assert(caesar->get_dummies_first_array_bit_vector(0) == 10);
    assert(
        caesar->get_dummies_first_array_enumeration(0) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element0);
    assert(caesar->get_dummies_first_array_integer(0) == 58);

    caesar->set_dummies_first_array_bit_a(1, 0);
    caesar->set_dummies_first_array_bit_b(1, 1);
    caesar->set_dummies_first_array_bit_vector(1, 0b1011);
    caesar->set_dummies_first_array_enumeration(
        1, fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element1);
    caesar->set_dummies_first_array_integer(1, 80);
    assert(caesar->get_dummies_first_array_bit_a(1) == 0);
    assert(caesar->get_dummies_first_array_bit_b(1) == 1);
    assert(caesar->get_dummies_first_array_bit_vector(1) == 11);
    assert(
        caesar->get_dummies_first_array_enumeration(1) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element1);
    assert(caesar->get_dummies_first_array_integer(1) == 80);

    // Index 0 should not have been affected
    assert(caesar->get_dummies_first_array_bit_a(0) == 1);
    assert(caesar->get_dummies_first_array_bit_b(0) == 0);
    assert(caesar->get_dummies_first_array_bit_vector(0) == 10);
    assert(
        caesar->get_dummies_first_array_enumeration(0) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element0);
    assert(caesar->get_dummies_first_array_integer(0) == 58);
}

void test_field_setter_on_write_only_register(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    int reg_index = 4;

    caesar->set_address(1337);
    assert(memory[reg_index] == 1337);

    // All other fields should be default value when writing a field in a "write only" register.

    caesar->set_address_a(244);
    assert(memory[reg_index] == 244 + (0b10101010 << 8));

    caesar->set_address_b(213);
    assert(memory[reg_index] == (213 << 8) + 0b11001100);
}

void test_field_setter_on_write_pulse_register(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    int reg_index = 1;

    caesar->set_command(1337);
    assert(memory[reg_index] == 1337);

    // All other fields should be default value when writing a field in a "write pulse" register.
    // Bit 0 = start = default value 1.
    // Bit 1 = abort = default value 0.

    caesar->set_command_start(0);
    assert(memory[reg_index] == 0);

    caesar->set_command_start(1);
    assert(memory[reg_index] == 1);

    caesar->set_command_abort(1);
    assert(memory[reg_index] == 3);

    caesar->set_command_abort(0);
    assert(memory[reg_index] == 1);
}

void test_field_setter_on_read_write_pulse_register(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    int reg_index = 2;

    caesar->set_irq_status(1337);
    assert(memory[reg_index] == 1337);

    // All other fields should be default value when writing a field in
    // a "read, write pulse" register.

    caesar->set_irq_status_a(1);
    assert((memory[reg_index] & 0b11) == 1);

    caesar->set_irq_status_b(1);
    assert((memory[reg_index] & 0b11) == 3);
}

void test_negative_integer_field_on_top_register_bit(fpga_regs::Caesar *caesar)
{
    // Two bit fields on the lowest two bits, the rest is our integer field.
    auto value = caesar->get_status_c_from_value(0b11111111111111111111111000000011);
    // Check that the number is interpreted as negative.
    assert(value == -128);
}

void test_registers(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    test_register_attributes();
    test_read_write_registers(memory, caesar);
    test_field_getters(caesar);
    test_field_getters_from_value(caesar);
    test_field_setters(caesar);
    test_field_setter_on_write_only_register(memory, caesar);
    test_field_setter_on_write_pulse_register(memory, caesar);
    test_field_setter_on_read_write_pulse_register(memory, caesar);
    test_negative_integer_field_on_top_register_bit(caesar);
}
