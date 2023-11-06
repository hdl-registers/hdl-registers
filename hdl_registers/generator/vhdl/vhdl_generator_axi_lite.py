# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import TYPE_CHECKING, Union

# Local folder libraries
from .vhdl_generator_common import RegisterVhdlGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class RegisterVhdlGeneratorAxiLite(RegisterVhdlGeneratorCommon):
    """
    Generate a wrapper around generic AXI-Lite register files with correct generics and ports.
    """

    def get_reg_file(self, register_objects: list[Union["Register", "RegisterArray"]]):
        """
        Get VHDL code for a wrapper around the generic AXi_lite register file from hdl_modules:

        * https://hdl-modules.com/modules/reg_file/reg_file.html#axi-lite-reg-file-vhd
        * https://gitlab.com/hdl_modules/hdl_modules/-/blob/main/modules/reg_file/\
src/axi_lite_reg_file.vhd

        The wrapper will set the correct generics and will use record types for ``regs_up`` and
        ``regs_down``.
        This makes it very easy-to-use and saves a lot of manual conversion.

        Note that the ``regs_up`` port is only available if there are any registers of a type where
        fabric gives a value to the bus.
        For example a "Read" register.
        If instead, for example, there are only "Write" registers, the ``regs_up`` port will not be
        available and the type for it is not available in the VHDL package.

        Same, but vice versa, for the ``regs_down`` port.
        Will only be available if there are any registers of a type where the bus provides a
        value to the fabric, e.g. "Read, Write".

        Similar concept for the ``reg_was_read`` and ``reg_was_written`` ports.
        They are only present if there are any readable/writable registers in the register map.

        Arguments:
          register_objects: Registers and register arrays to be included.
        Returns:
            str: VHDL code.
        """
        # Remove the trailing newline, so we can have a comment separator directly after.
        generated_header = self._header()[:-1]

        entity_name = f"{self.module_name}_reg_file"

        has_any_up_register = self._has_any_up_registers(register_objects=register_objects)
        has_any_down_register = self._has_any_down_registers(register_objects=register_objects)

        up_port = (
            f"    regs_up : in {self.module_name}_regs_up_t := {self.module_name}_regs_up_init;\n"
        )
        down_port = (
            f"    regs_down : out {self.module_name}_regs_down_t "
            f":= {self.module_name}_regs_down_init;\n"
        )

        was_read_port, was_written_port = self._get_was_accessed_ports(
            register_objects=register_objects
        )

        # Note that either of 'reg_was_read' or 'reg_was_written' is always present, otherwise
        # there would be no registers and we would not create this wrapper.
        # Hence it is safe to always end the 'regs_up'/'regs_down' ports with a semicolon.
        entity = f"""\
entity {entity_name} is
  port (
    clk : in std_ulogic;
    --# {{}}
    --# Register control bus
    axi_lite_m2s : in axi_lite_m2s_t;
    axi_lite_s2m : out axi_lite_s2m_t := axi_lite_s2m_init;
    --# {{}}
    -- Register values
{up_port if has_any_up_register else ""}\
{down_port if has_any_down_register else ""}\
    --# {{}}
    -- Each bit is pulsed for one cycle when the corresponding register is read/written.
{was_read_port}\
{was_written_port}\
  );
end entity;
"""

        up_conversion = """

  ------------------------------------------------------------------------------
  -- Combinatorially convert the register record to a list of SLV values that can be handled
  -- by the generic register file implementation.
  assign_regs_up : process(regs_up)
  begin
    regs_up_slv <= to_slv(regs_up);
  end process;
"""
        down_conversion = f"""

  ------------------------------------------------------------------------------
  -- Combinatorially convert the list of SLV values from the generic register file into the record
  -- we want to use in our application.
  assign_regs_down : process(regs_down_slv)
  begin
    regs_down <= to_{self.module_name}_regs_down(regs_down_slv);
  end process;
"""

        vhdl = f"""\
-- -----------------------------------------------------------------------------
-- AXI-Lite register file for the '{self.module_name}' module registers.
--
-- Is a wrapper around the generic AXI-Lite register file from hdl_modules:
-- * https://hdl-modules.com/modules/reg_file/reg_file.html#axi-lite-reg-file-vhd
-- * https://gitlab.com/hdl_modules/hdl_modules/-/blob/main/modules/reg_file/\
src/axi_lite_reg_file.vhd
--
-- Sets correct generics, and performs conversion to the easy-to-use register record types.
-- -----------------------------------------------------------------------------
{generated_header}
-- -----------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library axi;
use axi.axi_lite_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;

use work.{self.module_name}_regs_pkg.all;


{entity}
architecture a of {entity_name} is

  signal regs_up_slv, regs_down_slv : {self.module_name}_regs_t := {self.module_name}_regs_init;

begin

  ------------------------------------------------------------------------------
  -- Instantiate the generic AXI-Lite register file from
  -- * https://hdl-modules.com/modules/reg_file/reg_file.html#axi-lite-reg-file-vhd
  -- * https://gitlab.com/hdl_modules/hdl_modules/-/blob/main/modules/reg_file/\
src/axi_lite_reg_file.vhd
  axi_lite_reg_file_inst : entity reg_file.axi_lite_reg_file
    generic map (
      regs => {self.module_name}_reg_map,
      default_values => {self.module_name}_regs_init
    )
    port map(
      clk => clk,
      --
      axi_lite_m2s => axi_lite_m2s,
      axi_lite_s2m => axi_lite_s2m,
      --
      regs_up => regs_up_slv,
      regs_down => regs_down_slv,
      --
      reg_was_read => {"reg_was_read" if was_read_port else "open"},
      reg_was_written => {"reg_was_written"  if was_written_port else "open"}
    );
{up_conversion if has_any_up_register else ""}\
{down_conversion if has_any_down_register else ""}\

end architecture;
"""

        return vhdl

    def _get_was_accessed_ports(self, register_objects):
        has_any_readable = self._has_any_bus_readable_registers(register_objects=register_objects)
        has_any_writable = self._has_any_bus_writable_registers(register_objects=register_objects)

        was_accessed_port_type = f"out {self.module_name}_reg_was_accessed_t := (others => '0')"

        # If present, is always the last port so no trailing semicolon needed.
        was_written = (
            f"    reg_was_written : {was_accessed_port_type}\n" if has_any_writable else ""
        )

        was_read = f"    reg_was_read : {was_accessed_port_type}" if has_any_readable else ""
        if has_any_readable:
            was_read += ";\n" if was_written else "\n"

        return was_read, was_written
