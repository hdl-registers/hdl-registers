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
use vunit_lib.run_pkg.all;

use work.caesar_simulation_test_pkg.all;

use work.caesar_register_record_pkg.all;
use work.caesar_regs_pkg.all;


entity tb_caesar_simulation_test_pkg is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_caesar_simulation_test_pkg is

begin

  ------------------------------------------------------------------------------
  main : process
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_check_config_non_init_has_all_fields_different_than_init") then
      assert caesar_config_non_init.plain_bit_a /= caesar_config_init.plain_bit_a;
      assert caesar_config_non_init.plain_bit_vector /= caesar_config_init.plain_bit_vector;
      assert caesar_config_non_init.plain_integer /= caesar_config_init.plain_integer;
      assert caesar_config_non_init.plain_enumeration /= caesar_config_init.plain_enumeration;
      assert caesar_config_non_init.plain_bit_b /= caesar_config_init.plain_bit_b;


    elsif run("test_check_dummies_first_non_init_has_all_fields_different_than_init") then
      assert caesar_dummies_first_non_init.array_integer /= caesar_dummies_first_init.array_integer;
      assert caesar_dummies_first_non_init.array_bit_a /= caesar_dummies_first_init.array_bit_a;
      assert caesar_dummies_first_non_init.array_bit_b /= caesar_dummies_first_init.array_bit_b;
      assert (
        caesar_dummies_first_non_init.array_bit_vector
        /= caesar_dummies_first_init.array_bit_vector
      );
      assert (
        caesar_dummies_first_non_init.array_enumeration
        /= caesar_dummies_first_init.array_enumeration
      );

    end if;

    test_runner_cleanup(runner);
  end process;

end architecture;
