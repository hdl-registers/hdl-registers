// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl-registers project, an HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://github.com/hdl-registers/hdl-registers
// -------------------------------------------------------------------------------------------------

#include "test_constants.h"

void test_constants(uint32_t *memory, fpga_regs::Caesar *caesar)
{
  assert(fpga_regs::Caesar::data_width == 24);
  assert(fpga_regs::Caesar::decrement == -8);

  assert(fpga_regs::Caesar::enabled);
  assert(!fpga_regs::Caesar::disabled);
  assert(fpga_regs::Caesar::enabled && !fpga_regs::Caesar::disabled);

  assert(fpga_regs::Caesar::rate == 3.5);
  assert(fpga_regs::Caesar::rate != 3.6);

  assert(fpga_regs::Caesar::paragraph == "hello there :)");
  assert(fpga_regs::Caesar::paragraph != "");

  assert(fpga_regs::Caesar::base_address_bin == fpga_regs::Caesar::base_address_hex);
  // This assertions shows that values greater than unsigned 32-bit integer work.
  assert(fpga_regs::Caesar::base_address_bin == 34359738368);
}
