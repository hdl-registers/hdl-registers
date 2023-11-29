// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl-registers project, an HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://github.com/hdl-registers/hdl-registers
// -------------------------------------------------------------------------------------------------

#include "test_registers.h"

void test_addresses()
{
    // Assert that indexes are correct
    assert(CAESAR_CONFIG_INDEX == 0);
    assert(CAESAR_DUMMIES_FIRST_INDEX(0) == 7);
    assert(CAESAR_DUMMIES_SECOND_INDEX(0) == 8);
    assert(CAESAR_DUMMIES_FIRST_INDEX(1) == 9);
    assert(CAESAR_DUMMIES_SECOND_INDEX(1) == 10);
    assert(CAESAR_DUMMIES_FIRST_INDEX(2) == 11);
    assert(CAESAR_DUMMIES_SECOND_INDEX(2) == 12);

    // Assert that addresses are correct
    assert(CAESAR_CONFIG_ADDR == 0);
    assert(CAESAR_DUMMIES_FIRST_ADDR(0) == 28);
    assert(CAESAR_DUMMIES_SECOND_ADDR(0) == 32);
    assert(CAESAR_DUMMIES_FIRST_ADDR(1) == 36);
    assert(CAESAR_DUMMIES_SECOND_ADDR(1) == 40);
    assert(CAESAR_DUMMIES_FIRST_ADDR(2) == 44);
    assert(CAESAR_DUMMIES_SECOND_ADDR(2) == 48);
    assert(CAESAR_DUMMIES2_DUMMY_ADDR(0) == 52);
    // Last register
    assert(CAESAR_DUMMIES4_FLABBY_ADDR(1) == 4 * (CAESAR_NUM_REGS - 1));
}

void test_generated_type()
{
    // Assert positions within the generated type
    caesar_regs_t regs;
    assert(sizeof(regs) == 4 * CAESAR_NUM_REGS);

    assert((void *)&regs == (void *)&regs.config);
    assert((void *)&regs + 28 == (void *)&regs.dummies[0].first);
    assert((void *)&regs + 32 == (void *)&regs.dummies[0].second);
    assert((void *)&regs + 36 == (void *)&regs.dummies[1].first);
    assert((void *)&regs + 40 == (void *)&regs.dummies[1].second);
    assert((void *)&regs + 44 == (void *)&regs.dummies[2].first);
    assert((void *)&regs + 48 == (void *)&regs.dummies[2].second);
    assert((void *)&regs + 52 == (void *)&regs.dummies2[0].dummy);

    // Some dummy code that uses the generated type
    regs.config = 0;
    regs.dummies[0].first = CAESAR_DUMMIES_FIRST_ARRAY_BIT_VECTOR_MASK;
    regs.dummies[2].second =
        (1 << CAESAR_DUMMIES_FIRST_ARRAY_BIT_B_SHIFT);
}

void test_field_indexes()
{
    // Assert field indexes of plain register
    assert(CAESAR_CONFIG_PLAIN_BIT_A_SHIFT == 0);
    assert(CAESAR_CONFIG_PLAIN_BIT_A_MASK == 1);
    assert(CAESAR_CONFIG_PLAIN_BIT_A_MASK_INVERSE == 0b11111111111111111111111111111110);

    assert(CAESAR_CONFIG_PLAIN_BIT_B_SHIFT == 1);
    assert(CAESAR_CONFIG_PLAIN_BIT_B_MASK == 2);
    assert(CAESAR_CONFIG_PLAIN_BIT_B_MASK_INVERSE == 0b11111111111111111111111111111101);

    assert(CAESAR_CONFIG_PLAIN_BIT_VECTOR_SHIFT == 2);
    assert(CAESAR_CONFIG_PLAIN_BIT_VECTOR_MASK == 15 << 2);
    assert(CAESAR_CONFIG_PLAIN_BIT_VECTOR_MASK_INVERSE == 0b11111111111111111111111111000011);

    // Assert field indexes of array register
    assert(CAESAR_DUMMIES_FIRST_ARRAY_BIT_A_SHIFT == 0);
    assert(CAESAR_DUMMIES_FIRST_ARRAY_BIT_A_MASK == 1);
    assert(
        CAESAR_DUMMIES_FIRST_ARRAY_BIT_A_MASK_INVERSE == 0b11111111111111111111111111111110);

    assert(CAESAR_DUMMIES_FIRST_ARRAY_BIT_B_SHIFT == 1);
    assert(CAESAR_DUMMIES_FIRST_ARRAY_BIT_B_MASK == 2);
    assert(
        CAESAR_DUMMIES_FIRST_ARRAY_BIT_B_MASK_INVERSE == 0b11111111111111111111111111111101);

    assert(CAESAR_DUMMIES_FIRST_ARRAY_BIT_VECTOR_SHIFT == 2);
    assert(CAESAR_DUMMIES_FIRST_ARRAY_BIT_VECTOR_MASK == 31 << 2);
    assert(
        CAESAR_DUMMIES_FIRST_ARRAY_BIT_VECTOR_MASK_INVERSE == 0b11111111111111111111111110000011);
}

void test_enumeration_fields()
{
    // Assert elements of enumeration fields.
    assert(CAESAR_CONFIG_PLAIN_ENUMERATION_FIRST == 0);
    assert(CAESAR_CONFIG_PLAIN_ENUMERATION_SECOND == 1);
    assert(CAESAR_CONFIG_PLAIN_ENUMERATION_FIFTH == 4);

    assert(CAESAR_DUMMIES_FIRST_ARRAY_ENUMERATION_ELEMENT0 == 0);
    assert(CAESAR_DUMMIES_FIRST_ARRAY_ENUMERATION_ELEMENT1 == 1);
}

void test_registers()
{
    test_addresses();
    test_generated_type();
    test_field_indexes();
    test_enumeration_fields();
}
