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
from typing import TYPE_CHECKING, Any, Optional

# First party libraries
from hdl_registers.generator.vhdl.vhdl_generator_common import BUS_ACCESS_DIRECTIONS

# Local folder libraries
from .vhdl_simulation_generator_common import VhdlSimulationGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class VhdlSimulationWaitUntilPackageGenerator(VhdlSimulationGeneratorCommon):
    """
    Generate VHDL code with ``wait_until_X_equals`` procedures that simplify simulation.
    See the :ref:`generator_vhdl` article for usage details.

    * For each readable register, a procedure that waits until the register assumes a
      given natively-typed record value.

    * For each field in each readable register, a procedure that waits until the field assumes a
      given natively-typed value.

    Uses VUnit Verification Component calls, via :ref:`reg_file.reg_operations_pkg`
    from hdl_modules.

    The generated VHDL file needs also the generated packages from
    :class:`.VhdlRegisterPackageGenerator` and :class:`.VhdlRecordPackageGenerator`.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "VHDL simulation wait until package"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_register_wait_until_pkg.vhd"

    def create(self, **kwargs: Any) -> None:
        """
        See super class for API details.

        Overloaded here because this package file shall only be created if the register list
        actually has any registers.
        """
        self._create_if_there_are_registers_otherwise_delete_file(**kwargs)

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a package with ``wait_until_X_equals`` methods for registers/fields.
        """
        package_name = self.output_file.stem

        vhdl = f"""\
{self.header}
library ieee;
use ieee.fixed_pkg.all;
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

    def _declarations(self) -> str:
        """
        Get procedure declarations for all procedures.
        """
        separator = self.get_separator_line(indent=2)
        vhdl = ""

        for register, register_array in self.iterate_bus_accessible_registers(
            direction=BUS_ACCESS_DIRECTIONS["read"]
        ):
            declarations = []

            signature = self._register_wait_until_equals_signature(
                register=register, register_array=register_array
            )
            declarations.append(f"{signature};\n")

            for field in register.fields:
                signature = self._field_wait_until_equals_signature(
                    register=register, register_array=register_array, field=field
                )
                declarations.append(f"{signature};\n")

            vhdl += separator
            vhdl += "\n".join(declarations)
            vhdl += separator
            vhdl += "\n"

        return vhdl

    def _register_wait_until_equals_signature(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get signature for a 'wait_until_reg_equals' procedure.
        """
        register_name = self.register_name(register=register, register_array=register_array)
        register_description = self.register_description(
            register=register, register_array=register_array
        )

        if register.fields:
            value_type = f"{register_name}_t"
            slv_comment = ""
        else:
            value_type = "reg_t"
            slv_comment = (
                "  -- Note that '-' can be used as a wildcard in 'value' since 'check_match' is \n"
                "  -- used to check for equality.\n"
            )

        return f"""\
  -- Wait until the {register_description} equals the given 'value'.
{slv_comment}\
  procedure wait_until_{register_name}_equals(
    signal net : inout network_t;
{self.get_array_index_port(register_array=register_array)}\
    value : in {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master;
    timeout : delay_length := max_timeout;
    message : string := ""
  )\
"""

    def _field_wait_until_equals_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get signature for a 'wait_until_field_equals' procedure.
        """
        field_name = self.field_name(register=register, register_array=register_array, field=field)
        field_description = self.field_description(
            register=register, register_array=register_array, field=field
        )

        value_type = self.field_type_name(
            register=register, register_array=register_array, field=field
        )

        return f"""\
  -- Wait until the {field_description} equals the given 'value'.
  procedure wait_until_{field_name}_equals(
    signal net : inout network_t;
{self.get_array_index_port(register_array=register_array)}\
    value : in {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master;
    timeout : delay_length := max_timeout;
    message : string := ""
  )\
"""

    def _implementations(self) -> str:
        """
        Get implementations of all procedures.
        """
        separator = self.get_separator_line(indent=2)
        vhdl = ""

        for register, register_array in self.iterate_bus_accessible_registers(
            direction=BUS_ACCESS_DIRECTIONS["read"]
        ):
            implementations = []

            implementations.append(
                self._register_wait_until_equals_implementation(
                    register=register, register_array=register_array
                )
            )

            for field in register.fields:
                implementations.append(
                    self._field_wait_until_equals_implementation(
                        register=register, register_array=register_array, field=field
                    )
                )

            vhdl += separator
            vhdl += "\n".join(implementations)
            vhdl += separator
            vhdl += "\n"

        return vhdl

    def _register_wait_until_equals_implementation(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get implementation for a 'wait_until_reg_equals' procedure.
        """
        signature = self._register_wait_until_equals_signature(
            register=register, register_array=register_array
        )

        conversion = "to_slv(value)" if register.fields else "value"

        return f"""\
{signature} is
    constant reg_value : reg_t := {conversion};
{self._get_wait_until_common_constants(register=register, register_array=register_array)}\
  begin
    wait_until_read_equals(
      net=>net,
      bus_handle=>bus_handle,
      addr=>std_ulogic_vector(address),
      value=>reg_value,
      timeout=>timeout,
      msg=>timeout_message
    );
  end procedure;
"""

    def _get_wait_until_common_constants(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: Optional["RegisterField"] = None,
    ) -> str:
        """
        Get constants code that is common for all 'wait_until_*_equals' procedures.
        """
        reg_index = self.reg_index_constant(register=register, register_array=register_array)

        if field:
            description = self.field_description(
                register=register, register_array=register_array, field=field
            )
        else:
            description = self.register_description(
                register=register, register_array=register_array
            )

        array_index_message = (
            '      & " - array index: " & to_string(array_index)\n' if register_array else ""
        )

        return f"""\
{reg_index}\
    constant address : addr_t := base_address or to_unsigned(4 * reg_index, addr_t'length);

    constant base_timeout_message : string := (
      "Timeout while waiting for the {description} to equal the given value."
      & " value: " & to_string(reg_value)
{array_index_message}\
      & " - register index: " & to_string(reg_index)
      & " - base address: " & to_string(base_address)
    );
    function get_timeout_message return string is
    begin
      if message = "" then
        return base_timeout_message;
      end if;

      return base_timeout_message & " - message: " & message;
    end function;
    constant timeout_message : string := get_timeout_message;
"""

    def _field_wait_until_equals_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get implementation for a 'wait_until_field_equals' procedure.
        """
        signature = self._field_wait_until_equals_signature(
            register=register, register_array=register_array, field=field
        )
        field_name = self.field_name(register=register, register_array=register_array, field=field)
        field_to_slv = self.field_to_slv(field=field, field_name=field_name, value="value")

        return f"""\
{signature} is
    constant reg_value : reg_t := (
      {field_name} => {field_to_slv},
      others => '-'
    );
{self._get_wait_until_common_constants(register=register, register_array=register_array)}\
  begin
    wait_until_read_equals(
      net=>net,
      bus_handle=>bus_handle,
      addr=>std_ulogic_vector(address),
      value=>reg_value,
      timeout=>timeout,
      msg=>timeout_message
    );
  end procedure;
"""
