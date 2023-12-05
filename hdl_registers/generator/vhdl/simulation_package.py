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

# Local folder libraries
from .vhdl_generator_common import VhdlGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class VhdlSimulationPackageGenerator(VhdlGeneratorCommon):
    """
    Generate code that simplifies simulation of a register map.
    Uses the VHDL record types for register read/write values.

    * For each readable register

      * a procedure that reads the register and converts the value to the natively typed record.
      * a procedure that waits until the register assumes a given natively typed record value.

    * For each field in each readable register

      * a procedure that reads the natively-typed value of the field.
      * a procedure that waits until the field assumes a given natively typed value.

    * For each writeable register, a procedure that writes a given natively typed record value.

    * For each field in each writeable register, a procedure that writes a given field value.

    Uses VUnit Verification Component calls, via :ref:`reg_file.reg_operations_pkg`
    from hdl_modules.

    The generated VHDL file needs also the generated packages from
    :class:`.VhdlRegisterPackageGenerator` and :class:`.VhdlRecordPackageGenerator`.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "VHDL simulation package"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_register_simulation_pkg.vhd"

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a package with methods for reading/writing registers.

        Arguments:
          register_objects: Registers and register arrays to be included.
        Return:
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

    def _declarations(self) -> str:
        """
        Get procedure declarations for all procedures.
        """
        separator = self.get_separator_line(indent=2)
        vhdl = ""

        for register, register_array in self.iterate_registers():
            declarations = []

            if register.is_bus_readable:
                signature = self._register_read_write_signature(
                    is_read_not_write=True, register=register, register_array=register_array
                )
                declarations.append(f"{signature};\n")

                signature = self._register_wait_until_equals_signature(
                    register=register, register_array=register_array
                )
                declarations.append(f"{signature};\n")

                for field in register.fields:
                    signature = self._field_read_write_signature(
                        is_read_not_write=True,
                        register=register,
                        register_array=register_array,
                        field=field,
                    )
                    declarations.append(f"{signature};\n")

                    signature = self._field_wait_until_equals_signature(
                        register=register, register_array=register_array, field=field
                    )
                    declarations.append(f"{signature};\n")

            if register.is_bus_writeable:
                signature = self._register_read_write_signature(
                    is_read_not_write=False, register=register, register_array=register_array
                )
                declarations.append(f"{signature};\n")

                for field in register.fields:
                    signature = self._field_read_write_signature(
                        is_read_not_write=False,
                        register=register,
                        register_array=register_array,
                        field=field,
                    )
                    declarations.append(f"{signature};\n")

            vhdl += separator
            vhdl += "\n".join(declarations)
            vhdl += separator
            vhdl += "\n"

        return vhdl

    def _register_read_write_signature(
        self,
        is_read_not_write: bool,
        register: "Register",
        register_array: Optional["RegisterArray"],
    ) -> str:
        """
        Get signature for a 'read_reg'/'write_reg' procedure.
        """
        direction = "read" if is_read_not_write else "write"

        register_name = self.register_name(register=register, register_array=register_array)
        register_description = self.register_description(
            register=register, register_array=register_array
        )

        value_direction = "out" if is_read_not_write else "in"
        value_type = f"{register_name}_t" if register.fields else "reg_t"

        if register_array:
            array_name = self.register_array_name(register_array=register_array)
            array_index_port = f"    array_index : in {array_name}_range;\n"
        else:
            array_index_port = ""

        return f"""\
  -- {direction.capitalize()} the {register_description}.
  procedure {direction}_{register_name}(
    signal net : inout network_t;
{array_index_port}\
    value : {value_direction} {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master
  )\
"""

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

        if register_array:
            array_name = self.register_array_name(register_array=register_array)
            array_index_port = f"    array_index : in {array_name}_range;\n"
        else:
            array_index_port = ""

        return f"""\
  -- Wait until the {register_description} equals the given 'value'.
{slv_comment}\
  procedure wait_until_{register_name}_equals(
    signal net : inout network_t;
{array_index_port}\
    value : in {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master;
    timeout : delay_length := max_timeout;
    message : string := ""
  )\
"""

    def _field_read_write_signature(
        self,
        is_read_not_write: bool,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get signature for a 'read_field'/'write_field' procedure.
        """
        direction = "read" if is_read_not_write else "write"

        field_name = self.field_name(register=register, register_array=register_array, field=field)
        field_description = self.field_description(
            register=register, field=field, register_array=register_array
        )

        comment = ""
        if not is_read_not_write:
            if self._can_read_modify_write_register(register=register):
                comment = (
                    "  -- Will read-modify-write the register to set the field to the "
                    "supplied 'value'.\n"
                )
            else:
                comment = (
                    "  -- Will write the whole register, with the field set to the \n"
                    "  -- supplied 'value' and all other fields to their default values.\n"
                )

        value_direction = "out" if is_read_not_write else "in"
        value_type = self.field_type_name(
            register=register, register_array=register_array, field=field
        )

        if register_array:
            array_name = self.register_array_name(register_array=register_array)
            array_index_port = f"    array_index : in {array_name}_range;\n"
        else:
            array_index_port = ""

        return f"""\
  -- {direction.capitalize()} the {field_description}.
{comment}\
  procedure {direction}_{field_name}(
    signal net : inout network_t;
{array_index_port}\
    value : {value_direction} {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master
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

        if register_array:
            array_name = self.register_array_name(register_array=register_array)
            array_index_port = f"    array_index : in {array_name}_range;\n"
        else:
            array_index_port = ""

        return f"""\
  -- Wait until the {field_description} equals the given 'value'.
  procedure wait_until_{field_name}_equals(
    signal net : inout network_t;
{array_index_port}\
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

        for register, register_array in self.iterate_registers():
            implementations = []

            if register.is_bus_readable:
                implementations.append(
                    self._register_read_implementation(
                        register=register, register_array=register_array
                    )
                )

                implementations.append(
                    self._register_wait_until_equals_implementation(
                        register=register, register_array=register_array
                    )
                )

                for field in register.fields:
                    implementations.append(
                        self._field_read_implementation(
                            register=register, register_array=register_array, field=field
                        )
                    )

                    implementations.append(
                        self._field_wait_until_equals_implementation(
                            register=register, register_array=register_array, field=field
                        )
                    )

            if register.is_bus_writeable:
                implementations.append(
                    self._register_write_implementation(
                        register=register, register_array=register_array
                    )
                )

                for field in register.fields:
                    implementations.append(
                        self._field_write_implementation(
                            register=register, register_array=register_array, field=field
                        )
                    )

            vhdl += separator
            vhdl += "\n".join(implementations)
            vhdl += separator
            vhdl += "\n"

        return vhdl

    def _register_read_implementation(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get implementation for a 'read_reg' procedure.
        """
        signature = self._register_read_write_signature(
            is_read_not_write=True, register=register, register_array=register_array
        )
        reg_index = self._reg_index_constant(register=register, register_array=register_array)

        register_name = self.register_name(register=register, register_array=register_array)
        conversion = f"to_{register_name}(reg_value)" if register.fields else "reg_value"

        return f"""\
{signature} is
{reg_index}\
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

    def _reg_index_constant(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get 'reg_index' constant declaration suitable for implementation of procedures.
        """
        register_name = self.register_name(register=register, register_array=register_array)
        reg_index = (
            f"{register_name}(array_index=>array_index)" if register_array else register_name
        )

        return f"    constant reg_index : {self.name}_reg_range := {reg_index};\n"

    def _register_write_implementation(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get implementation for a 'write_reg' procedure.
        """
        signature = self._register_read_write_signature(
            is_read_not_write=False, register=register, register_array=register_array
        )
        reg_index = self._reg_index_constant(register=register, register_array=register_array)

        conversion = "to_slv(value)" if register.fields else "value"

        return f"""\
{signature} is
{reg_index}\
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
        reg_index = self._reg_index_constant(register=register, register_array=register_array)

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

    def _field_read_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get implementation for a 'read_field' procedure.
        """
        signature = self._field_read_write_signature(
            is_read_not_write=True, register=register, register_array=register_array, field=field
        )

        register_name = self.register_name(register=register, register_array=register_array)

        array_index_association = "      array_index => array_index,\n" if register_array else ""

        return f"""\
{signature} is
    variable reg_value : {register_name}_t := {register_name}_init;
  begin
    read_{register_name}(
      net => net,
{array_index_association}\
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
    value := reg_value.{field.name};
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

    def _field_write_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get implementation for a 'write_field' procedure.
        """
        signature = self._field_read_write_signature(
            is_read_not_write=False, register=register, register_array=register_array, field=field
        )
        register_name = self.register_name(register=register, register_array=register_array)

        array_index_association = "      array_index => array_index,\n" if register_array else ""

        if self._can_read_modify_write_register(register=register):
            set_base_value = f"""\
    read_{register_name}(
      net => net,
{array_index_association}\
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
"""
        else:
            set_base_value = ""

        return f"""\
{signature} is
    variable reg_value : {register_name}_t := {register_name}_init;
  begin
{set_base_value}\
    reg_value.{field.name} := value;

    write_{register_name}(
      net => net,
{array_index_association}\
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
  end procedure;
"""

    @staticmethod
    def _can_read_modify_write_register(register: "Register") -> bool:
        """
        Return true if the register is of a writeable type where the bus can also read back
        a previously-written value.
        """
        if register.mode == "r_w":
            return True

        if register.mode in ["w", "wpulse", "r_wpulse"]:
            return False

        raise ValueError(f"Got non-writeable register: {register}")

    def create(self, **kwargs: Any) -> None:
        """
        See super class for API details.

        Overloaded here because this package file shall only be created if the register list
        actually has any registers.
        If not, if for example the user has a register list with only constants, we do not want
        to flood the file system with unnecessary files.
        The package would be empty anyway.

        If the artifact file exists from a previous run, we delete it since we do not want stray
        files laying around and we do not want to give the false impression that this file is being
        actively generated.
        """
        if self.register_list.register_objects:
            super().create(**kwargs)
        else:
            self._delete_output_file_if_exists()
