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

use work.counter_regs_pkg.all;
use work.counter_register_record_pkg.all;


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

  signal regs_up : counter_regs_up_t := counter_regs_up_init;
  signal regs_down : counter_regs_down_t := counter_regs_down_init;

  signal reg_was_written : counter_reg_was_written_t := counter_reg_was_written_init;

begin

  ------------------------------------------------------------------------------
  counter_register_file_axi_lite_inst : entity work.counter_register_file_axi_lite
    port map (
      clk => clk,
      --
      axi_lite_m2s => regs_m2s,
      axi_lite_s2m => regs_s2m,
      --
      regs_up => regs_up,
      regs_down => regs_down,
      --
      reg_was_read => open,
      reg_was_written => reg_was_written
    );


  ------------------------------------------------------------------------------
  set_status : process
  begin
    wait until rising_edge(clk);

    if regs_down.command.start then
      regs_up.status.enabled <= '1';
    end if;

    if regs_down.command.stop then
      regs_up.status.enabled <= '0';
    end if;

    if reg_was_written.config then
      -- Clear value when configuration is changed.
      regs_up.status.pulse_count <= 0;
    else
      regs_up.status.pulse_count <= regs_up.status.pulse_count + to_int(pulse);
    end if;
  end process;


  ------------------------------------------------------------------------------
  count_block : block
    constant counter_width : positive := 10;
    constant counter_activate_value : positive := 2 ** counter_width - 1;
    -- One bit extra to avoid overflow.
    constant counter_max_value : positive := 2 ** (counter_width + 1) - 1;

    signal count : natural range 0 to counter_max_value := 0;

    signal clock_enable_p1 : std_ulogic := '0';
  begin

    ------------------------------------------------------------------------------
    count_events : process
    begin
      wait until rising_edge(clk);

      pulse <= '0';

      case regs_down.config.condition is
        when condition_clock_cycles =>
          count <= count + regs_down.config.increment;

        when condition_clock_cycles_with_enable =>
          if clock_enable then
            count <= count + regs_down.config.increment;
          end if;

        when condition_enable_edges =>
          if clock_enable /= clock_enable_p1 then
            count <= count + regs_down.config.increment;
          end if;
      end case;

      if count >= counter_activate_value then
        count <= 0;
        pulse <= regs_up.status.enabled;
      end if;

      clock_enable_p1 <= clock_enable;
    end process;

  end block;

end architecture;
