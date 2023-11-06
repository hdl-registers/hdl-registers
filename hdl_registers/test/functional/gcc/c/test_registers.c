// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl_registers project, a HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://gitlab.com/hdl_registers/hdl_registers
// -------------------------------------------------------------------------------------------------

#include "test_registers.h"

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
        TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_A_MASK_INVERSE == 0b11111111111111111111111111111110);

    assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_SHIFT == 1);
    assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_MASK == 2);
    assert(
        TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_B_MASK_INVERSE == 0b11111111111111111111111111111101);

    assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_SHIFT == 2);
    assert(TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK == 31 << 2);
    assert(
        TEST_DUMMY_REGS_ARRAY_DUMMY_REG_ARRAY_BIT_VECTOR_MASK_INVERSE == 0b11111111111111111111111110000011);
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

void test_registers()
{
    test_addresses();
    test_generated_type();
    test_field_indexes();
    test_enumeration_fields();
}
