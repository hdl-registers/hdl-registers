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
use ieee.fixed_pkg.all;

library vunit_lib;
use vunit_lib.run_pkg.all;

library register_file;
use register_file.register_file_pkg.all;

use work.caesar_regs_pkg.all;
use work.caesar_register_record_pkg.all;


entity tb_record_pkg is
  generic (
    runner_cfg : string
  );
end entity;

architecture tb of tb_record_pkg is

begin

  test_runner_watchdog(runner, 1 ms);


  ------------------------------------------------------------------------------
  main : process
    variable reg : register_t := (others => '0');
    variable test : caesar_field_test_t := caesar_field_test_init;

    variable record_all : caesar_registers_t := caesar_registers_init;
    variable record_up : caesar_regs_up_t := caesar_regs_up_init;
    variable record_down : caesar_regs_down_t := caesar_regs_down_init;
    variable slv : caesar_regs_t := caesar_regs_init;
  begin
    test_runner_setup(runner, runner_cfg);

    if run("test_casting_unsigned_types") then
      test.u0 := to_unsigned(arg=>3, size_res=>test.u0);
      reg := to_slv(test);
      assert to_caesar_field_test(reg).u0 = test.u0;

    elsif run("test_casting_signed_types") then
      test.s0 := to_signed(arg=>-1, size_res=>test.s0);
      reg := to_slv(test);
      assert to_caesar_field_test(reg).s0 = test.s0;

    elsif run("test_casting_unsigned_fixed_types") then
      test.ufixed0 := to_ufixed(arg=>35.25, size_res=>caesar_field_test_init.ufixed0);
      reg := to_slv(test);
      assert to_caesar_field_test(reg).ufixed0 = test.ufixed0;

    elsif run("test_casting_signed_fixed_types") then
      test.sfixed0 := to_sfixed(arg=>-1.375, size_res=>caesar_field_test_init.sfixed0);
      reg := to_slv(test);
      assert to_caesar_field_test(reg).sfixed0 = test.sfixed0;

    elsif run("test_casting_record") then
      record_all.status.a := '1';
      record_all.status.b := '0';
      record_all.status.c := -420;

      -- A register that is up-only.
      record_all.dummies(0).second.flip := '0';
      record_all.dummies(1).second.flip := '1';
      record_all.dummies(2).second.flip := '0';

      -- A register that is down-only.
      record_all.dummies4(0).flabby.enable := '1';
      record_all.dummies4(1).flabby.enable := '0';

      slv := to_slv(record_all);

      assert slv(caesar_status)(caesar_status_a) = '1';
      assert slv(caesar_status)(caesar_status_b) = '0';
      assert slv(caesar_status)(caesar_status_c) = "111111111111111111111001011100";

      assert slv(caesar_dummies_second(0))(caesar_dummies_second_flip) = '0';
      assert slv(caesar_dummies_second(1))(caesar_dummies_second_flip) = '1';
      assert slv(caesar_dummies_second(2))(caesar_dummies_second_flip) = '0';

      assert slv(caesar_dummies4_flabby(0))(caesar_dummies4_flabby_enable) = '1';
      assert slv(caesar_dummies4_flabby(1))(caesar_dummies4_flabby_enable) = '0';

    elsif run("test_casting_record_up") then
      record_up.status.a := '1';
      record_up.status.b := '0';

      record_up.dummies3(0).status := x"13371337";

      slv := to_slv(record_up);

      assert slv(caesar_status)(caesar_status_a) = '1';
      assert slv(caesar_status)(caesar_status_b) = '0';

      assert slv(caesar_dummies3_status(0)) = x"13371337";

    elsif run("test_casting_record_down") then
      slv(caesar_dummies4_dummy(0)) := x"fffffff2";
      slv(caesar_dummies4_dummy(1)) := x"fffffff1";

      record_down := to_caesar_regs_down(slv);

      assert record_down.dummies4(0).dummy.a = '0';
      assert record_down.dummies4(0).dummy.b = '1';

      assert record_down.dummies4(1).dummy.a = '1';
      assert record_down.dummies4(1).dummy.b = '0';

    end if;

    test_runner_cleanup(runner);
  end process;

end architecture;
