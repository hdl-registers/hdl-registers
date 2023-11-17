-- -------------------------------------------------------------------------------------------------
-- Copyright (c) Lukas Vik. All rights reserved.
--
-- This file is part of the hdl_registers project, a HDL register generator fast enough to run
-- in real time.
-- https://hdl-registers.com
-- https://gitlab.com/hdl_registers/hdl_registers
-- -------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library vunit_lib;
context vunit_lib.vc_context;
context vunit_lib.vunit_context;

library axi;
use axi.axi_lite_pkg.all;

library bfm;

library reg_file;
use reg_file.reg_operations_pkg.all;

use work.counter_regs_pkg.all;
use work.counter_register_record_pkg.all;
use work.counter_register_simulation_pkg.all;


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
    variable command : counter_command_t := counter_command_init;
    variable status : counter_status_t := counter_status_init;
  begin
    test_runner_setup(runner, runner_cfg);

    -- Check initial state.
    read_counter_status(net=>net, value=>status);
    check_equal(status.enabled, '0');
    check_equal(status.pulse_count, 0);

    if run("test_count_clock_cycles") then
      config.mode := mode_clock_cycles;
      config.increment := 13;

    elsif run("test_count_clock_cycles_with_enable") then
      config.mode := mode_clock_cycles_with_enable;
      config.increment := 8;

      clock_enable <= '1';
    end if;

    -- Set configuration, which depends on test case.
    write_counter_config(net=>net, value=>config);

    -- Enable the operation.
    command.start := '1';
    write_counter_command(net=>net, value=>command);

    -- Check updated status.
    read_counter_status(net=>net, value=>status);
    check_equal(status.enabled, '1');
    check_equal(status.pulse_count, 0);

    -- Wait until a number of pulses have passed.
    status.enabled := '1';
    status.pulse_count := 10;
    wait_until_counter_status_equals(net=>net, value=>status);

    test_runner_cleanup(runner);
  end process;


  ------------------------------------------------------------------------------
  axi_lite_master_inst : entity bfm.axi_lite_master
    generic map (
      bus_handle => regs_bus_master
    )
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
