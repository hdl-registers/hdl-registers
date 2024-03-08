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
use reg_file.reg_file_pkg.all;
use reg_file.reg_operations_pkg.write_reg;

use work.caesar_regs_pkg.all;
use work.caesar_register_record_pkg.all;
use work.caesar_register_read_write_pkg.all;
use work.caesar_register_wait_until_pkg.all;
use work.caesar_simulation_test_pkg.all;


entity tb_wait_until_equals is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_wait_until_equals is

  constant clk_period : time := 10 ns;
  signal clk : std_ulogic := '0';

  signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
  signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

  signal regs_up : caesar_regs_up_t := caesar_regs_up_init;
  signal regs_down : caesar_regs_down_t := caesar_regs_down_init;

  constant write_register_timeout : time := 500 * clk_period;
  signal start_write_plain_register, start_write_array_register : boolean := false;

begin

  clk <= not clk after clk_period / 2;
  test_runner_watchdog(runner, 1 ms);


  ------------------------------------------------------------------------------
  main : process
    variable reg : reg_t := (others => '0');
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_wait_until_plain_register_equals") then
      start_write_plain_register <= true;
      wait until rising_edge(clk);
      start_write_plain_register <= true;

      wait_until_caesar_config_equals(
        net=>net,
        value=>caesar_config_non_init,
        timeout=>write_register_timeout + 10 * clk_period
      );

      -- Check that it took roughly the time we expect it to.
      assert now > write_register_timeout;
      assert now < write_register_timeout + 10 * clk_period;

    elsif run("test_wait_until_plain_register_equals_timeout") then
      -- vunit: .expected_failure
      -- We never set the register, so it will never assume this value.
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      wait_until_caesar_config_equals(
        net=>net, value=>caesar_config_non_init, timeout=>100 * clk_period
      );

    elsif run("test_wait_until_array_register_equals") then
      start_write_array_register <= true;
      wait until rising_edge(clk);
      start_write_array_register <= true;

      wait_until_caesar_dummies_first_equals(
        net=>net,
        array_index => 1,
        value=>caesar_dummies_first_non_init,
        timeout=>write_register_timeout + 10 * clk_period
      );

      -- Check that it took roughly the time we expect it to.
      assert now > write_register_timeout;
      assert now < write_register_timeout + 10 * clk_period;

    elsif run("test_wait_until_array_register_equals_timeout") then
      -- vunit: .expected_failure
      -- We never set the register, so it will never assume this value.
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      wait_until_caesar_dummies_first_equals(
        net=>net,
        array_index => 1,
        value=>caesar_dummies_first_non_init,
        timeout=>100 * clk_period,
        message=>"Extra printout that can be set!"
      );

    elsif run("test_wait_until_reg_equals_works_even_when_there_is_junk_in_unused_bits") then
      -- The fields of the register currently occupy bits 14:0.
      -- Write junk to some other bits of the register.
      reg := to_slv(caesar_config_non_init);
      reg(31 downto 20) := "101010101010";
      write_reg(net=>net, reg_index=>caesar_config, value=>reg);

      wait_until_caesar_config_equals(net=>net, value=>caesar_config_non_init);

    elsif run("test_using_wildcard_in_slv_register_value_is_possible") then
      -- Use "don't care" as a wildcard. The wait should end after the very first write.
      wait_until_caesar_current_timestamp_equals(net=>net, value=>(others => '-'));

    elsif run("wait_until_plain_field_equals") then
      start_write_plain_register <= true;
      wait until rising_edge(clk);
      start_write_plain_register <= true;

      wait_until_caesar_config_plain_enumeration_equals(
        net=>net,
        value=>caesar_config_non_init.plain_enumeration,
        timeout=>write_register_timeout + 10 * clk_period
      );

      -- Check that it took roughly the time we expect it to.
      assert now > write_register_timeout;
      assert now < write_register_timeout + 10 * clk_period;

    elsif run("test_wait_until_plain_field_equals_timeout") then
      -- vunit: .expected_failure
      -- We never set the register, so it will never assume this value.
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      wait_until_caesar_config_plain_integer_equals(
        net=>net, value=>caesar_config_non_init.plain_integer, timeout=>100 * clk_period
      );

    elsif run("test_wait_until_plain_field_equals_timeout_with_message") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      wait_until_caesar_config_plain_integer_equals(
        net=>net,
        value=>caesar_config_non_init.plain_integer,
        timeout=>100 * clk_period,
        message=>"Extra printout that can be set!"
      );

    elsif run("test_wait_until_array_field_equals") then
      start_write_array_register <= true;
      wait until rising_edge(clk);
      start_write_array_register <= true;

      wait_until_caesar_dummies_first_array_integer_equals(
        net=>net,
        array_index => 1,
        value=>caesar_dummies_first_non_init.array_integer,
        timeout=>write_register_timeout + 10 * clk_period
      );

      -- Check that it took roughly the time we expect it to.
      assert now > write_register_timeout;
      assert now < write_register_timeout + 10 * clk_period;

    elsif run("test_wait_until_array_field_equals_timeout") then
      -- vunit: .expected_failure
      -- We never set the register, so it will never assume this value.
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      wait_until_caesar_dummies_first_array_integer_equals(
        net=>net,
        array_index => 1,
        value=>caesar_dummies_first_non_init.array_integer,
        timeout=>100 * clk_period,
        message=>"Extra printout that can be set!"
      );

    elsif run("test_wait_until_array_field_equals_timeout_with_base_address") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      wait_until_caesar_dummies_first_array_integer_equals(
        net=>net,
        array_index => 1,
        value=>caesar_dummies_first_non_init.array_integer,
        timeout=>100 * clk_period,
        base_address=>x"00050000",
        message=>"Extra printout that can be set!"
      );

    end if;

    test_runner_cleanup(runner);
  end process;


  ------------------------------------------------------------------------------
  write_plain_register_after_timeout : process
  begin
    wait until start_write_plain_register and rising_edge(clk);

    wait for write_register_timeout;

    write_caesar_config(net=>net, value=>caesar_config_non_init);
  end process;


  ------------------------------------------------------------------------------
  write_array_register_after_timeout : process
  begin
    wait until start_write_array_register and rising_edge(clk);

    -- Write the two array indexes that are not affected straight away.
    write_caesar_dummies_first(net=>net, array_index=>0, value=>caesar_dummies_first_non_init);
    write_caesar_dummies_first(net=>net, array_index=>2, value=>caesar_dummies_first_non_init);

    wait for write_register_timeout;

    write_caesar_dummies_first(net=>net, array_index=>1, value=>caesar_dummies_first_non_init);
  end process;


  ------------------------------------------------------------------------------
  axi_lite_master_inst : entity bfm.axi_lite_master
    port map (
      clk => clk,
      --
      axi_lite_m2s => axi_lite_m2s,
      axi_lite_s2m => axi_lite_s2m
    );


  ------------------------------------------------------------------------------
  caesar_reg_file_inst : entity work.caesar_reg_file
    port map(
      clk => clk,
      --
      axi_lite_m2s => axi_lite_m2s,
      axi_lite_s2m => axi_lite_s2m,
      --
      regs_up => regs_up,
      regs_down => regs_down
    );

end architecture;
