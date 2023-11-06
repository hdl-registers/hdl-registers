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

library common;
use common.types_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;
use reg_file.reg_operations_pkg.all;

use work.test_regs_pkg.all;


entity tb_axi_lite_reg_file is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_axi_lite_reg_file is

  signal clk : std_ulogic := '0';

  signal axi_lite_m2s : axi_lite_m2s_t := axi_lite_m2s_init;
  signal axi_lite_s2m : axi_lite_s2m_t := axi_lite_s2m_init;

  signal regs_up : test_regs_up_t := test_regs_up_init;
  signal regs_down : test_regs_down_t := test_regs_down_init;

  signal reg_was_read, reg_was_written : test_reg_was_accessed_t := (others => '0');

  signal reg_was_read_count, reg_was_written_count : natural_vec_t(reg_was_read'range) := (
    others => 0
  );

begin

  test_runner_watchdog(runner, 1 ms);
  clk <= not clk after 2 ns;


  ------------------------------------------------------------------------------
  main : process
    procedure wait_for_write is
    begin
      wait_until_idle(net, as_sync(regs_bus_master));
    end procedure;

    procedure check_config_default_values(value : test_config_t) is
    begin
      check_equal(value.plain_bit_a, test_config_plain_bit_a_init);
      check_equal(value.plain_bit_b, test_config_plain_bit_b_init);
      check_equal(value.plain_bit_vector, test_config_plain_bit_vector_init);
      assert value.plain_enumeration = test_config_plain_enumeration_init;
      check_equal(value.plain_integer, test_config_plain_integer_init);
    end procedure;

    procedure check_irq_status_default_values(value : test_irq_status_t) is
    begin
      check_equal(value.a, test_irq_status_a_init);
      check_equal(value.b, test_irq_status_b_init);
      check_equal(value.c, test_irq_status_c_init);
      assert value.d = test_irq_status_d_init;
      check_equal(value.e, test_irq_status_e_init);
    end procedure;

    procedure check_dummies2_dummy_default_values(value : test_dummies2_dummy_t) is
    begin
      check_equal(value.f, test_dummies2_dummy_f_init);
      check_equal(value.g, test_dummies2_dummy_g_init);
      check_equal(value.h, test_dummies2_dummy_h_init);
      assert value.i = test_dummies2_dummy_i_init;
      check_equal(value.j, test_dummies2_dummy_j_init);
    end procedure;

    variable reg : reg_t := (others => '0');

    variable config : test_config_t;
    variable irq_status : test_irq_status_t;
    variable dummies_first : test_dummies_first_t;
    variable dummies2_dummy : test_dummies2_dummy_t;

    variable reg_was_read_expected, reg_was_written_expected : natural_vec_t(reg_was_read'range) :=
      (others => 0);
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_default_values_of_plain_registers") then
      -- Compare to the explicit values set in TOML.

      -- A plain register of type 'r_w' that has all the different field types.
      -- Show that the default value constants have been set correctly.
      check_equal(test_config_plain_bit_a_init, '0');
      check_equal(test_config_plain_bit_b_init, '1');
      check_equal(test_config_plain_bit_vector_init, std_logic_vector'("0011"));
      assert test_config_plain_enumeration_init = plain_enumeration_third;
      check_equal(test_config_plain_integer_init, 66);

      -- The aggregated record type should have identical init values.
      check_config_default_values(test_regs_down_init.config);
      check_config_default_values(regs_down.config);

      -- An 'r_w' register gets its default value from the 'default_values' generic,
      -- which is an SLV value calculated in Python.
      -- Show that converting to record from SLV works correctly.
      read_reg(net=>net, reg_index=>test_config, value=>reg);
      config := to_test_config(reg);
      check_config_default_values(config);

      reg_was_read_expected(test_config) := 1;

      -- A plain register of type 'r_wpulse' that has all the different field types.
      check_equal(test_irq_status_a_init, '1');
      check_equal(test_irq_status_b_init, '0');
      check_equal(test_irq_status_c_init, std_logic_vector'("101"));
      assert test_irq_status_d_init = d_second;
      check_equal(test_irq_status_e_init, -10);

      -- The aggregated record types, down and up, should have identical init values.
      check_irq_status_default_values(test_regs_up_init.irq_status);
      check_irq_status_default_values(test_regs_down_init.irq_status);

      -- Reading the value of a 'r_wpulse' register, you get the value from 'regs_up'.
      -- Hence, the value is converted from record to SLV, read over register bus as an SLV below,
      -- and then converted back to record.
      read_reg(net=>net, reg_index=>test_irq_status, value=>reg);
      irq_status := to_test_irq_status(reg);
      check_irq_status_default_values(irq_status);

      reg_was_read_expected(test_irq_status) := 1;

    elsif run("test_default_values_of_array_registers") then
      -- Similar test as above but for a register in a register array.
      -- A register of type 'r_wpulse' in a register array that has all different field types.
      -- Compare to the explicit values set in TOML.
      check_equal(test_dummies2_dummy_f_init, '0');
      check_equal(test_dummies2_dummy_g_init, '1');
      check_equal(test_dummies2_dummy_h_init, std_logic_vector'("01010"));
      assert test_dummies2_dummy_i_init = i_third;
      check_equal(test_dummies2_dummy_j_init, -19);

      -- The aggregated record types, down and up, should have identical init values.
      -- In all repetitions of the array.
      check_equal(test_regs_up_init.dummies2'length, 2);
      check_equal(test_regs_down_init.dummies2'length, 2);

      for array_idx in test_regs_up_init.dummies2'range loop
        check_dummies2_dummy_default_values(test_regs_up_init.dummies2(array_idx).dummy);
        check_dummies2_dummy_default_values(test_regs_down_init.dummies2(array_idx).dummy);

        read_reg(net=>net, reg_index=>test_dummies2_dummy(array_idx), value=>reg);
        dummies2_dummy := to_test_dummies2_dummy(reg);
        check_dummies2_dummy_default_values(dummies2_dummy);

        reg_was_read_expected(test_dummies2_dummy(array_idx)) := 1;
      end loop;

    elsif run("test_write_value_to_plain_register") then
      -- Set different values than the default values.
      config.plain_bit_a := '1';
      config.plain_bit_b := '0';
      config.plain_bit_vector := "1010";
      config.plain_enumeration := plain_enumeration_fifth;
      config.plain_integer := -13;

      -- Convert to SLV, write over register bus.
      -- Register file converts it back to a record for the checks below.
      write_reg(net=>net, reg_index=>test_config, value=>to_slv(config));
      reg_was_written_expected(test_config) := 1;
      wait_for_write;

      check_equal(regs_down.config.plain_bit_a, '1');
      check_equal(regs_down.config.plain_bit_b, '0');
      check_equal(regs_down.config.plain_bit_vector, std_logic_vector'("1010"));
      assert regs_down.config.plain_enumeration = plain_enumeration_fifth;
      check_equal(regs_down.config.plain_integer, -13);

    elsif run("test_write_value_to_array_register") then
      -- Test writing different data to the same register but different repetitions of the array.

      dummies_first.array_bit_a := '1';
      dummies_first.array_bit_b := '0';
      dummies_first.array_bit_vector := "10101";
      dummies_first.array_enumeration := array_enumeration_element1;
      dummies_first.array_integer := 13;

      write_reg(net=>net, reg_index=>test_dummies_first(0), value=>to_slv(dummies_first));
      reg_was_written_expected(test_dummies_first(0)) := 1;

      dummies_first.array_bit_a := '0';
      dummies_first.array_bit_b := '1';
      dummies_first.array_bit_vector := "01010";
      dummies_first.array_enumeration := array_enumeration_element1;
      dummies_first.array_integer := 57;

      write_reg(net=>net, reg_index=>test_dummies_first(1), value=>to_slv(dummies_first));
      reg_was_written_expected(test_dummies_first(1)) := 1;

      dummies_first.array_bit_a := '1';
      dummies_first.array_bit_b := '1';
      dummies_first.array_bit_vector := "11001";
      dummies_first.array_enumeration := array_enumeration_element0;
      dummies_first.array_integer := 99;

      write_reg(net=>net, reg_index=>test_dummies_first(2), value=>to_slv(dummies_first));
      reg_was_written_expected(test_dummies_first(2)) := 1;

      wait_for_write;

      check_equal(regs_down.dummies(0).first.array_bit_a, '1');
      check_equal(regs_down.dummies(0).first.array_bit_b, '0');
      check_equal(regs_down.dummies(0).first.array_bit_vector, std_logic_vector'("10101"));
      assert regs_down.dummies(0).first.array_enumeration = array_enumeration_element1;
      check_equal(regs_down.dummies(0).first.array_integer, 13);

      check_equal(regs_down.dummies(1).first.array_bit_a, '0');
      check_equal(regs_down.dummies(1).first.array_bit_b, '1');
      check_equal(regs_down.dummies(1).first.array_bit_vector, std_logic_vector'("01010"));
      assert regs_down.dummies(1).first.array_enumeration = array_enumeration_element1;
      check_equal(regs_down.dummies(1).first.array_integer, 57);

      check_equal(regs_down.dummies(2).first.array_bit_a, '1');
      check_equal(regs_down.dummies(2).first.array_bit_b, '1');
      check_equal(regs_down.dummies(2).first.array_bit_vector, std_logic_vector'("11001"));
      assert regs_down.dummies(2).first.array_enumeration = array_enumeration_element0;
      check_equal(regs_down.dummies(2).first.array_integer, 99);

    elsif run("test_reading_write_only_register_should_fail") then
      -- vunit: .expected_failure
      read_reg(net=>net, reg_index=>test_command, value=>reg);

    elsif run("test_writing_read_only_register_should_fail") then
      -- vunit: .expected_failure
      write_reg(net=>net, reg_index=>test_status, value=>reg);

    end if;

    wait_for_write;

    assert reg_was_read_expected = reg_was_read_count;
    assert reg_was_written_expected = reg_was_written_count;

    test_runner_cleanup(runner);
  end process;


  ------------------------------------------------------------------------------
  count : process
  begin
    wait until rising_edge(clk);

    for reg_idx in reg_was_read'range loop
      reg_was_read_count(reg_idx) <= reg_was_read_count(reg_idx) + to_int(reg_was_read(reg_idx));
      reg_was_written_count(reg_idx) <= (
        reg_was_written_count(reg_idx) + to_int(reg_was_written(reg_idx))
      );
    end loop;
  end process;


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
  test_reg_file_inst : entity work.test_reg_file
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
