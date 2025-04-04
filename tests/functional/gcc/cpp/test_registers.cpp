// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl-registers project, an HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://github.com/hdl-registers/hdl-registers
// -------------------------------------------------------------------------------------------------

#include "test_registers.h"

void test_register_attributes()
{
    assert(fpga_regs::caesar::conf::plain_bit_a::width == 1);
    assert(fpga_regs::caesar::conf::plain_bit_a::shift == 0);
    assert(fpga_regs::caesar::conf::plain_bit_a::mask_at_base == 1);
    assert(fpga_regs::caesar::conf::plain_bit_a::mask_shifted == 1);
    assert(fpga_regs::caesar::conf::plain_bit_a::default_value == 0);
    assert(fpga_regs::caesar::conf::plain_bit_a::default_value_raw == 0);

    assert(fpga_regs::caesar::conf::plain_bit_vector::width == 4);
    assert(fpga_regs::caesar::conf::plain_bit_vector::shift == 1);
    assert(fpga_regs::caesar::conf::plain_bit_vector::mask_at_base == 15);
    assert(fpga_regs::caesar::conf::plain_bit_vector::mask_shifted == 30);
    assert(fpga_regs::caesar::conf::plain_bit_vector::default_value == 3);
    assert(fpga_regs::caesar::conf::plain_bit_vector::default_value_raw == 6);

    assert(fpga_regs::caesar::conf::plain_integer::width == 8);
    assert(fpga_regs::caesar::conf::plain_integer::shift == 5);
    assert(fpga_regs::caesar::conf::plain_integer::mask_at_base == 255);
    assert(fpga_regs::caesar::conf::plain_integer::mask_shifted == 8160);
    assert(fpga_regs::caesar::conf::plain_integer::default_value == 66);
    assert(fpga_regs::caesar::conf::plain_integer::default_value_raw == 2112);

    assert(fpga_regs::caesar::conf::plain_enumeration::width == 3);
    assert(fpga_regs::caesar::conf::plain_enumeration::shift == 13);
    assert(fpga_regs::caesar::conf::plain_enumeration::mask_at_base == 7);
    assert(fpga_regs::caesar::conf::plain_enumeration::mask_shifted == 57344);
    assert(fpga_regs::caesar::conf::plain_enumeration::default_value == fpga_regs::caesar::conf::plain_enumeration::Enumeration::third);
    assert(fpga_regs::caesar::conf::plain_enumeration::default_value_raw == 16384);

    assert(fpga_regs::caesar::conf::plain_bit_b::width == 1);
    assert(fpga_regs::caesar::conf::plain_bit_b::shift == 16);
    assert(fpga_regs::caesar::conf::plain_bit_b::mask_at_base == 1);
    assert(fpga_regs::caesar::conf::plain_bit_b::mask_shifted == 65536);
    assert(fpga_regs::caesar::conf::plain_bit_b::default_value == 1);
    assert(fpga_regs::caesar::conf::plain_bit_b::default_value_raw == 65536);

    assert(fpga_regs::caesar::dummies::array_length == 3);
    assert(fpga_regs::caesar::dummies2::array_length == 2);

    // Test some array attributes, to show the namespace hierarchy mostly.
    assert(fpga_regs::caesar::dummies::first::array_bit_vector::width == 5);
    assert(fpga_regs::caesar::dummies::first::array_bit_vector::default_value == 12);
}

bool operator==(const fpga_regs::caesar::conf::Value &lhs, const fpga_regs::caesar::conf::Value &rhs)
{
    return (
        lhs.plain_bit_a == rhs.plain_bit_a &&
        lhs.plain_bit_vector == rhs.plain_bit_vector &&
        lhs.plain_integer == rhs.plain_integer &&
        lhs.plain_enumeration == rhs.plain_enumeration &&
        lhs.plain_bit_b == rhs.plain_bit_b);
}

