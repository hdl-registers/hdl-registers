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
use ieee.numeric_std.all;

library vunit_lib;
context vunit_lib.vunit_context;

library reg_file;
use reg_file.reg_file_pkg.all;

use work.test_regs_pkg.all;


entity tb_regs_pkg is
  generic (
    test_integer_lower_range : boolean := false;
    test_integer_upper_range : boolean := false;
    runner_cfg : string
  );
end entity;

architecture tb of tb_regs_pkg is

begin

  ------------------------------------------------------------------------------
  main : process
    constant expected_base_address : unsigned(35 downto 0) := x"8_0000_0000";

    variable reg : reg_t := (others => '0');
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_register_addresses") then
      check_equal(test_config, 0);
      check_equal(test_command, 1);
      check_equal(test_irq_status, 2);
      check_equal(test_status, 3);

      check_equal(test_dummies_array_length, 3);
      check_equal(test_dummies_first(0), 7);
      check_equal(test_dummies_second(0), 8);
      check_equal(test_dummies_first(1), 9);
      check_equal(test_dummies_second(1), 10);
      check_equal(test_dummies_first(2), 11);
      check_equal(test_dummies_second(2), 12);

      check_equal(test_dummies2_dummy(0), 13);

    elsif run("test_register_modes") then
      assert test_reg_map(test_config).reg_type = r_w;
      assert test_reg_map(test_status).reg_type = r;
      assert test_reg_map(test_command).reg_type = wpulse;
      assert test_reg_map(test_irq_status).reg_type = r_wpulse;
      assert test_reg_map(test_address).reg_type = w;

      assert test_reg_map(test_dummies_first(0)).reg_type = r_w;
      assert test_reg_map(test_dummies_second(0)).reg_type = r;
      assert test_reg_map(test_dummies_first(1)).reg_type = r_w;
      assert test_reg_map(test_dummies_second(1)).reg_type = r;
      assert test_reg_map(test_dummies_first(2)).reg_type = r_w;
      assert test_reg_map(test_dummies_second(2)).reg_type = r;

    elsif run("test_register_field_indexes") then
      -- Generated field indexes should match the order and widths in the TOML

      -- Status register
      check_equal(test_config_plain_bit_a, 0);
      check_equal(test_config_plain_bit_b, 1);

      check_equal(test_config_plain_bit_vector'low, 2);
      check_equal(test_config_plain_bit_vector'high, 5);
      check_equal(test_config_plain_bit_vector_width, 4);
      check_equal(test_config_plain_bit_vector_t'high, 3);
      check_equal(test_config_plain_bit_vector_t'low, 0);

      -- Fields in array registers
      check_equal(test_dummies_first_array_bit_a, 0);
      check_equal(test_dummies_first_array_bit_b, 1);

      check_equal(test_dummies_first_array_bit_vector'low, 2);
      check_equal(test_dummies_first_array_bit_vector'high, 6);
      check_equal(test_dummies_first_array_bit_vector_width, 5);
      check_equal(test_dummies_first_array_bit_vector_t'high, 4);
      check_equal(test_dummies_first_array_bit_vector_t'low, 0);

    elsif run("test_constants") then
      check_equal(test_constant_data_width, 24);
      check_equal(test_constant_decrement, -8);
      check_equal(test_constant_enabled, true);
      check_equal(test_constant_rate, 3.5);
      check_equal(test_constant_paragraph, "hello there :)");
      check_equal(test_constant_base_address_bin, expected_base_address);

    elsif run("test_bit_vector_field_types") then
      check_equal(test_field_test_u0_t'high, 1);
      check_equal(test_field_test_u0_t'low, 0);

      check_equal(test_field_test_s0_t'high, 1);
      check_equal(test_field_test_s0_t'low, 0);

      check_equal(test_field_test_ufixed0_t'high, 5);
      check_equal(test_field_test_ufixed0_t'low, -2);

      check_equal(test_field_test_sfixed0_t'high, 2);
      check_equal(test_field_test_sfixed0_t'low, -3);

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

      reg(test_config_plain_enumeration) := "000";
      assert to_test_config_plain_enumeration(reg) = plain_enumeration_first;

      reg(test_config_plain_enumeration) := "001";
      assert to_test_config_plain_enumeration(reg) = plain_enumeration_second;

      reg(test_config_plain_enumeration) := "010";
      assert to_test_config_plain_enumeration(reg) = plain_enumeration_third;

      reg(test_config_plain_enumeration) := "011";
      assert to_test_config_plain_enumeration(reg) = plain_enumeration_fourth;

      reg(test_config_plain_enumeration) := "100";
      assert to_test_config_plain_enumeration(reg) = plain_enumeration_fifth;

    elsif run("test_enumeration_out_of_range") then
      -- vunit: .expected_failure
      -- Element does not exist in enum.
      reg(test_config_plain_enumeration) := "110";
      assert to_test_config_plain_enumeration(reg) = plain_enumeration_fifth;

    elsif run("test_integer_to_slv") then
      check_equal(to_test_config_plain_integer_slv(-17), std_logic_vector'("11101111"));
      check_equal(to_test_config_plain_integer_slv(-16), std_logic_vector'("11110000"));
      check_equal(to_test_config_plain_integer_slv(-15), std_logic_vector'("11110001"));

      check_equal(to_test_config_plain_integer_slv(63), std_logic_vector'("00111111"));
      check_equal(to_test_config_plain_integer_slv(64), std_logic_vector'("01000000"));
      check_equal(to_test_config_plain_integer_slv(65), std_logic_vector'("01000001"));

    elsif run("test_integer_to_slv_out_of_range") then
      -- vunit: .expected_failure
      -- Is outside of the numeric range of the field.
      check_equal(to_test_config_plain_integer_slv(127), std_logic_vector'("01111111"));

    elsif run("test_integer_from_slv") then
      reg := (others => '1');

      reg(test_config_plain_integer) := "11101111";
      assert to_test_config_plain_integer(reg) = -17;

      reg(test_config_plain_integer) := "11110000";
      assert to_test_config_plain_integer(reg) = -16;

      reg(test_config_plain_integer) := "11110001";
      assert to_test_config_plain_integer(reg) = -15;

      reg(test_config_plain_integer) := "00111111";
      assert to_test_config_plain_integer(reg) = 63;

      reg(test_config_plain_integer) := "01000000";
      assert to_test_config_plain_integer(reg) = 64;

      reg(test_config_plain_integer) := "01000001";
      assert to_test_config_plain_integer(reg) = 65;

    elsif run("test_integer_from_slv_out_of_range") then
      -- vunit: .expected_failure
      -- Is outside of the numeric range of the field.
      reg(test_config_plain_integer) := "01111111";
      assert to_test_config_plain_integer(reg) = 1;
    end if;

    test_runner_cleanup(runner);
  end process;

end architecture;
