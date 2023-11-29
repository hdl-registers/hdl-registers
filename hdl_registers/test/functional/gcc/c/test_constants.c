// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl-registers project, an HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://github.com/hdl-registers/hdl-registers
// -------------------------------------------------------------------------------------------------

#include "test_constants.h"

void test_constants()
{
  assert(CAESAR_DATA_WIDTH == 24);
  assert(CAESAR_DECREMENT == -8);

  assert(CAESAR_ENABLED);
  assert(!CAESAR_DISABLED);
  assert(CAESAR_ENABLED && !CAESAR_DISABLED);

  assert(CAESAR_RATE == 3.5);
  assert(CAESAR_RATE != 3.6);

  assert(CAESAR_PARAGRAPH == "hello there :)");
  assert(CAESAR_PARAGRAPH != "-");

  assert(CAESAR_BASE_ADDRESS_BIN == CAESAR_BASE_ADDRESS_HEX);
  assert(CAESAR_BASE_ADDRESS_BIN == 34359738368);
}
