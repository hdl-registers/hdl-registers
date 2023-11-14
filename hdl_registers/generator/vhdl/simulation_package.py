# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .vhdl_generator_common import VhdlGeneratorCommon


class VhdlSimulationPackageGenerator(VhdlGeneratorCommon):
    """
    Generate code that simplifies simulation of a register map.
    """

    SHORT_DESCRIPTION = "VHDL simulation package"

    @property
    def output_file(self):
        return self.output_folder / f"{self.name}_register_simulation_pkg.vhd"

    def get_code(self, **kwargs):
        """
        Get a package with methods for reading/writing registers.
        Uses the VHDL record types for register read/write values.

        Uses VUnit Verification Component calls, via :ref:`reg_file.reg_operations_pkg`
        from hdl_modules.

        Arguments:
          register_objects: Registers and register arrays to be included.
        Returns:
            str: VHDL code.
        """
        package_name = self.output_file.stem

        vhdl = f"""\
{self.header}
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library vunit_lib;
context vunit_lib.vc_context;

library common;
use common.addr_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;
use reg_file.reg_operations_pkg.all;

use work.{self.name}_regs_pkg.all;
use work.{self.name}_register_record_pkg.all;


package {package_name} is

{self._declarations()}\
end package;

package body {package_name} is

{self._implementations()}\
end package body;
"""

        return vhdl

    def _register_read_write_signature(
        self, is_read_not_write: bool, register, register_array=None
    ):
        """
        Get signature for a 'read_reg'/'write_reg' procedure.
        """
        direction = "read" if is_read_not_write else "write"
        value_direction = "out" if is_read_not_write else "in"

        register_name = self.register_name(register=register, register_array=register_array)
        value_type = f"{register_name}_t" if register.fields else "reg_t"

        if register_array:
            array_name = self.register_array_name(register_array=register_array)
            array_index_port = f"    array_index : in {array_name}_range;\n"
        else:
            array_index_port = ""

        return f"""\
  procedure {direction}_{register_name}(
    signal net : inout network_t;
{array_index_port}\
    value : {value_direction} {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master
  )"""

    def _declarations(self):
        """
        Get procedure declarations for all 'read_reg'/'write_reg' procedures.
        """
        vhdl = ""

        for register, register_array in self.iterate_registers():
            register_description = self.register_description(
                register=register, register_array=register_array
            )

            if register.is_bus_readable:
                signature = self._register_read_write_signature(
                    is_read_not_write=True, register=register, register_array=register_array
                )
                vhdl += f"""\
  -- Read the {register_description}.
{signature};

"""

            if register.is_bus_writeable:
                signature = self._register_read_write_signature(
                    is_read_not_write=False, register=register, register_array=register_array
                )
                vhdl += f"""\
  -- Write the {register_description}.
{signature};

"""

        return vhdl

    def _register_read_write_implementation_start(
        self, is_read_not_write, register, register_array
    ):
        """
        Get implementation for all 'read_reg' procedures.
        """
        signature = self._register_read_write_signature(
            is_read_not_write=is_read_not_write, register=register, register_array=register_array
        )
        register_name = self.register_name(register=register, register_array=register_array)

        reg_index = (
            f"{register_name}(array_index=>array_index)" if register_array else register_name
        )

        return f"""\
{signature} is
    constant reg_index : {self.name}_reg_range := {reg_index};\
"""

    def _register_read_implementation(self, register, register_array):
        """
        Get implementation for a 'read_reg' procedure.
        """
        start = self._register_read_write_implementation_start(
            is_read_not_write=True, register=register, register_array=register_array
        )

        register_name = self.register_name(register=register, register_array=register_array)
        conversion = f"to_{register_name}(reg_value)" if register.fields else "reg_value"

        return f"""\
{start}
    variable reg_value : reg_t := (others => '0');
  begin
    read_reg(
      net => net,
      reg_index => reg_index,
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
    value := {conversion};
  end procedure;

"""

    def _register_write_implementation(self, register, register_array):
        """
        Get implementation for a 'write_reg' procedure.
        """
        start = self._register_read_write_implementation_start(
            is_read_not_write=False, register=register, register_array=register_array
        )

        conversion = "to_slv(value)" if register.fields else "value"

        return f"""\
{start}
    constant reg_value : reg_t := {conversion};
  begin
    write_reg(
      net => net,
      reg_index => reg_index,
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
  end procedure;

"""

    def _implementations(self):
        """
        Get implementations of 'read_reg'/'write_reg' procedures.
        """
        vhdl = ""

        for register, register_array in self.iterate_registers():
            if register.is_bus_readable:
                vhdl += self._register_read_implementation(
                    register=register, register_array=register_array
                )

            if register.is_bus_writeable:
                vhdl += self._register_write_implementation(
                    register=register, register_array=register_array
                )

        return vhdl
