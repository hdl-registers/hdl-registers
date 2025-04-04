// -------------------------------------------------------------------------------------------------
// Copyright (c) Lukas Vik. All rights reserved.
//
// This file is part of the hdl-registers project, an HDL register generator fast enough to run
// in real time.
// https://hdl-registers.com
// https://github.com/hdl-registers/hdl-registers
// -------------------------------------------------------------------------------------------------

#include <iostream>
#include <assert.h>

#include "caesar.h"

void test_registers(uint32_t *memory, fpga_regs::Caesar *caesar);
