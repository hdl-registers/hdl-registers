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

use work.caesar_register_record_pkg.all;
use work.caesar_regs_pkg.all;


package caesar_simulation_test_pkg is

  -- Different values than init values.
  constant caesar_conf_non_init : caesar_conf_t := (
    plain_bit_a => '1',
    plain_bit_vector => "1100",
    plain_integer => -33,
    plain_enumeration => plain_enumeration_fifth,
    plain_bit_b => '0'
  );

  -- Different values than init values.
  constant caesar_dummies_first_non_init : caesar_dummies_first_t := (
    array_integer => 33,
    array_bit_a => '0',
    array_bit_b => '1',
    array_bit_vector => "11001",
    array_enumeration => array_enumeration_element0
  );

end package;
