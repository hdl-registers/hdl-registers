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

use work.example_regs_pkg.all;


entity tb_generated_vhdl_package is
  generic (
    test_integer_lower_range : boolean := false;
    test_integer_upper_range : boolean := false;
    runner_cfg : string
  );
end entity;

architecture tb of tb_generated_vhdl_package is

begin

  ------------------------------------------------------------------------------
  main : process
    constant expected_base_address : unsigned(31 downto 0) := x"8000_0000";
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_register_addresses") then
      check_equal(example_configuration, 0);
      check_equal(example_status, 1);
      check_equal(example_command, 2);

      check_equal(example_base_addresses_array_length, 3);
      check_equal(example_base_addresses_read_address(0), 3);
      check_equal(example_base_addresses_write_address(0), 4);
      check_equal(example_base_addresses_read_address(1), 5);
      check_equal(example_base_addresses_write_address(1), 6);
      check_equal(example_base_addresses_read_address(2), 7);
      check_equal(example_base_addresses_write_address(2), 8);

    elsif run("test_register_modes") then
      assert example_reg_map(example_configuration).reg_type = r_w;
      assert example_reg_map(example_status).reg_type = r;
      assert example_reg_map(example_command).reg_type = wpulse;

      assert example_reg_map(example_base_addresses_read_address(0)).reg_type = r_w;
      assert example_reg_map(example_base_addresses_write_address(0)).reg_type = r_w;
      assert example_reg_map(example_base_addresses_read_address(1)).reg_type = r_w;
      assert example_reg_map(example_base_addresses_write_address(1)).reg_type = r_w;
      assert example_reg_map(example_base_addresses_read_address(2)).reg_type = r_w;
      assert example_reg_map(example_base_addresses_write_address(2)).reg_type = r_w;

    elsif run("test_register_field_indexes") then
      -- Generated bit field indexes should match the order and widths in the TOML

      -- Status register
      check_equal(example_status_idle, 0);
      check_equal(example_status_stalling, 1);

      check_equal(example_status_counter'low, 2);
      check_equal(example_status_counter'high, 9);
      check_equal(example_status_counter_width, 8);
      check_equal(example_status_counter_t'high, 7);
      check_equal(example_status_counter_t'low, 0);

      -- Fields in array registers
      check_equal(example_base_addresses_read_address_address'low, 0);
      check_equal(example_base_addresses_read_address_address'high, 27);
      check_equal(example_base_addresses_read_address_address_width, 28);

      check_equal(example_base_addresses_write_address_address'low, 0);
      check_equal(example_base_addresses_write_address_address'high, 27);
      check_equal(example_base_addresses_write_address_address_width, 28);

    elsif run("test_constants") then
      check_equal(example_constant_axi_data_width, 64);
      check_equal(example_constant_clock_rate_hz, 156250000.0);
      check_equal(example_constant_supports_pre_filtering, true);
      check_equal(example_constant_name, "example module");
      check_equal(example_constant_base_address, expected_base_address);

    elsif run("test_bit_vector_field_types") then
      check_equal(example_field_test_u0_t'high, 1);
      check_equal(example_field_test_u0_t'low, 0);

      check_equal(example_field_test_s0_t'high, 1);
      check_equal(example_field_test_s0_t'low, 0);

      check_equal(example_field_test_ufixed0_t'high, 5);
      check_equal(example_field_test_ufixed0_t'low, -2);

      check_equal(example_field_test_sfixed0_t'high, 2);
      check_equal(example_field_test_sfixed0_t'low, -3);

      check_equal(example_constant_clock_rate_hz, 156250000.0);

    end if;

    test_runner_cleanup(runner);
  end process;

end architecture;
