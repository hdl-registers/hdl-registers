// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl_registers project, a HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://gitlab.com/hdl_registers/hdl_registers
// -------------------------------------------------------------------------------------------------

#include <assert.h>

#include "caesar.h"

void test_registers(uint32_t *memory, fpga_regs::Caesar *caesar);
