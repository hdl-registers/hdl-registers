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
from hdl_registers.register_mode import SoftwareAccessDirection

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

    Uses VUnit Verification Component calls to create bus read operations.

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

    def create(self, **kwargs: Any) -> Path:
        """
        See super class for API details.

        Overloaded here because this package file shall only be created if the register list
        actually has any registers.
        """
        return self._create_if_there_are_registers_otherwise_delete_file(**kwargs)

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
use vunit_lib.bus_master_pkg.bus_master_t;
use vunit_lib.bus_master_pkg.wait_until_read_equals;
use vunit_lib.com_types_pkg.max_timeout;
use vunit_lib.com_types_pkg.network_t;
use vunit_lib.string_ops.hex_image;

library common;
use common.addr_pkg.addr_t;
use common.addr_pkg.addr_width;

library reg_file;
use reg_file.reg_file_pkg.reg_t;
use reg_file.reg_operations_pkg.regs_bus_master;

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

        for register, register_array in self.iterate_software_accessible_registers(
            direction=SoftwareAccessDirection.READ
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
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
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
        field_name = self.qualified_field_name(
            register=register, register_array=register_array, field=field
        )
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

        for register, register_array in self.iterate_software_accessible_registers(
            direction=SoftwareAccessDirection.READ
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

{self._get_common_constants(register=register, register_array=register_array, field=None)}\
  begin
    wait_until_read_equals(
      net => net,
      bus_handle => bus_handle,
      addr => std_ulogic_vector(reg_address),
      value => reg_value,
      timeout => timeout,
      msg => get_message
    );
  end procedure;
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
        field_name = self.qualified_field_name(
            register=register, register_array=register_array, field=field
        )
        field_to_slv = self.field_to_slv(field=field, field_name=field_name, value="value")

        return f"""\
{signature} is
    constant reg_value : reg_t := (
      {field_name} => {field_to_slv},
      others => '-'
    );

{self._get_common_constants(register=register, register_array=register_array, field=field)}\
  begin
    wait_until_read_equals(
      net => net,
      bus_handle => bus_handle,
      addr => std_ulogic_vector(reg_address),
      value => reg_value,
      timeout => timeout,
      msg => get_message
    );
  end procedure;
"""

    def _get_common_constants(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: Optional["RegisterField"],
    ) -> str:
        """
        Get constants code that is common for all 'wait_until_*_equals' procedures.
        """
        if field:
            field_description = f" the '{field.name}' field in"
        else:
            field_description = ""

        return f"""\
{self.reg_index_constant(register=register, register_array=register_array)}\
{self.reg_address_constant()}\

{self.get_register_array_message(register_array=register_array)}\
{self.get_base_address_message()}\
    constant base_message : string := (
      "Timeout while waiting for{field_description} the '{register.name}' register"
      & register_array_message
      & base_address_message
      & " to equal the given value: "
      & to_string(reg_value)
      & "."
    );
{self.get_message()}\
"""
