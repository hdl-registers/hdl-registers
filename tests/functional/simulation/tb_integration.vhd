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
use vunit_lib.bus_master_pkg.as_sync;
use vunit_lib.check_pkg.all;
use vunit_lib.com_pkg.net;
use vunit_lib.run_pkg.all;
use vunit_lib.sync_pkg.wait_until_idle;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

library bfm;

library common;
use common.types_pkg.all;

library register_file;
use register_file.register_file_pkg.all;
use register_file.register_operations_pkg.read_reg;
use register_file.register_operations_pkg.register_bus_master;
use register_file.register_operations_pkg.write_reg;

use work.caesar_simulation_test_pkg.all;

use work.caesar_regs_pkg.all;
use work.caesar_register_record_pkg.all;
use work.caesar_register_read_write_pkg.all;


entity tb_integration is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_integration is

  constant clk_period : time := 10 ns;
  signal clk : std_ulogic := '0';

  signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
  signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

  signal regs_up : caesar_regs_up_t := caesar_regs_up_init;
  signal regs_down : caesar_regs_down_t := caesar_regs_down_init;

  signal reg_was_read : caesar_reg_was_read_t := caesar_reg_was_read_init;
  signal reg_was_written : caesar_reg_was_written_t := caesar_reg_was_written_init;

  signal reg_was_read_count, reg_was_written_count : natural_vec_t(caesar_register_range) := (
    others => 0
  );

  signal command_start_low_count, command_abort_high_count : natural := 0;
  signal irq_status_a_low_count, irq_status_b_high_count : natural := 0;
  signal dummies_f_high_count, dummies_g_low_count : natural_vec_t(regs_down.dummies4'range) := (
    others => 0
  );
  signal dummies_a_high_count, dummies_b_low_count : natural_vec_t(regs_down.dummies4'range) := (
    others => 0
  );