bool operator==(const fpga_regs::caesar::dummies::first::Value &lhs, const fpga_regs::caesar::dummies::first::Value &rhs)
{
    return (
        lhs.array_integer == rhs.array_integer &&
        lhs.array_bit_a == rhs.array_bit_a &&
        lhs.array_bit_b == rhs.array_bit_b &&
        lhs.array_bit_vector == rhs.array_bit_vector &&
        lhs.array_enumeration == rhs.array_enumeration);
}

void test_read_write_registers(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    caesar->set_conf(fpga_regs::caesar::conf::default_value);

    assert(caesar->get_conf() == fpga_regs::caesar::conf::default_value);
    assert(caesar->get_conf_plain_bit_vector() == fpga_regs::caesar::conf::plain_bit_vector::default_value);
    assert(caesar->get_conf_plain_bit_a() == fpga_regs::caesar::conf::plain_bit_a::default_value);
    assert(caesar->get_conf_plain_integer() == fpga_regs::caesar::conf::plain_integer::default_value);
    assert(caesar->get_conf_plain_enumeration() == fpga_regs::caesar::conf::plain_enumeration::default_value);
    assert(caesar->get_conf_plain_bit_b() == fpga_regs::caesar::conf::plain_bit_b::default_value);

    caesar->set_dummies_first(0, fpga_regs::caesar::dummies::first::default_value);
    assert(caesar->get_dummies_first(0) == fpga_regs::caesar::dummies::first::default_value);
    assert(caesar->get_dummies_first_array_integer(0) == fpga_regs::caesar::dummies::first::array_integer::default_value);
    assert(caesar->get_dummies_first_array_bit_a(0) == fpga_regs::caesar::dummies::first::array_bit_a::default_value);
    assert(caesar->get_dummies_first_array_bit_b(0) == fpga_regs::caesar::dummies::first::array_bit_b::default_value);
    assert(caesar->get_dummies_first_array_bit_vector(0) == fpga_regs::caesar::dummies::first::array_bit_vector::default_value);
    assert(caesar->get_dummies_first_array_enumeration(0) == fpga_regs::caesar::dummies::first::array_enumeration::default_value);
}

void test_field_getters(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    // Assert field getters of plain register
    memory[0] = (0b0 << 16) | (0b100 << 13) | (0b01010011 << 5) | (0b1010 << 1) | (0b1 << 0);
    assert(caesar->get_conf_plain_bit_a() == 1);
    assert(caesar->get_conf_plain_bit_vector() == 10);
    assert(caesar->get_conf_plain_integer() == 83);
    assert(
        caesar->get_conf_plain_enumeration() == fpga_regs::caesar::conf::plain_enumeration::Enumeration::fifth);
    assert(caesar->get_conf_plain_bit_b() == 0);

    memory[0] = ((0b1 << 16) | (0b011 << 13) | (0b11011100 << 5) | (0b1011 << 1) | (0b0 << 0));
    assert(caesar->get_conf_plain_bit_a() == 0);
    assert(caesar->get_conf_plain_bit_vector() == 11);
    assert(caesar->get_conf_plain_integer() == -36);
    assert(
        caesar->get_conf_plain_enumeration() == fpga_regs::caesar::conf::plain_enumeration::Enumeration::fourth);
    assert(caesar->get_conf_plain_bit_b() == 1);

    // Assert field getters of array register
    memory[7] = (0b0 << 14) | (0b11010 << 9) | (0b0 << 8) | (0b1 << 7) | (0b1010011 << 0);
    memory[9] = (0b1 << 14) | (0b01011 << 9) | (0b1 << 8) | (0b0 << 7) | (0b0011100 << 0);

    assert(caesar->get_dummies_first_array_integer(0) == 83);
    assert(caesar->get_dummies_first_array_bit_a(0) == 1);
    assert(caesar->get_dummies_first_array_bit_b(0) == 0);
    assert(caesar->get_dummies_first_array_bit_vector(0) == 26);
    assert(
        caesar->get_dummies_first_array_enumeration(0) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element0);

    assert(caesar->get_dummies_first_array_integer(1) == 28);
    assert(caesar->get_dummies_first_array_bit_a(1) == 0);
    assert(caesar->get_dummies_first_array_bit_b(1) == 1);
    assert(caesar->get_dummies_first_array_bit_vector(1) == 11);
    assert(
        caesar->get_dummies_first_array_enumeration(1) == fpga_regs::caesar::dummies::first::array_enumeration::Enumeration::element1);
}

