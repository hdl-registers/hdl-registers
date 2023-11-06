// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl_registers project, a HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://gitlab.com/hdl_registers/hdl_registers
// -------------------------------------------------------------------------------------------------

#include "test_constants.h"

void test_constants(uint32_t *memory, fpga_regs::Test *test)
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
