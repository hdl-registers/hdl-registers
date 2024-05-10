-- -------------------------------------------------------------------------------------------------
-- Copyright (c) Lukas Vik. All rights reserved.
--
-- This file is part of the hdl-registers project, an HDL register generator fast enough to run
-- in real time.
-- https://hdl-registers.com
-- https://github.com/hdl-registers/hdl-registers
-- -------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library vunit_lib;
use vunit_lib.com_pkg.net;
use vunit_lib.run_pkg.all;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

library bfm;

library reg_file;

use work.counter_register_record_pkg.all;
use work.counter_register_check_pkg.all;
use work.counter_register_read_write_pkg.all;
use work.counter_register_wait_until_pkg.all;
use work.counter_regs_pkg.all;


entity tb_counter is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_counter is

  signal clk : std_ulogic := '0';

  signal regs_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
  signal regs_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

  signal pulse, clock_enable : std_ulogic := '0';

begin

  clk <= not clk after 5 ns;
  test_runner_watchdog(runner, 1 ms);


  ------------------------------------------------------------------------------
  main : process
    variable config : counter_config_t := counter_config_init;
  begin
    test_runner_setup(runner, runner_cfg);

    -- Check initial state.
    check_counter_status_enabled_equal(net=>net, expected=>'0');
    check_counter_status_pulse_count_equal(net=>net, expected=>0);

    if run("test_count_clock_cycles") then
      config.condition := condition_clock_cycles;
      config.increment := 13;

    elsif run("test_count_clock_cycles_with_enable") then
      config.condition := condition_clock_cycles_with_enable;
      config.increment := 8;

      clock_enable <= '1';
    end if;

    -- Set configuration, which depends on test case.
    write_counter_config(net=>net, value=>config);

    -- Enable the operation.
    write_counter_command_start(net=>net, value=>'1');

    -- Check updated status.
    check_counter_status_enabled_equal(net=>net, expected=>'1');
    check_counter_status_pulse_count_equal(net=>net, expected=>0);

    -- Wait until a number of pulses have passed.
    wait_until_counter_status_pulse_count_equals(net=>net, value=>10);

    -- Stop the operation.
    write_counter_command_stop(net=>net, value=>'1');

    -- Make sure that status is updated.
    check_counter_status_enabled_equal(net=>net, expected=>'0');

    test_runner_cleanup(runner);
  end process;


  ------------------------------------------------------------------------------
  axi_lite_master_inst : entity bfm.axi_lite_master
    port map (
      clk => clk,
      --
      axi_lite_m2s => regs_m2s,
      axi_lite_s2m => regs_s2m
    );


  ------------------------------------------------------------------------------
  counter_inst : entity work.counter
    port map (
      clk => clk,
      --
      regs_m2s => regs_m2s,
      regs_s2m => regs_s2m,
      --
      clock_enable => clock_enable,
      pulse => pulse
    );

end architecture;
