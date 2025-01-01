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
use vunit_lib.com_pkg.net;
use vunit_lib.run_pkg.all;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

library bfm;

library register_file;
use register_file.register_file_pkg.all;

use work.caesar_simulation_test_pkg.all;

use work.caesar_register_check_pkg.all;
use work.caesar_register_record_pkg.all;
use work.caesar_register_read_write_pkg.all;


entity tb_check_pkg is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_check_pkg is

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
    variable reg_value : register_t := register_init;
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_check_equal_of_plain_register_fields") then
      check_caesar_config_plain_bit_a_equal(net=>net, expected=>caesar_config_init.plain_bit_a);
      check_caesar_config_plain_bit_b_equal(net=>net, expected=>caesar_config_init.plain_bit_b);
      check_caesar_config_plain_bit_vector_equal(
        net=>net, expected=>caesar_config_init.plain_bit_vector
      );
      check_caesar_config_plain_enumeration_equal(
        net=>net, expected=>caesar_config_init.plain_enumeration
      );
      check_caesar_config_plain_integer_equal(
        net=>net, expected=>caesar_config_init.plain_integer
      );

      check_caesar_field_test_ufixed0_equal(net=>net, expected=>"11111111");
      check_caesar_field_test_sfixed0_equal(net=>net, expected=>"111111");

    elsif run("test_check_equal_of_plain_register_as_record") then
      check_caesar_config_equal(net=>net, expected=>caesar_config_init);

    elsif run("test_check_equal_of_plain_register_as_slv") then
      reg_value := std_ulogic_vector(to_unsigned(14, 32));
      regs_up.current_timestamp <= reg_value;
      check_caesar_current_timestamp_equal(net=>net, expected=>reg_value);

    elsif run("test_check_equal_of_plain_register_as_integer") then
      regs_up.current_timestamp <= std_ulogic_vector(to_unsigned(14, 32));
      check_caesar_current_timestamp_equal(net=>net, expected=>14);

    elsif run("test_check_equal_of_array_register_fields") then
      -- Write a non-init value to one of the array indexes, to show that the array index argument
      -- is propagated.
      write_caesar_dummies_first(net=>net, array_index=>1, value=>caesar_dummies_first_non_init);

      check_caesar_dummies_first_array_bit_a_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init.array_bit_a
      );
      check_caesar_dummies_first_array_bit_b_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init.array_bit_b
      );
      check_caesar_dummies_first_array_bit_vector_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init.array_bit_vector
      );
      check_caesar_dummies_first_array_enumeration_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init.array_enumeration
      );
      check_caesar_dummies_first_array_integer_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init.array_integer
      );

    elsif run("test_check_equal_of_array_register_as_record") then
      -- Write a non-init value to one of the array indexes, to show that the array index argument
      -- is propagated.
      write_caesar_dummies_first(net=>net, array_index=>1, value=>caesar_dummies_first_non_init);

      check_caesar_dummies_first_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init
      );

    elsif run("test_check_equal_of_array_register_as_slv") then
      reg_value := std_ulogic_vector(to_unsigned(127, 32));
      regs_up.dummies3(0).status <= reg_value;

      check_caesar_dummies3_status_equal(net=>net, array_index=>0, expected=>reg_value);

    elsif run("test_check_equal_of_array_register_as_integer") then
      regs_up.dummies3(0).status <= std_ulogic_vector(to_unsigned(127, 32));

      check_caesar_dummies3_status_equal(net=>net, array_index=>0, expected=>127);

    elsif run("test_check_register_equal_fail_0") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_dummies_first_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init
      );

    elsif run("test_check_register_equal_fail_1") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      reg_value := std_ulogic_vector(to_unsigned(14, 32));
      check_caesar_current_timestamp_equal(
        net=>net, expected=>reg_value, base_address=>x"00050000", message=>"Alarming error!"
      );

    elsif run("test_check_register_equal_fail_2") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_current_timestamp_equal(net=>net, expected=>44);

    elsif run("test_check_equal_fail_for_bit_field") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_config_plain_bit_a_equal(
        net=>net, expected=>caesar_config_non_init.plain_bit_a
      );

    elsif run("test_check_equal_fail_for_bit_vector_field_at_a_base_address") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_config_plain_bit_vector_equal(
        net=>net, expected=>caesar_config_non_init.plain_bit_vector, base_address=>x"00050000"
      );

    elsif run("test_check_equal_fail_for_enumeration_field") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_config_plain_enumeration_equal(
        net=>net, expected=>caesar_config_non_init.plain_enumeration
      );

    elsif run("test_check_equal_fail_for_integer_field") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_config_plain_integer_equal(
        net=>net, expected=>caesar_config_non_init.plain_integer
      );

    elsif run("test_check_equal_fail_for_ufixed_field") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_field_test_ufixed0_equal(
        net=>net, expected=>"10101010", message=>"Custom message here"
      );

    elsif run("test_check_equal_fail_for_sfixed_field") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_field_test_sfixed0_equal(net=>net, expected=>"101010");

    elsif run("test_check_equal_fail_for_array_register_field") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_dummies_first_array_bit_a_equal(
        net=>net, array_index=>1, expected=>caesar_dummies_first_non_init.array_bit_a
      );

    elsif run("test_check_equal_fail_for_array_register_field_at_a_base_address") then
      -- vunit: .expected_failure
      -- Should fail. Inspect the console output to see that error message is constructed correctly.
      check_caesar_dummies_first_array_bit_vector_equal(
        net=>net,
        array_index=>1,
        expected=>caesar_dummies_first_non_init.array_bit_vector,
        base_address=>x"00050000",
        message=>"Custom message here"
      );

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