void test_field_setters(fpga_regs::Caesar *caesar)
{
    // Assert field getters of plain register.
    // We do not check the raw value in memory (since it would be cumbersome).
    // But since the behavior of the getters is verified with raw memory values above,
    // a test setter->getter->verify is sufficient to prove that the setter is correct.

    caesar->set_conf_plain_bit_a(1);
    caesar->set_conf_plain_bit_b(0);
    caesar->set_conf_plain_bit_vector(0b1010);
    caesar->set_conf_plain_enumeration(
        fpga_regs::caesar::conf::plain_enumeration::Enumeration::first);
    caesar->set_conf_plain_integer(77);
    assert(caesar->get_conf_plain_bit_a() == 1);
    assert(caesar->get_conf_plain_bit_b() == 0);
    assert(caesar->get_conf_plain_bit_vector() == 10);
    assert(
        caesar->get_conf_plain_enumeration() == fpga_regs::caesar::conf::plain_enumeration::Enumeration::first);
    assert(caesar->get_conf_plain_integer() == 77);

    caesar->set_conf_plain_bit_a(0);
    caesar->set_conf_plain_bit_b(1);
    caesar->set_conf_plain_bit_vector(0b1011);
    caesar->set_conf_plain_enumeration(
        fpga_regs::caesar::conf::plain_enumeration::Enumeration::fifth);
    caesar->set_conf_plain_integer(-45);
    assert(caesar->get_conf_plain_bit_a() == 0);
    assert(caesar->get_conf_plain_bit_b() == 1);
    assert(caesar->get_conf_plain_bit_vector() == 11);
    assert(
        caesar->get_conf_plain_enumeration() == fpga_regs::caesar::conf::plain_enumeration::Enumeration::fifth);
    assert(caesar->get_conf_plain_integer() == -45);

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
    // All other fields should be default value when writing a field in a "write only" register.

    int reg_index = 4;

    caesar->set_address_a(244);
    assert(memory[reg_index] == 244 + (0b10101010 << 8));

    caesar->set_address_b(213);
    assert(memory[reg_index] == (213 << 8) + 0b11001100);
}

void test_field_setter_on_write_pulse_register(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    // All other fields should be default value when writing a field in a "write pulse" register.
    // Bit 0 = start = default value 1.
    // Bit 1 = abort = default value 0.
    int reg_index = 1;

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
    // All other fields should be default value when writing a field in
    // a "read, write pulse" register.
    int reg_index = 2;

    caesar->set_irq_status_a(1);
    assert((memory[reg_index] & 0b11) == 1);

    caesar->set_irq_status_b(1);
    assert((memory[reg_index] & 0b11) == 3);
}

void test_negative_integer_field_on_top_register_bit(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    // Two bit fields on the lowest two bits, the rest is our integer field.
    memory[3] = 0b11111111111111111111111000000011;

    // Check that the number is interpreted as negative.
    assert(caesar->get_status_c() == -128);
}

void test_registers(uint32_t *memory, fpga_regs::Caesar *caesar)
{
    test_register_attributes();
    test_read_write_registers(memory, caesar);
    test_field_getters(memory, caesar);
    test_field_setters(caesar);
    test_field_setter_on_write_only_register(memory, caesar);
    test_field_setter_on_write_pulse_register(memory, caesar);
    test_field_setter_on_read_write_pulse_register(memory, caesar);
    test_negative_integer_field_on_top_register_bit(memory, caesar);
}
