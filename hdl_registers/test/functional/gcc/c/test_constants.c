// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl_registers project, a HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://gitlab.com/hdl_registers/hdl_registers
// -------------------------------------------------------------------------------------------------

#include "test_constants.h"

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
