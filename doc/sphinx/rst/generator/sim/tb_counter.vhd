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

use work.receiver_register_record_pkg.all;
use work.receiver_register_check_pkg.all;
use work.receiver_register_read_write_pkg.all;
use work.receiver_register_wait_until_pkg.all;
use work.receiver_regs_pkg.all;


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
  begin
    test_runner_setup(runner, runner_cfg);


    -- Check register value as an integer.
    check_receiver_interrupt_status_equal(net=>net, expected=>0);

    -- Check native value of each field.
    check_receiver_status_equal(
      net=>net,
      expected=>(
        enabled=>'1',
        calibration_offset=>-18,
        tdata=>"0111",
        state=>state_idle
      )
    );


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
