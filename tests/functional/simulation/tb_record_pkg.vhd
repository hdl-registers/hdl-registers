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

library reg_file;
use reg_file.reg_file_pkg.all;

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
  variable reg : reg_t := (others => '0');
    variable test : caesar_field_test_t := caesar_field_test_init;
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

    end if;

    test_runner_cleanup(runner);
  end process;

end architecture;
