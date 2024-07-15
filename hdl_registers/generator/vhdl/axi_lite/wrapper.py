# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import Any

# First party libraries
from hdl_registers.generator.vhdl.vhdl_generator_common import VhdlGeneratorCommon
from hdl_registers.register_mode import HardwareAccessDirection, SoftwareAccessDirection


class VhdlAxiLiteWrapperGenerator(VhdlGeneratorCommon):
    """
    Generate a VHDL wrapper around a generic AXI-Lite register file with correct generics and ports.
    See the :ref:`generator_vhdl` article for usage details.

    The wrapper will set the correct generics and will use record types for ``regs_up`` and
    ``regs_down``.
    This makes it very easy-to-use and saves a lot of manual conversion.

    It wraps the following VHDL file:

    * https://hdl-modules.com/modules/reg_file/reg_file.html#axi-lite-reg-file-vhd
    * https://github.com/hdl-modules/hdl-modules/blob/main/modules/reg_file/src/\
axi_lite_reg_file.vhd

    It also requires the generated packages from
    :class:`.VhdlRegisterPackageGenerator` and :class:`.VhdlRecordPackageGenerator`.

    Note that the ``regs_up`` port is only available if there are any registers of a type where
    hardware gives a value to the bus.
    For example a "Read" register.
    If instead, for example, there are only "Write" registers, the ``regs_up`` port will not be
    available and the type for it is not available in the VHDL package.

    Same, but vice versa, for the ``regs_down`` port.
    Will only be available if there are any registers of a type where the bus provides a
    value to the hardware, e.g. "Read, Write".

    Similar concept for the ``reg_was_read`` and ``reg_was_written`` ports.
    They are only present if there are any readable/writeable registers in the register map.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "VHDL AXI-Lite register file"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_reg_file.vhd"

    def create(self, **kwargs: Any) -> Path:
        """
        See super class for API details.

        Overloaded here because this file shall only be created if the register list
        actually has any registers.
        """
        return self._create_if_there_are_registers_otherwise_delete_file(**kwargs)

    def get_code(self, **kwargs: Any) -> str:
        """
        Get VHDL code for a wrapper around the generic AXi_lite register file from hdl-modules:
        """
        entity_name = self.output_file.stem

        up_port = f"    regs_up : in {self.name}_regs_up_t := {self.name}_regs_up_init;\n"
        has_any_up = self.has_any_hardware_accessible_register(HardwareAccessDirection.UP)

        down_port = (
            f"    regs_down : out {self.name}_regs_down_t " f":= {self.name}_regs_down_init;\n"
        )
        has_any_down = self.has_any_hardware_accessible_register(HardwareAccessDirection.DOWN)

        was_read_port, was_written_port = self._get_was_accessed_ports()

        # Note that either of 'reg_was_read' or 'reg_was_written' is always present, otherwise
        # there would be no registers and we would not create this wrapper.
        # Hence it is safe to always end the 'regs_up'/'regs_down' ports with a semicolon.
        entity = f"""\
entity {entity_name} is
  port (
    clk : in std_ulogic;
    --# {{}}
    --# Register control bus.
    axi_lite_m2s : in axi_lite_m2s_t;
    axi_lite_s2m : out axi_lite_s2m_t := axi_lite_s2m_init;
    --# {{}}
    -- Register values.
{up_port if has_any_up else ""}\
{down_port if has_any_down else ""}\
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
    regs_down <= to_{self.name}_regs_down(regs_down_slv);
  end process;
"""

        was_read_conversion = f"""

  ------------------------------------------------------------------------------
  -- Combinatorially convert status mask to a record where only the applicable registers \
are present.
  assign_reg_was_read : process(reg_was_read_slv)
  begin
    reg_was_read <= to_{self.name}_reg_was_read(reg_was_read_slv);
  end process;
"""

        was_written_conversion = f"""

  ------------------------------------------------------------------------------
  -- Combinatorially convert status mask to a record where only the applicable registers \
are present.
  assign_reg_was_written : process(reg_was_written_slv)
  begin
    reg_was_written <= to_{self.name}_reg_was_written(reg_was_written_slv);
  end process;
"""

        vhdl = f"""\
-- -----------------------------------------------------------------------------
-- AXI-Lite register file for the '{self.name}' module registers.
--
-- Is a wrapper around the generic AXI-Lite register file from hdl-modules:
-- * https://hdl-modules.com/modules/reg_file/reg_file.html#axi-lite-reg-file-vhd
-- * https://github.com/hdl-modules/hdl-modules/blob/main/modules/reg_file/src/axi_lite_reg_file.vhd
--
-- Sets correct generics, and performs conversion to the easy-to-use register record types.
-- -----------------------------------------------------------------------------
{self.header}\
-- -----------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

library axi_lite;
use axi_lite.axi_lite_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;

use work.{self.name}_regs_pkg.all;
use work.{self.name}_register_record_pkg.all;


{entity}
architecture a of {entity_name} is

  signal regs_up_slv, regs_down_slv : {self.name}_regs_t := {self.name}_regs_init;

  signal reg_was_read_slv, reg_was_written_slv : {self.name}_reg_was_accessed_t := (
    others => '0'
  );

begin

  ------------------------------------------------------------------------------
  -- Instantiate the generic AXI-Lite register file from
  -- * https://hdl-modules.com/modules/reg_file/reg_file.html#axi-lite-reg-file-vhd
  -- * https://github.com/hdl-modules/hdl-modules/blob/main/modules/reg_file/src/\
axi_lite_reg_file.vhd
  axi_lite_reg_file_inst : entity reg_file.axi_lite_reg_file
    generic map (
      regs => {self.name}_reg_map,
      default_values => {self.name}_regs_init
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
      reg_was_read => reg_was_read_slv,
      reg_was_written => reg_was_written_slv
    );
{up_conversion if has_any_up else ""}\
{down_conversion if has_any_down else ""}\
{was_read_conversion if was_read_port else ""}\
{was_written_conversion if was_written_port else ""}\

end architecture;
"""

        return vhdl

    def _get_was_accessed_ports(self) -> tuple[str, str]:
        has_any_read = self.has_any_software_accessible_register(
            direction=SoftwareAccessDirection.READ
        )
        has_any_write = self.has_any_software_accessible_register(
            direction=SoftwareAccessDirection.WRITE
        )

        # If present, is always the last port so no trailing semicolon needed.
        was_written = (
            (
                f"    reg_was_written : out {self.name}_reg_was_written_t := "
                f"{self.name}_reg_was_written_init\n"
            )
            if has_any_write
            else ""
        )

        was_read = (
            (
                f"    reg_was_read : out {self.name}_reg_was_read_t := "
                f"{self.name}_reg_was_read_init"
            )
            if has_any_read
            else ""
        )

        if has_any_read:
            was_read += ";\n" if was_written else "\n"

        return was_read, was_written
