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
use vunit_lib.check_pkg.all;
use vunit_lib.run_pkg.all;

library register_file;
use register_file.register_file_pkg.all;

use work.caesar_regs_pkg.all;


entity tb_register_package is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_register_package is

begin

  ------------------------------------------------------------------------------
  main : process
    constant expected_base_address : unsigned(35 downto 0) := x"8_0000_0000";

    variable reg : register_t := (others => '0');
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_register_addresses") then
      check_equal(caesar_config, 0);
      check_equal(caesar_command, 1);
      check_equal(caesar_irq_status, 2);
      check_equal(caesar_status, 3);

      check_equal(caesar_dummies_array_length, 3);
      check_equal(caesar_dummies_first(0), 7);
      check_equal(caesar_dummies_second(0), 8);
      check_equal(caesar_dummies_first(1), 9);
      check_equal(caesar_dummies_second(1), 10);
      check_equal(caesar_dummies_first(2), 11);
      check_equal(caesar_dummies_second(2), 12);

      check_equal(caesar_dummies2_dummy(0), 13);

    elsif run("test_register_modes") then
      assert caesar_reg_map(caesar_config).mode = r_w;
      assert caesar_reg_map(caesar_status).mode = r;
      assert caesar_reg_map(caesar_command).mode = wpulse;
      assert caesar_reg_map(caesar_irq_status).mode = r_wpulse;
      assert caesar_reg_map(caesar_address).mode = w;

      assert caesar_reg_map(caesar_dummies_first(0)).mode = r_w;
      assert caesar_reg_map(caesar_dummies_second(0)).mode = r;
      assert caesar_reg_map(caesar_dummies_first(1)).mode = r_w;
      assert caesar_reg_map(caesar_dummies_second(1)).mode = r;
      assert caesar_reg_map(caesar_dummies_first(2)).mode = r_w;
      assert caesar_reg_map(caesar_dummies_second(2)).mode = r;

    elsif run("test_register_field_indexes") then
      -- Generated field indexes should match the order and widths in the TOML

      -- Status register
      check_equal(caesar_config_plain_bit_a, 0);

      check_equal(caesar_config_plain_bit_vector'low, 1);
      check_equal(caesar_config_plain_bit_vector'high, 4);
      check_equal(caesar_config_plain_bit_vector_width, 4);
      check_equal(caesar_config_plain_bit_vector_t'high, 3);
      check_equal(caesar_config_plain_bit_vector_t'low, 0);

      check_equal(caesar_config_plain_bit_b, 16);

      -- Fields in array registers
      check_equal(caesar_dummies_first_array_bit_a, 7);
      check_equal(caesar_dummies_first_array_bit_b, 8);

      check_equal(caesar_dummies_first_array_bit_vector'low, 9);
      check_equal(caesar_dummies_first_array_bit_vector'high, 13);
      check_equal(caesar_dummies_first_array_bit_vector_width, 5);
      check_equal(caesar_dummies_first_array_bit_vector_t'high, 4);
      check_equal(caesar_dummies_first_array_bit_vector_t'low, 0);

    elsif run("test_constants") then
      check_equal(caesar_constant_data_width, 24);
      check_equal(caesar_constant_decrement, -8);
      check_equal(caesar_constant_enabled, true);
      check_equal(caesar_constant_rate, 3.5);
      check_equal(caesar_constant_paragraph, "hello there :)");
      check_equal(caesar_constant_base_address_bin, expected_base_address);

    elsif run("test_bit_vector_numerical_interpretations") then
      check_equal(caesar_field_test_u0_t'high, 1);
      check_equal(caesar_field_test_u0_t'low, 0);

      check_equal(caesar_field_test_s0_t'high, 1);
      check_equal(caesar_field_test_s0_t'low, 0);

      check_equal(caesar_field_test_ufixed0_t'high, 5);
      check_equal(caesar_field_test_ufixed0_t'low, -2);

      check_equal(caesar_field_test_sfixed0_t'high, 2);
      check_equal(caesar_field_test_sfixed0_t'low, -3);

    elsif run("test_enumeration_to_slv") then
      check_equal(
        to_slv(plain_enumeration_first),
        std_logic_vector'("000")
      );
      check_equal(
        to_slv(plain_enumeration_second),
        std_logic_vector'("001")
      );
      check_equal(
        to_slv(plain_enumeration_third),
        std_logic_vector'("010")
      );
      check_equal(
        to_slv(plain_enumeration_fourth),
        std_logic_vector'("011")
      );
      check_equal(
        to_slv(plain_enumeration_fifth),
        std_logic_vector'("100")
      );

    elsif run("test_enumeration_from_slv") then
      reg := (others => '1');

      reg(caesar_config_plain_enumeration) := "000";
      assert to_caesar_config_plain_enumeration(reg) = plain_enumeration_first;

      reg(caesar_config_plain_enumeration) := "001";
      assert to_caesar_config_plain_enumeration(reg) = plain_enumeration_second;

      reg(caesar_config_plain_enumeration) := "010";
      assert to_caesar_config_plain_enumeration(reg) = plain_enumeration_third;

      reg(caesar_config_plain_enumeration) := "011";
      assert to_caesar_config_plain_enumeration(reg) = plain_enumeration_fourth;

      reg(caesar_config_plain_enumeration) := "100";
      assert to_caesar_config_plain_enumeration(reg) = plain_enumeration_fifth;

    elsif run("test_enumeration_out_of_range") then
      -- vunit: .expected_failure
      -- Element does not exist in enum.
      reg(caesar_config_plain_enumeration) := "110";
      assert to_caesar_config_plain_enumeration(reg) = plain_enumeration_fifth;

    elsif run("test_integer_to_slv") then
      check_equal(to_caesar_config_plain_integer_slv(-17), std_logic_vector'("11101111"));
      check_equal(to_caesar_config_plain_integer_slv(-16), std_logic_vector'("11110000"));
      check_equal(to_caesar_config_plain_integer_slv(-15), std_logic_vector'("11110001"));

      check_equal(to_caesar_config_plain_integer_slv(63), std_logic_vector'("00111111"));
      check_equal(to_caesar_config_plain_integer_slv(64), std_logic_vector'("01000000"));
      check_equal(to_caesar_config_plain_integer_slv(65), std_logic_vector'("01000001"));

    elsif run("test_integer_to_slv_out_of_range") then
      -- vunit: .expected_failure
      -- Is outside of the numeric range of the field.
      -- Aldec Riviera-PRO catches this error during compilation, so if you are running
      -- these functional tests with that simulator, this needs to be commented out.
      check_equal(to_caesar_config_plain_integer_slv(127), std_logic_vector'("01111111"));

    elsif run("test_integer_from_slv") then
      reg := (others => '1');

      reg(caesar_config_plain_integer) := "11101111";
      assert to_caesar_config_plain_integer(reg) = -17;

      reg(caesar_config_plain_integer) := "11110000";
      assert to_caesar_config_plain_integer(reg) = -16;

      reg(caesar_config_plain_integer) := "11110001";
      assert to_caesar_config_plain_integer(reg) = -15;

      reg(caesar_config_plain_integer) := "00111111";
      assert to_caesar_config_plain_integer(reg) = 63;

      reg(caesar_config_plain_integer) := "01000000";
      assert to_caesar_config_plain_integer(reg) = 64;

      reg(caesar_config_plain_integer) := "01000001";
      assert to_caesar_config_plain_integer(reg) = 65;

    elsif run("test_integer_from_slv_out_of_range") then
      -- vunit: .expected_failure
      -- Is outside of the numeric range of the field.
      reg(caesar_config_plain_integer) := "01111111";
      assert to_caesar_config_plain_integer(reg) = 1;
    end if;

    test_runner_cleanup(runner);
  end process;

end architecture;
