-- -------------------------------------------------------------------------------------------------
-- Copyright (c) Lukas Vik. All rights reserved.
--
-- This file is part of the hdl_registers project, a HDL register generator fast enough to run
-- in real time.
-- https://hdl-registers.com
-- https://gitlab.com/hdl_registers/hdl_registers
-- -------------------------------------------------------------------------------------------------
-- Instantiate all these strange register maps and let them elaborate.
-- Basically shows that the code compiles and can run.
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

use work.array_only_up_regs_pkg.all;
use work.array_only_down_regs_pkg.all;
use work.plain_and_array_only_up_regs_pkg.all;
use work.plain_and_array_only_down_regs_pkg.all;
use work.plain_only_up_regs_pkg.all;
use work.plain_only_down_regs_pkg.all;


entity tb_instantiate_strange_register_maps is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_instantiate_strange_register_maps is

  signal clk : std_ulogic := '0';

begin

  clk <= not clk after 5 ns;
  test_runner_watchdog(runner, 1 ms);


  ------------------------------------------------------------------------------
  main : process
  begin
    test_runner_setup(runner, runner_cfg);

    wait for 100 ns;

    test_runner_cleanup(runner);
  end process;


  ------------------------------------------------------------------------------
  array_only_up_block : block
    signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
    signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

    signal regs_up : array_only_up_regs_up_t := array_only_up_regs_up_init;

    signal reg_was_read : array_only_up_reg_was_accessed_t := (others => '0');
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
      generic map (
        bus_handle => regs_bus_master
      )
      port map (
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m
      );


    ------------------------------------------------------------------------------
    array_only_up_reg_file_inst : entity work.array_only_up_reg_file
      port map(
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m,
        --
        regs_up => regs_up,
        --
        reg_was_read => reg_was_read
      );

  end block;


  ------------------------------------------------------------------------------
  array_only_down_block : block
    signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
    signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

    signal regs_down : array_only_down_regs_down_t := array_only_down_regs_down_init;

    signal reg_was_written : array_only_down_reg_was_accessed_t := (others => '0');
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
      generic map (
        bus_handle => regs_bus_master
      )
      port map (
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m
      );


    ------------------------------------------------------------------------------
    array_only_down_reg_file_inst : entity work.array_only_down_reg_file
      port map(
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m,
        --
        regs_down => regs_down,
        --
        reg_was_written => reg_was_written
      );

  end block;


  ------------------------------------------------------------------------------
  plain_and_array_only_up_block : block
    signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
    signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

    signal regs_up : plain_and_array_only_up_regs_up_t := plain_and_array_only_up_regs_up_init;

    signal reg_was_read : plain_and_array_only_up_reg_was_accessed_t := (others => '0');
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
      generic map (
        bus_handle => regs_bus_master
      )
      port map (
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m
      );


    ------------------------------------------------------------------------------
    plain_and_array_only_up_reg_file_inst : entity work.plain_and_array_only_up_reg_file
      port map(
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m,
        --
        regs_up => regs_up,
        --
        reg_was_read => reg_was_read
      );

  end block;


  ------------------------------------------------------------------------------
  plain_and_array_only_down_block : block
    signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
    signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

    signal regs_down : plain_and_array_only_down_regs_down_t :=
      plain_and_array_only_down_regs_down_init;

    signal reg_was_written : plain_and_array_only_down_reg_was_accessed_t := (others => '0');
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
      generic map (
        bus_handle => regs_bus_master
      )
      port map (
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m
      );


    ------------------------------------------------------------------------------
    plain_and_array_only_down_reg_file_inst : entity work.plain_and_array_only_down_reg_file
      port map(
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m,
        --
        regs_down => regs_down,
        --
        reg_was_written => reg_was_written
      );

  end block;


  ------------------------------------------------------------------------------
  plain_only_up_block : block
    signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
    signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

    signal regs_up : plain_only_up_regs_up_t := plain_only_up_regs_up_init;

    signal reg_was_read : plain_only_up_reg_was_accessed_t := (others => '0');
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
      generic map (
        bus_handle => regs_bus_master
      )
      port map (
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m
      );


    ------------------------------------------------------------------------------
    plain_only_up_reg_file_inst : entity work.plain_only_up_reg_file
      port map(
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m,
        --
        regs_up => regs_up,
        --
        reg_was_read => reg_was_read
      );

  end block;


  ------------------------------------------------------------------------------
  plain_only_down_block : block
    signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
    signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

    signal regs_down : plain_only_down_regs_down_t := plain_only_down_regs_down_init;

    signal reg_was_written : plain_only_down_reg_was_accessed_t := (others => '0');
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
      generic map (
        bus_handle => regs_bus_master
      )
      port map (
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m
      );


    ------------------------------------------------------------------------------
    plain_only_down_reg_file_inst : entity work.plain_only_down_reg_file
      port map(
        clk => clk,
        --
        axi_lite_m2s => axi_lite_m2s,
        axi_lite_s2m => axi_lite_s2m,
        --
        regs_down => regs_down,
        --
        reg_was_written => reg_was_written
      );

  end block;

end architecture;
