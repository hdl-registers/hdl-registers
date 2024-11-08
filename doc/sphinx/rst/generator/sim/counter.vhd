-- -------------------------------------------------------------------------------------------------
-- Copyright (c) Lukas Vik. All rights reserved.
--
-- This file is part of the hdl-registers project, an HDL register generator fast enough to run
-- in real time.
-- https://hdl-registers.com
-- https://github.com/hdl-registers/hdl-registers
-- -------------------------------------------------------------------------------------------------
-- Regularly send out a 'pulse', with a frequency that is configurable over the register bus.
-- -------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

library common;
use common.types_pkg.all;


entity counter is
  port (
    clk : in std_ulogic;
    --
    regs_m2s : in axi_lite_m2s_t;
    regs_s2m : out axi_lite_s2m_t := axi_lite_s2m_init;
    --
    clock_enable : in std_ulogic;
    pulse : out std_ulogic := '0'
  );
end entity;

architecture a of counter is

begin


end architecture;
