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
use ieee.numeric_std.all;

library vunit_lib;
context vunit_lib.vc_context;
context vunit_lib.vunit_context;

library axi;
use axi.axi_lite_pkg.all;

library bfm;

library common;
use common.types_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;
use reg_file.reg_operations_pkg.all;

use work.caesar_regs_pkg.all;
use work.caesar_register_record_pkg.all;
use work.caesar_register_read_write_pkg.all;


entity tb_read_write_as_integer is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_read_write_as_integer is

  constant clk_period : time := 10 ns;
  signal clk : std_ulogic := '0';

  signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
  signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

  signal regs_up : caesar_regs_up_t := caesar_regs_up_init;
  signal regs_down : caesar_regs_down_t := caesar_regs_down_init;

begin

  clk <= not clk after clk_period / 2;
  test_runner_watchdog(runner, 1 ms);


  ------------------------------------------------------------------------------
  main : process
    procedure wait_for_write is
    begin
      wait_until_idle(net, as_sync(regs_bus_master));
    end procedure;

    variable reg, reg2 : reg_t := (others => '0');
    variable int : integer := 0;
    variable s0 : caesar_field_test_s0_t := caesar_field_test_s0_init;
    variable u0 : caesar_field_test_u0_t := caesar_field_test_u0_init;
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_writing_register_without_fields_as_integer") then
      -- Use a plain register.
      check_equal(regs_down.tuser, 0);

      -- Write and check an SLV first.
      reg := "10101010101010101010101010101010";
      write_caesar_tuser(net=>net, value=>reg);
      wait_for_write;
      check_equal(regs_down.tuser, reg);

      -- Then an integer.
      reg := "01010101010101010101010101010101";
      write_caesar_tuser(net=>net, value=>to_integer(unsigned(reg)));
      wait_for_write;
      check_equal(regs_down.tuser, reg);

    elsif run("test_reading_register_without_fields_as_integer") then
      -- Use a register in an array.
      read_caesar_dummies3_status(net=>net, array_index=>0, value=>reg);
      read_caesar_dummies3_status(net=>net, array_index=>0, value=>int);

      -- Default values.
      check_equal(reg, 0);
      check_equal(int, 0);

      reg2 := "01010101010101010101010101010101";
      regs_up.dummies3(0).status <= reg2;

      read_caesar_dummies3_status(net=>net, array_index=>0, value=>reg);
      read_caesar_dummies3_status(net=>net, array_index=>0, value=>int);

      check_equal(reg, reg2);
      check_equal(int, to_integer(unsigned(reg2)));

    elsif run("test_reading_and_writing_unsigned_field_as_integer") then
      read_caesar_field_test_u0(net=>net, value=>u0);
      check_equal(u0, caesar_field_test_u0_init);

      -- Write new value as an integer.
      write_caesar_field_test_u0(net=>net, value=>2);

      -- Check it, both as an integer and SLV.
      read_caesar_field_test_u0(net=>net, value=>int);
      check_equal(int, 2);
      read_caesar_field_test_u0(net=>net, value=>u0);
      check_equal(u0, unsigned'("10"));

    elsif run("test_reading_and_writing_signed_field_as_integer") then
      read_caesar_field_test_s0(net=>net, value=>s0);
      check_equal(s0, caesar_field_test_s0_init);

      -- Write new value as an integer.
      write_caesar_field_test_s0(net=>net, value=>-2);

      -- Check it, both as an integer and SLV.
      read_caesar_field_test_s0(net=>net, value=>int);
      check_equal(int, -2);
      read_caesar_field_test_s0(net=>net, value=>s0);
      check_equal(s0, signed'("10"));

    end if;

    test_runner_cleanup(runner);
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
