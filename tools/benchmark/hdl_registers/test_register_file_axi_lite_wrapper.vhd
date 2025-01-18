-- -------------------------------------------------------------------------------------------------
-- Copyright (c) Lukas Vik. All rights reserved.
--
-- This file is part of the hdl-registers project, an HDL register generator fast enough to run
-- in real time.
-- https://hdl-registers.com
-- https://github.com/hdl-registers/hdl-registers
-- -------------------------------------------------------------------------------------------------
-- Wrapper for the generated register file.
-- Does not assign the reg_was_read and reg_was_written signals, to make the comparison
-- with other tools more fair.
-- -------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

use work.test_register_record_pkg.all;


entity test_register_file_axi_lite_wrapper is
  port (
    clk : in std_ulogic;
    --# {}
    --# Register control bus.
    axi_lite_m2s : in axi_lite_m2s_t;
    axi_lite_s2m : out axi_lite_s2m_t := axi_lite_s2m_init;
    --# {}
    -- Register values.
    regs_down : out test_regs_down_t := test_regs_down_init
  );
end entity;

architecture a of test_register_file_axi_lite_wrapper is

begin

  ------------------------------------------------------------------------------
  test_register_file_axi_lite_inst : entity work.test_register_file_axi_lite
    port map(
      clk => clk,
      --
      axi_lite_m2s => axi_lite_m2s,
      axi_lite_s2m => axi_lite_s2m,
      --
      regs_down => regs_down,
      --
      reg_was_read => open,
      reg_was_written => open
    );

end architecture;