begin

  clk <= not clk after clk_period / 2;
  test_runner_watchdog(runner, 1 ms);


  ------------------------------------------------------------------------------
  main : process
    procedure wait_for_write is
    begin
      wait_until_idle(net, as_sync(register_bus_master));
    end procedure;

    procedure check_irq_status_default_values(value : caesar_irq_status_t) is
    begin
      check_equal(value.a, caesar_irq_status_a_init);
      check_equal(value.b, caesar_irq_status_b_init);
      check_equal(value.c, caesar_irq_status_c_init);
      assert value.d = caesar_irq_status_d_init;
      check_equal(value.e, caesar_irq_status_e_init);
    end procedure;

    procedure check_dummies2_dummy_default_values(value : caesar_dummies2_dummy_t) is
    begin
      check_equal(value.f, caesar_dummies2_dummy_f_init);
      check_equal(value.g, caesar_dummies2_dummy_g_init);
      check_equal(value.h, caesar_dummies2_dummy_h_init);
      assert value.i = caesar_dummies2_dummy_i_init;
      check_equal(value.j, caesar_dummies2_dummy_j_init);
    end procedure;

    variable reg_was_read_expected, reg_was_written_expected : natural_vec_t(
      caesar_register_range
    ) := (others => 0);

    procedure test_plain_r_register is
      procedure check(
        reg : caesar_status_t; a : std_logic := '0'; b : std_logic := '1'
      ) is
      begin
        check_equal(reg.a, a);
        check_equal(reg.b, b);
      end procedure;

      variable status : caesar_status_t := caesar_status_init;
    begin
      -- Check init values in the register record and the aggregated record.
      check(caesar_status_init);
      check(caesar_regs_up_init.status);

      -- Check that read gets initial value.
      read_caesar_status(net=>net, value=>status);
      check(status);

      -- Check read updated value.
      regs_up.status.a <= '1';
      regs_up.status.b <= '0';
      read_caesar_status(net=>net, value=>status);
      check(status, '1', '0');

      -- Check that the correct register index was accessed.
      reg_was_read_expected(caesar_status) := 2;
    end procedure;

    procedure test_array_r_register is
      procedure check(
        reg : caesar_dummies_second_t; flip : std_logic := '1'; flop : integer := 99
      ) is
      begin
        check_equal(reg.flip, flip);
        check_equal(reg.flop, flop);
      end procedure;

      variable dummies_second : caesar_dummies_second_t := caesar_dummies_second_init;
    begin
      -- Check init values in the register record, the aggregated record and the register file.
      check(caesar_dummies_second_init);
      for array_index in regs_up.dummies'range loop
        check(caesar_regs_up_init.dummies(array_index).second);

        read_caesar_dummies_second(net=>net, array_index=>array_index, value=>dummies_second);
        check(dummies_second);

        -- Check that the correct register index was accessed.
        reg_was_read_expected(caesar_dummies_second(array_index=>array_index)) := 1;
        assert reg_was_read_expected = reg_was_read_count;
      end loop;

      -- Check read updated value.
      regs_up.dummies(0).second.flip <= '0';
      regs_up.dummies(0).second.flop <= 66;
      read_caesar_dummies_second(net=>net, array_index=>0, value=>dummies_second);
      check(dummies_second, '0', 66);

      -- Check that the correct register index was accessed.
      reg_was_read_expected(caesar_dummies_second(array_index=>0)) := 2;
      assert reg_was_read_expected = reg_was_read_count;

      -- Check that another indexes of the array still have the init value.
      for array_index in 1 to regs_up.dummies'high loop
        read_caesar_dummies_second(net=>net, array_index=>array_index, value=>dummies_second);
        check(dummies_second);

        reg_was_read_expected(caesar_dummies_second(array_index=>array_index)) := 2;
      end loop;
    end procedure;

    procedure test_plain_w_register is
      procedure check(
        reg : caesar_address_t;
        a : unsigned(7 downto 0) := "11001100";
        b : unsigned(7 downto 0) := "10101010"
      ) is
      begin
        check_equal(reg.a, a);
        check_equal(reg.b, b);
      end procedure;

      variable address : caesar_address_t := caesar_address_init;
    begin
      -- Check init values in the register record, the aggregated record and in the register file.
      check(caesar_address_init);
      check(caesar_regs_down_init.address);
      check(regs_down.address);

      -- Check writing updated value.
      address.a := "01010101";
      address.b := "00110011";
      write_caesar_address(net=>net, value=>address);
      wait_for_write;
      check(regs_down.address, "01010101", "00110011");

      -- Check that the correct register index was accessed.
      reg_was_written_expected(caesar_address) := 1;
    end procedure;

    procedure test_array_w_register is
      procedure check(
        reg : caesar_dummies4_flabby_t;
        count : integer := -19;
        enable : std_logic := '1'
      ) is
      begin
        check_equal(reg.count, count);
        check_equal(reg.enable, enable);
      end procedure;

      variable flabby : caesar_dummies4_flabby_t := caesar_dummies4_flabby_init;
    begin
      -- Check init values in the register record, the aggregated record and in the register file.
      check(caesar_dummies4_flabby_init);
      for array_index in regs_down.dummies4'range loop
        check(caesar_regs_down_init.dummies4(array_index).flabby);
        check(regs_down.dummies4(array_index).flabby);
      end loop;

      -- Check writing updated value.
      flabby.count := -13;
      flabby.enable := '0';
      write_caesar_dummies4_flabby(net=>net, array_index=>regs_down.dummies4'high, value=>flabby);
      wait_for_write;
      check(regs_down.dummies4(regs_down.dummies4'high).flabby, -13, '0');

      -- Check that other indexes of the array still have the init value.
      for array_index in 0 to regs_down.dummies4'high - 1 loop
        check(regs_down.dummies4(array_index).flabby);
      end loop;

      -- Check that the correct register index was accessed.
      reg_was_written_expected(caesar_dummies4_flabby(array_index=>regs_down.dummies4'high)) := 1;
    end procedure;

    procedure check_config(got : caesar_config_t; expected : caesar_config_t) is
    begin
      check_equal(got.plain_bit_a, expected.plain_bit_a);
      check_equal(got.plain_bit_vector, expected.plain_bit_vector);
      check_equal(got.plain_integer, expected.plain_integer);
      assert got.plain_enumeration = expected.plain_enumeration;
      check_equal(got.plain_bit_b, expected.plain_bit_b);
    end procedure;

    procedure test_plain_r_w_register is
      variable config : caesar_config_t := caesar_config_init;
    begin
      -- Check init values in the aggregated record and in the register file.
      check_config(got=>caesar_regs_down_init.config, expected=>caesar_config_init);
      check_config(got=>regs_down.config, expected=>caesar_config_init);

      read_caesar_config(net=>net, value=>config);
      check_config(got=>config, expected=>caesar_config_init);

      -- Check writing updated value.
      write_caesar_config(net=>net, value=>caesar_config_non_init);
      wait_for_write;

      -- Should be set in register as well as in the read-back value.
      check_config(got=>regs_down.config, expected=>caesar_config_non_init);
      read_caesar_config(net=>net, value=>config);
      check_config(got=>config, expected=>caesar_config_non_init);

      -- Check that the correct register index was accessed.
      reg_was_read_expected(caesar_config) := 2;
      reg_was_written_expected(caesar_config) := 1;
    end procedure;

    procedure test_array_r_w_register is
      procedure check_dummies_first(
        got : caesar_dummies_first_t; expected : caesar_dummies_first_t
      ) is
      begin
        check_equal(got.array_integer, expected.array_integer);
        check_equal(got.array_bit_a, expected.array_bit_a);
        check_equal(got.array_bit_b, expected.array_bit_b);
        check_equal(got.array_bit_vector, expected.array_bit_vector);
        assert got.array_enumeration = expected.array_enumeration;
      end procedure;

      variable first : caesar_dummies_first_t := caesar_dummies_first_init;
    begin
      -- Check init values in the aggregated record and in the register file.
      for array_index in regs_down.dummies'range loop
        check_dummies_first(
          got=>caesar_regs_down_init.dummies(array_index).first, expected=>caesar_dummies_first_init
        );
        check_dummies_first(
          got=>regs_down.dummies(array_index).first, expected=>caesar_dummies_first_init
        );

        read_caesar_dummies_first(net=>net, array_index=>array_index, value=>first);
        check_dummies_first(got=>first, expected=>caesar_dummies_first_init);

        -- Check that the correct register index was accessed.
        reg_was_read_expected(caesar_dummies_first(array_index=>array_index)) := 1;
        assert reg_was_read_expected = reg_was_read_count;
      end loop;

      -- Check writing updated value.
      write_caesar_dummies_first(net=>net, array_index=>2, value=>caesar_dummies_first_non_init);
      wait_for_write;

      -- Should be set in register as well as in the read-back value.
      check_dummies_first(got=>regs_down.dummies(2).first, expected=>caesar_dummies_first_non_init);
      read_caesar_dummies_first(net=>net, array_index=>2, value=>first);
      check_dummies_first(got=>first, expected=>caesar_dummies_first_non_init);

      -- Check that the correct register index was accessed.
      reg_was_read_expected(caesar_dummies_first(array_index=>2)) := 2;
      assert reg_was_read_expected = reg_was_read_count;

      -- Check that other indexes in the array still have the init value.
      for array_index in 0 to 1 loop
        read_caesar_dummies_first(net=>net, array_index=>array_index, value=>first);
        check_dummies_first(got=>first, expected=>caesar_dummies_first_init);

        reg_was_read_expected(caesar_dummies_first(array_index=>array_index)) := 2;
      end loop;

      -- Check that the correct register index was accessed.
      reg_was_written_expected(caesar_dummies_first(array_index=>2)) := 1;
    end procedure;

    procedure test_plain_wpulse_register is
      procedure check(
        reg : caesar_command_t;
        start : std_logic := '1';
        abort : std_logic := '0'
      ) is
      begin
        check_equal(reg.start, start);
        check_equal(reg.abort, abort);
      end procedure;

      variable command : caesar_command_t := caesar_command_init;
    begin
      -- Check init values in the register record, the aggregated record and in the register file.
      check(caesar_command_init);
      check(caesar_regs_down_init.command);
      check(regs_down.command);

      wait for 10 * clk_period;
      check_equal(command_start_low_count, 0);
      check_equal(command_abort_high_count, 0);

      -- Write with one bit having a non-default value.
      command.start := '0';
      write_caesar_command(net=>net, value=>command);
      wait_for_write;
      check_equal(command_start_low_count, 1);
      check_equal(command_abort_high_count, 0);

      -- Write with two bits having a non-default value.
      command.abort := '1';
      write_caesar_command(net=>net, value=>command);
      wait_for_write;
      check_equal(command_start_low_count, 2);
      check_equal(command_abort_high_count, 1);

      -- Should still be the same after a while.
      wait for 10 * clk_period;
      check_equal(command_start_low_count, 2);
      check_equal(command_abort_high_count, 1);

      -- Check that the correct register index was accessed.
      reg_was_written_expected(caesar_command) := 2;
    end procedure;

    procedure test_array_wpulse_register is
      procedure check(
        reg : caesar_dummies4_dummy_t;
        a : std_logic := '0';
        b : std_logic := '1'
      ) is
      begin
        check_equal(reg.a, a);
        check_equal(reg.b, b);
      end procedure;

      variable dummy : caesar_dummies4_dummy_t := caesar_dummies4_dummy_init;
    begin
      -- Check init values in the register record, the aggregated record and in the register file.
      check(caesar_dummies4_dummy_init);
      for array_index in caesar_regs_down_init.dummies4'range loop
        check(caesar_regs_down_init.dummies4(array_index).dummy);
        check(regs_down.dummies4(array_index).dummy);
      end loop;

      wait for 10 * clk_period;
      assert dummies_a_high_count = (0, 0);
      assert dummies_b_low_count = (0, 0);

      -- Write with one bit having a non-default value.
      dummy.a := '1';
      write_caesar_dummies4_dummy(net=>net, array_index=>1, value=>dummy);
      wait_for_write;
      assert dummies_a_high_count = (0, 1);
      assert dummies_b_low_count = (0, 0);

      -- Write with two bits having a non-default value.
      dummy.b := '0';
      write_caesar_dummies4_dummy(net=>net, array_index=>1, value=>dummy);
      wait_for_write;
      assert dummies_a_high_count = (0, 2);
      assert dummies_b_low_count = (0, 1);

      -- Should still be the same after a while.
      wait for 10 * clk_period;
      assert dummies_a_high_count = (0, 2);
      assert dummies_b_low_count = (0, 1);

      -- Check that the correct register index was accessed.
      reg_was_written_expected(caesar_dummies4_dummy(array_index=>1)) := 2;
    end procedure;

    procedure test_plain_r_wpulse_register is
      procedure check(
        reg : caesar_irq_status_t;
        a : std_logic := '1';
        b : std_logic := '0'
      ) is
      begin
        check_equal(reg.a, a);
        check_equal(reg.b, b);
      end procedure;

      variable irq_status : caesar_irq_status_t := caesar_irq_status_init;
    begin
      -- Check init values in the register record, the aggregated record and in the register file.
      check(caesar_irq_status_init);
      check(caesar_regs_down_init.irq_status);
      check(regs_down.irq_status);

      wait for 10 * clk_period;
      check_equal(irq_status_a_low_count, 0);
      check_equal(irq_status_b_high_count, 0);

      -- Check setting an updated read value.
      regs_up.irq_status.a <= '0';
      regs_up.irq_status.b <= '1';
      read_caesar_irq_status(net=>net, value=>irq_status);
      check(irq_status, '0', '1');

      -- Read value should not affect the 'down' value.
      wait for 10 * clk_period;
      check_equal(irq_status_a_low_count, 0);
      check_equal(irq_status_b_high_count, 0);

      -- Write with one bit having a non-default value.
      irq_status.a := '1';
      irq_status.b := '1';
      write_caesar_irq_status(net=>net, value=>irq_status);
      wait_for_write;
      wait for 10 * clk_period;
      check_equal(irq_status_a_low_count, 0);
      check_equal(irq_status_b_high_count, 1);

      -- Should not affect the read value which we set above.
      read_caesar_irq_status(net=>net, value=>irq_status);
      check(irq_status, '0', '1');

      -- Check that the correct register index was accessed.
      reg_was_read_expected(caesar_irq_status) := 2;
      reg_was_written_expected(caesar_irq_status) := 1;
    end procedure;

    procedure test_array_r_wpulse_register is
      procedure check(
        reg : caesar_dummies2_dummy_t;
        f : std_logic := '0';
        g : std_logic := '1'
      ) is
      begin
        check_equal(reg.f, f);
        check_equal(reg.g, g);
      end procedure;

      variable dummy : caesar_dummies2_dummy_t := caesar_dummies2_dummy_init;
    begin
      -- Check init values in the register record, the aggregated record and in the register file.
      check(caesar_dummies2_dummy_init);
      for array_index in caesar_regs_down_init.dummies2'range loop
        check(caesar_regs_down_init.dummies2(array_index).dummy);
        check(regs_down.dummies2(array_index).dummy);
      end loop;

      wait for 10 * clk_period;
      assert dummies_f_high_count = (0, 0);
      assert dummies_g_low_count = (0, 0);

      -- Check setting an updated read value.
      regs_up.dummies2(1).dummy.f <= '1';
      regs_up.dummies2(1).dummy.g <= '0';
      read_caesar_dummies2_dummy(net=>net, array_index=>1, value=>dummy);
      check(dummy, '1', '0');

      -- Read value should not affect the 'down' value.
      wait for 10 * clk_period;
      assert dummies_f_high_count = (0, 0);
      assert dummies_g_low_count = (0, 0);

      -- Write with one bit having a non-default value.
      dummy.f := '1';
      dummy.g := '1';
      write_caesar_dummies2_dummy(net=>net, array_index=>1, value=>dummy);
      wait_for_write;
      assert dummies_f_high_count = (0, 1);
      assert dummies_g_low_count = (0, 0);

      -- Should not affect the read value which we set above.
      read_caesar_dummies2_dummy(net=>net, array_index=>1, value=>dummy);
      check(dummy, '1', '0');

      -- Check that the correct register index was accessed.
      reg_was_read_expected(caesar_dummies2_dummy(array_index=>1)) := 2;
      reg_was_written_expected(caesar_dummies2_dummy(array_index=>1)) := 1;
    end procedure;

    variable config, config2 : caesar_config_t;
    variable command : caesar_command_t := caesar_command_init;
    variable irq_status : caesar_irq_status_t;
    variable dummies_first, dummies_first2 : caesar_dummies_first_t;
    variable dummies2_dummy : caesar_dummies2_dummy_t;

    variable reg : register_t := (others => '0');
    variable bit_1, bit_2 : std_ulogic := '0';

    variable check_register_access_counts : boolean := true;
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_reading_write_only_register_should_fail") then
      -- vunit: .expected_failure
      read_reg(net=>net, reg_index=>caesar_command, value=>reg);

    elsif run("test_writing_read_only_register_should_fail") then
      -- vunit: .expected_failure
      write_reg(net=>net, reg_index=>caesar_status, value=>reg);

    elsif run("test_default_values_of_plain_registers") then
      -- Compare to the explicit values set in TOML.

      -- A plain register of type 'r_w' that has all the different field types.
      -- Show that the default value constants have been set correctly.
      check_equal(caesar_config_plain_bit_a_init, '0');
      check_equal(caesar_config_plain_bit_vector_init, std_logic_vector'("0011"));
      check_equal(caesar_config_plain_integer_init, 66);
      assert caesar_config_plain_enumeration_init = plain_enumeration_third;
      check_equal(caesar_config_plain_bit_b_init, '1');

      -- The aggregated record type should have identical init values.
      check_config(got=>caesar_regs_down_init.config, expected=>caesar_config_init);
      check_config(got=>regs_down.config, expected=>caesar_config_init);

      -- An 'r_w' register gets its default value from the 'default_values' generic,
      -- which is an SLV value calculated in Python.
      -- Show that converting to record from SLV works correctly.
      read_caesar_config(net=>net, value=>config);
      check_config(got=>config, expected=>caesar_config_init);

      reg_was_read_expected(caesar_config) := 1;

      -- A plain register of type 'r_wpulse' that has all the different field types.
      check_equal(caesar_irq_status_a_init, '1');
      check_equal(caesar_irq_status_b_init, '0');
      check_equal(caesar_irq_status_c_init, std_logic_vector'("101"));
      assert caesar_irq_status_d_init = d_second;
      check_equal(caesar_irq_status_e_init, -10);

      -- The aggregated record types, down and up, should have identical init values.
      check_irq_status_default_values(caesar_regs_up_init.irq_status);
      check_irq_status_default_values(caesar_regs_down_init.irq_status);

      -- Reading the value of a 'r_wpulse' register, you get the value from 'regs_up'.
      -- Hence, the value is converted from record to SLV, read over register bus as an SLV below,
      -- and then converted back to record.
      read_caesar_irq_status(net=>net, value=>irq_status);
      check_irq_status_default_values(irq_status);

      reg_was_read_expected(caesar_irq_status) := 1;

    elsif run("test_default_values_of_array_registers") then
      -- Similar test as above but for a register in a register array.
      -- A register of type 'r_wpulse' in a register array that has all different field types.
      -- Compare to the explicit values set in TOML.
      check_equal(caesar_dummies2_dummy_f_init, '0');
      check_equal(caesar_dummies2_dummy_g_init, '1');
      check_equal(caesar_dummies2_dummy_h_init, std_logic_vector'("01010"));
      assert caesar_dummies2_dummy_i_init = i_third;
      check_equal(caesar_dummies2_dummy_j_init, -19);

      -- The aggregated record types, down and up, should have identical init values.
      -- In all repetitions of the array.
      check_equal(caesar_regs_up_init.dummies2'length, 2);
      check_equal(caesar_regs_down_init.dummies2'length, 2);

      for array_index in caesar_regs_up_init.dummies2'range loop
        check_dummies2_dummy_default_values(caesar_regs_up_init.dummies2(array_index).dummy);
        check_dummies2_dummy_default_values(caesar_regs_down_init.dummies2(array_index).dummy);

        read_caesar_dummies2_dummy(net=>net, array_index=>array_index, value=>dummies2_dummy);
        check_dummies2_dummy_default_values(dummies2_dummy);

        reg_was_read_expected(caesar_dummies2_dummy(array_index)) := 1;
      end loop;

    elsif run("test_write_value_to_plain_register") then
      -- Set different values than the default values.
      config.plain_bit_a := '1';
      config.plain_bit_vector := "1010";
      config.plain_integer := -13;
      config.plain_enumeration := plain_enumeration_fifth;
      config.plain_bit_b := '0';

      -- Convert to SLV, write over register bus.
      -- Register file converts it back to a record for the checks below.
      write_caesar_config(net=>net, value=>config);
      reg_was_written_expected(caesar_config) := 1;
      wait_for_write;

      check_equal(regs_down.config.plain_bit_a, '1');
      check_equal(regs_down.config.plain_bit_vector, std_logic_vector'("1010"));
      check_equal(regs_down.config.plain_integer, -13);
      assert regs_down.config.plain_enumeration = plain_enumeration_fifth;
      check_equal(regs_down.config.plain_bit_b, '0');

    elsif run("test_write_value_to_array_register") then
      -- Test writing different data to the same register but different repetitions of the array.

      dummies_first.array_integer := 13;
      dummies_first.array_bit_a := '1';
      dummies_first.array_bit_b := '0';
      dummies_first.array_bit_vector := "10101";
      dummies_first.array_enumeration := array_enumeration_element1;

      write_caesar_dummies_first(net=>net, array_index=>0, value=>dummies_first);
      reg_was_written_expected(caesar_dummies_first(0)) := 1;

      dummies_first.array_integer := 57;
      dummies_first.array_bit_a := '0';
      dummies_first.array_bit_b := '1';
      dummies_first.array_bit_vector := "01010";
      dummies_first.array_enumeration := array_enumeration_element1;

      write_caesar_dummies_first(net=>net, array_index=>1, value=>dummies_first);
      reg_was_written_expected(caesar_dummies_first(1)) := 1;

      dummies_first.array_integer := 99;
      dummies_first.array_bit_a := '1';
      dummies_first.array_bit_b := '1';
      dummies_first.array_bit_vector := "11001";
      dummies_first.array_enumeration := array_enumeration_element0;

      write_caesar_dummies_first(net=>net, array_index=>2, value=>dummies_first);
      reg_was_written_expected(caesar_dummies_first(2)) := 1;

      wait_for_write;

      check_equal(regs_down.dummies(0).first.array_integer, 13);
      check_equal(regs_down.dummies(0).first.array_bit_a, '1');
      check_equal(regs_down.dummies(0).first.array_bit_b, '0');
      check_equal(regs_down.dummies(0).first.array_bit_vector, std_logic_vector'("10101"));
      assert regs_down.dummies(0).first.array_enumeration = array_enumeration_element1;

      check_equal(regs_down.dummies(1).first.array_integer, 57);
      check_equal(regs_down.dummies(1).first.array_bit_a, '0');
      check_equal(regs_down.dummies(1).first.array_bit_b, '1');
      check_equal(regs_down.dummies(1).first.array_bit_vector, std_logic_vector'("01010"));
      assert regs_down.dummies(1).first.array_enumeration = array_enumeration_element1;

      check_equal(regs_down.dummies(2).first.array_integer, 99);
      check_equal(regs_down.dummies(2).first.array_bit_a, '1');
      check_equal(regs_down.dummies(2).first.array_bit_b, '1');
      check_equal(regs_down.dummies(2).first.array_bit_vector, std_logic_vector'("11001"));
      assert regs_down.dummies(2).first.array_enumeration = array_enumeration_element0;

    elsif run("test_operations_on_plain_r_register") then
      test_plain_r_register;

    elsif run("test_operations_on_array_r_register") then
      test_array_r_register;

    elsif run("test_operations_on_plain_w_register") then
      test_plain_w_register;

    elsif run("test_operations_on_array_w_register") then
      test_array_w_register;

    elsif run("test_operations_on_plain_r_w_register") then
      test_plain_r_w_register;

    elsif run("test_operations_on_array_r_w_register") then
      test_array_r_w_register;

    elsif run("test_operations_on_plain_wpulse_register") then
      test_plain_wpulse_register;

    elsif run("test_operations_on_array_wpulse_register") then
      test_array_wpulse_register;

    elsif run("test_operations_on_plain_r_wpulse_register") then
      test_plain_r_wpulse_register;

    elsif run("test_operations_on_array_r_wpulse_register") then
      test_array_r_wpulse_register;

    elsif run("test_read_plain_field") then
      -- Check default value.
      read_caesar_config_plain_bit_a(net=>net, value=>bit_1);
      read_caesar_config_plain_bit_b(net=>net, value=>bit_2);

      check_equal(bit_1, '0');
      check_equal(bit_2, '1');

      -- Write a new value.
      config.plain_bit_a := '1';
      config.plain_bit_b := '0';

      write_caesar_config(net=>net, value=>config);

      -- Check updated value.
      read_caesar_config_plain_bit_a(net=>net, value=>bit_1);
      read_caesar_config_plain_bit_b(net=>net, value=>bit_2);

      check_equal(bit_1, '1');
      check_equal(bit_2, '0');

      reg_was_read_expected(caesar_config) := 4;
      reg_was_written_expected(caesar_config) := 1;

    elsif run("test_read_array_field") then
      -- Check default value.
      read_caesar_dummies_first_array_bit_a(net=>net, array_index=>1, value=>bit_1);
      read_caesar_dummies_first_array_bit_b(net=>net, array_index=>1, value=>bit_2);

      check_equal(bit_1, caesar_dummies_first_init.array_bit_a);
      check_equal(bit_2, caesar_dummies_first_init.array_bit_b);

      -- Write a new value.
      dummies_first.array_bit_a := caesar_dummies_first_non_init.array_bit_a;
      dummies_first.array_bit_b := caesar_dummies_first_non_init.array_bit_b;

      write_caesar_dummies_first(net=>net, array_index=>1, value=>dummies_first);

      -- Check updated value.
      read_caesar_dummies_first_array_bit_a(net=>net, array_index=>1, value=>bit_1);
      read_caesar_dummies_first_array_bit_b(net=>net, array_index=>1, value=>bit_2);

      check_equal(bit_1, caesar_dummies_first_non_init.array_bit_a);
      check_equal(bit_2, caesar_dummies_first_non_init.array_bit_b);

      reg_was_read_expected(caesar_dummies_first(array_index=>1)) := 4;
      reg_was_written_expected(caesar_dummies_first(array_index=>1)) := 1;

    elsif run("test_plain_field_read_modify_write") then
      -- This register is of mode "r_w", so the procedure will read-modify-write.
      read_caesar_config(net=>net, value=>config);
      assert config = caesar_config_init;

      -- Write a new value.
      config.plain_bit_a := not config.plain_bit_a;
      write_caesar_config_plain_bit_a(net=>net, value=>config.plain_bit_a);

      -- Check updated value.
      read_caesar_config(net=>net, value=>config2);
      assert config2 = config;

      reg_was_read_expected(caesar_config) := 3;
      reg_was_written_expected(caesar_config) := 1;

      -- Write a new value on a different bit.
      config.plain_bit_b := not config.plain_bit_b;
      write_caesar_config_plain_bit_b(net=>net, value=>config.plain_bit_b);

      -- Check updated value.
      read_caesar_config(net=>net, value=>config2);
      assert config2 = config;

      reg_was_read_expected(caesar_config) := 5;
      reg_was_written_expected(caesar_config) := 2;

    elsif run("test_plain_field_write") then
      -- This register is of mode "wpulse", so the procedure will only write.
      command.abort := not command.abort;
      write_caesar_command_abort(net=>net, value=>command.abort);

      wait until regs_down.command'event for 10 * clk_period;
      wait until rising_edge(clk);
      assert regs_down.command.abort = '1';
      -- The 'start' field still has its non-zero default value in the write.
      assert regs_down.command.start = '1';

      -- Should go back to default at the next clock cycle.
      wait until rising_edge(clk);
      assert regs_down.command.abort = '0';
      assert regs_down.command.start = '1';

      reg_was_written_expected(caesar_command) := 1;

    elsif run("test_array_field_read_modify_write") then
      -- This register is of mode "r_w", so the procedure will read-modify-write.
      read_caesar_dummies_first(net=>net, array_index=>1, value=>dummies_first);
      assert dummies_first.array_enumeration = caesar_dummies_first_init.array_enumeration;

      -- Write a new value.
      dummies_first.array_enumeration := caesar_dummies_first_non_init.array_enumeration;
      write_caesar_dummies_first_array_enumeration(
        net=>net, array_index=>1, value=>dummies_first.array_enumeration
      );

      -- Check updated value.
      read_caesar_dummies_first(net=>net, array_index=>1, value=>dummies_first2);
      assert dummies_first2 = dummies_first;

      reg_was_read_expected(caesar_dummies_first(array_index=>1)) := 3;
      reg_was_written_expected(caesar_dummies_first(array_index=>1)) := 1;

    end if;

    wait_for_write;

    if check_register_access_counts then
      assert reg_was_read_expected = reg_was_read_count report "Incorrect register read count";
      assert reg_was_written_expected = reg_was_written_count
        report "Incorrect register write count";
    end if;

    test_runner_cleanup(runner);
  end process;


  ------------------------------------------------------------------------------
  count_register_status : process
  begin
    wait until rising_edge(clk);

    command_start_low_count <= command_start_low_count + to_int(not regs_down.command.start);
    command_abort_high_count <= command_abort_high_count + to_int(regs_down.command.abort);

    irq_status_a_low_count <= irq_status_a_low_count + to_int(not regs_down.irq_status.a);
    irq_status_b_high_count <= irq_status_b_high_count + to_int(regs_down.irq_status.b);

    for array_index in regs_down.dummies2'range loop
      dummies_f_high_count(array_index) <= (
        dummies_f_high_count(array_index) + to_int(regs_down.dummies2(array_index).dummy.f)
      );

      dummies_g_low_count(array_index) <= (
        dummies_g_low_count(array_index) + to_int(not regs_down.dummies2(array_index).dummy.g)
      );
    end loop;

    for array_index in regs_down.dummies4'range loop
      dummies_a_high_count(array_index) <= (
        dummies_a_high_count(array_index) + to_int(regs_down.dummies4(array_index).dummy.a)
      );

      dummies_b_low_count(array_index) <= (
        dummies_b_low_count(array_index) + to_int(not regs_down.dummies4(array_index).dummy.b)
      );
    end loop;
  end process;


  ------------------------------------------------------------------------------
  count_register_accesses : process
  begin
    wait until rising_edge(clk);

    assert reg_was_read_count'length = 22;

    reg_was_read_count(caesar_config) <=
      reg_was_read_count(caesar_config) + to_int(reg_was_read.config);
    reg_was_read_count(caesar_irq_status) <=
      reg_was_read_count(caesar_irq_status) + to_int(reg_was_read.irq_status);
    reg_was_read_count(caesar_status) <=
      reg_was_read_count(caesar_status) + to_int(reg_was_read.status);
    reg_was_read_count(caesar_current_timestamp) <=
      reg_was_read_count(caesar_current_timestamp) + to_int(reg_was_read.current_timestamp);

    reg_was_written_count(caesar_config) <=
      reg_was_written_count(caesar_config) + to_int(reg_was_written.config);
    reg_was_written_count(caesar_command) <=
      reg_was_written_count(caesar_command) + to_int(reg_was_written.command);
    reg_was_written_count(caesar_irq_status) <=
      reg_was_written_count(caesar_irq_status) + to_int(reg_was_written.irq_status);
    reg_was_written_count(caesar_address) <=
      reg_was_written_count(caesar_address) + to_int(reg_was_written.address);
    reg_was_written_count(caesar_tuser) <=
      reg_was_written_count(caesar_tuser) + to_int(reg_was_written.tuser);

    for array_idx in caesar_dummies_range loop
      reg_was_read_count(caesar_dummies_first(array_idx)) <=
        reg_was_read_count(caesar_dummies_first(array_idx))
        + to_int(reg_was_read.dummies(array_idx).first);
      reg_was_read_count(caesar_dummies_second(array_idx)) <=
        reg_was_read_count(caesar_dummies_second(array_idx))
        + to_int(reg_was_read.dummies(array_idx).second);

      reg_was_written_count(caesar_dummies_first(array_idx)) <=
        reg_was_written_count(caesar_dummies_first(array_idx))
        + to_int(reg_was_written.dummies(array_idx).first);
    end loop;

    for array_idx in caesar_dummies2_range loop
      reg_was_read_count(caesar_dummies2_dummy(array_idx)) <=
        reg_was_read_count(caesar_dummies2_dummy(array_idx))
        + to_int(reg_was_read.dummies2(array_idx).dummy);

      reg_was_written_count(caesar_dummies2_dummy(array_idx)) <=
        reg_was_written_count(caesar_dummies2_dummy(array_idx))
        + to_int(reg_was_written.dummies2(array_idx).dummy);
    end loop;

    for array_idx in caesar_dummies3_range loop
      reg_was_read_count(caesar_dummies3_dummy(array_idx)) <=
        reg_was_read_count(caesar_dummies3_dummy(array_idx))
        + to_int(reg_was_read.dummies3(array_idx).dummy);
      reg_was_read_count(caesar_dummies3_status(array_idx)) <=
        reg_was_read_count(caesar_dummies3_status(array_idx))
        + to_int(reg_was_read.dummies3(array_idx).status);
    end loop;

    for array_idx in caesar_dummies4_range loop
      reg_was_written_count(caesar_dummies4_dummy(array_idx)) <=
        reg_was_written_count(caesar_dummies4_dummy(array_idx))
        + to_int(reg_was_written.dummies4(array_idx).dummy);
      reg_was_written_count(caesar_dummies4_flabby(array_idx)) <=
        reg_was_written_count(caesar_dummies4_flabby(array_idx))
        + to_int(reg_was_written.dummies4(array_idx).flabby);
    end loop;
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
      regs_down => regs_down,
      --
      reg_was_read => reg_was_read,
      reg_was_written => reg_was_written
    );

end architecture;
