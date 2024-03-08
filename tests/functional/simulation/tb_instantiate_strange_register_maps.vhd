-- -------------------------------------------------------------------------------------------------
-- Copyright (c) Lukas Vik. All rights reserved.
--
-- This file is part of the hdl-registers project, an HDL register generator fast enough to run
-- in real time.
-- https://hdl-registers.com
-- https://github.com/hdl-registers/hdl-registers
-- -------------------------------------------------------------------------------------------------
-- Instantiate all these strange register maps and let them elaborate.
-- Basically shows that the code compiles and can run.
-- -------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library vunit_lib;
use vunit_lib.run_pkg.all;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

library bfm;

library reg_file;

use work.array_only_up_regs_pkg.all;
use work.array_only_up_register_record_pkg.all;
use work.array_only_up_register_read_write_pkg.all;
use work.array_only_up_register_wait_until_pkg.all;

use work.array_only_down_regs_pkg.all;
use work.array_only_down_register_record_pkg.all;
use work.array_only_down_register_read_write_pkg.all;
use work.array_only_down_register_wait_until_pkg.all;

use work.plain_and_array_only_up_regs_pkg.all;
use work.plain_and_array_only_up_register_record_pkg.all;
use work.plain_and_array_only_up_register_read_write_pkg.all;
use work.plain_and_array_only_up_register_wait_until_pkg.all;

use work.plain_and_array_only_down_regs_pkg.all;
use work.plain_and_array_only_down_register_record_pkg.all;
use work.plain_and_array_only_down_register_read_write_pkg.all;
use work.plain_and_array_only_down_register_wait_until_pkg.all;

use work.plain_only_up_regs_pkg.all;
use work.plain_only_up_register_record_pkg.all;
use work.plain_only_up_register_read_write_pkg.all;
use work.plain_only_up_register_wait_until_pkg.all;

use work.plain_only_down_regs_pkg.all;
use work.plain_only_down_register_record_pkg.all;
use work.plain_only_down_register_read_write_pkg.all;
use work.plain_only_down_register_wait_until_pkg.all;

use work.only_constants_regs_pkg.all;

use work.empty_regs_pkg.all;


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

    signal reg_was_read : array_only_up_reg_was_read_t := array_only_up_reg_was_read_init;
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
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

    signal reg_was_written : array_only_down_reg_was_written_t := (
      array_only_down_reg_was_written_init
    );
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
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

    signal reg_was_read : plain_and_array_only_up_reg_was_read_t := (
      plain_and_array_only_up_reg_was_read_init
    );
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
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

    signal reg_was_written : plain_and_array_only_down_reg_was_written_t := (
      plain_and_array_only_down_reg_was_written_init
    );
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
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

    signal reg_was_read : plain_only_up_reg_was_read_t := plain_only_up_reg_was_read_init;
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
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

    signal reg_was_written : plain_only_down_reg_was_written_t := (
      plain_only_down_reg_was_written_init
    );
  begin

    ------------------------------------------------------------------------------
    axi_lite_master_inst : entity bfm.axi_lite_master
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
