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
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.numerical_interpretation import Signed, Unsigned

# Local folder libraries
from .vhdl_simulation_generator_common import VhdlSimulationGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class VhdlSimulationReadWritePackageGenerator(VhdlSimulationGeneratorCommon):
    """
    Generate VHDL code with register read/write procedures that simplify simulation.
    See the :ref:`generator_vhdl` article for usage details.

    * For each readable register, procedures that read the register value.
      Value can be read as:

      1. bit vector,

      2. integer, or

      3. native VHDL record type as given by :class:`.VhdlRecordPackageGenerator`.

    * For each field in each readable register, a procedure that reads the natively-typed value of
      the field.

    * For each writeable register, a procedure that writes the register value.
      Value can be written as:

      1. bit vector, or

      2. native VHDL record type as given by :class:`.VhdlRecordPackageGenerator`.

    * For each field in each writeable register, a procedure that writes a given
      natively-typed field value.

    Uses VUnit Verification Component calls to create bus read/write operations.

    The generated VHDL file needs also the generated packages from
    :class:`.VhdlRegisterPackageGenerator` and :class:`.VhdlRecordPackageGenerator`.
    """

    __version__ = "1.1.0"

    SHORT_DESCRIPTION = "VHDL simulation read/write package"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_register_read_write_pkg.vhd"

    def create(self, **kwargs: Any) -> Path:
        """
        See super class for API details.

        Overloaded here because this package file shall only be created if the register list
        actually has any registers.
        """
        return self._create_if_there_are_registers_otherwise_delete_file(**kwargs)

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a package with methods for reading/writing registers.
        """
        package_name = self.output_file.stem

        vhdl = f"""\
{self.header}
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

library vunit_lib;
use vunit_lib.bus_master_pkg.bus_master_t;
use vunit_lib.bus_master_pkg.read_bus;
use vunit_lib.bus_master_pkg.write_bus;
use vunit_lib.com_types_pkg.network_t;

library common;
use common.addr_pkg.addr_t;
use common.addr_pkg.addr_width;

library reg_file;
use reg_file.reg_file_pkg.reg_t;
use reg_file.reg_file_pkg.reg_width;
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

        for register, register_array in self.iterate_registers():
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )
            declarations = []

            if register.mode.software_can_read:
                # Read the register as a plain SLV.
                signature = self._register_read_write_signature(
                    is_read_not_write=True,
                    register=register,
                    register_array=register_array,
                    value_type="reg_t",
                )
                declarations.append(f"{signature};\n")

                # Read the register as a plain SLV casted to integer.
                signature = self._register_read_write_signature(
                    is_read_not_write=True,
                    register=register,
                    register_array=register_array,
                    value_type="integer",
                )
                declarations.append(f"{signature};\n")

                if register.fields:
                    # Read the register as a record.
                    signature = self._register_read_write_signature(
                        is_read_not_write=True,
                        register=register,
                        register_array=register_array,
                        value_type=f"{register_name}_t",
                    )
                    declarations.append(f"{signature};\n")

                for field in register.fields:
                    # Read the field as its native type.
                    value_type = self.field_type_name(
                        register=register, register_array=register_array, field=field
                    )
                    signature = self._field_read_write_signature(
                        is_read_not_write=True,
                        register=register,
                        register_array=register_array,
                        field=field,
                        value_type=value_type,
                    )
                    declarations.append(f"{signature};\n")

                    if self._should_be_able_to_access_field_as_integer(field=field):
                        # Read the field casted to an integer.
                        signature = self._field_read_write_signature(
                            is_read_not_write=True,
                            register=register,
                            register_array=register_array,
                            field=field,
                            value_type="integer",
                        )
                        declarations.append(f"{signature};\n")

            if register.mode.software_can_write:
                # Write the register as an integer.
                signature = self._register_read_write_signature(
                    is_read_not_write=False,
                    register=register,
                    register_array=register_array,
                    value_type="integer",
                )
                declarations.append(f"{signature};\n")

                if register.fields:
                    # Write the register as a record.
                    signature = self._register_read_write_signature(
                        is_read_not_write=False,
                        register=register,
                        register_array=register_array,
                        value_type=f"{register_name}_t",
                    )
                    declarations.append(f"{signature};\n")
                else:
                    # Write the register as a plain SLV.
                    # This one is made available only if there are no fields.
                    # This is because there can be a signature ambiguity if both are available
                    # that some compilers can not resolve.
                    # Namely e.g. value=>(field_name => '1').
                    # Where the field is a std_logic.
                    # GHDL gets confused in this case between using the signature with the record
                    # or the one with SLV.
                    signature = self._register_read_write_signature(
                        is_read_not_write=False,
                        register=register,
                        register_array=register_array,
                        value_type="reg_t",
                    )
                    declarations.append(f"{signature};\n")

                for field in register.fields:
                    # Write the field as its native type.
                    value_type = self.field_type_name(
                        register=register, register_array=register_array, field=field
                    )
                    signature = self._field_read_write_signature(
                        is_read_not_write=False,
                        register=register,
                        register_array=register_array,
                        field=field,
                        value_type=value_type,
                    )
                    declarations.append(f"{signature};\n")

                    if self._should_be_able_to_access_field_as_integer(field=field):
                        # Write the field casted to an integer.
                        signature = self._field_read_write_signature(
                            is_read_not_write=False,
                            register=register,
                            register_array=register_array,
                            field=field,
                            value_type="integer",
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
        value_type: str,
    ) -> str:
        """
        Get signature for a 'read_reg'/'write_reg' procedure.
        """
        direction = "read" if is_read_not_write else "write"
        value_direction = "out" if is_read_not_write else "in"

        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        # If it is not either of these, then it is the native type which shall not have a comment
        # since it is the default.
        type_comment = (
            " as a plain 'reg_t'"
            if value_type == "reg_t"
            else " as an 'integer'" if value_type == "integer" else ""
        )

        return f"""\
  -- {direction.capitalize()} the {register_description}{type_comment}.
  procedure {direction}_{register_name}(
    signal net : inout network_t;
{self.get_array_index_port(register_array=register_array)}\
    value : {value_direction} {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master
  )\
"""

    def _field_read_write_signature(
        self,
        is_read_not_write: bool,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        value_type: str,
    ) -> str:
        """
        Get signature for a 'read_field'/'write_field' procedure.
        """
        direction = "read" if is_read_not_write else "write"

        field_name = self.qualified_field_name(
            register=register, register_array=register_array, field=field
        )
        field_description = self.field_description(
            register=register, field=field, register_array=register_array
        )
        # If its not integer, then it is the native type which shall shall not have a comment
        # since it is the default.
        type_comment = " as an 'integer'" if value_type == "integer" else ""

        comment = ""
        if not is_read_not_write:
            if self.field_setter_should_read_modify_write(register=register):
                comment = (
                    "  -- Will read-modify-write the register to set the field to the "
                    "supplied 'value'.\n"
                )
            else:
                comment = (
                    "  -- Will write the whole register, with the field set to the \n"
                    "  -- supplied 'value' and everything else set to default.\n"
                )

        value_direction = "out" if is_read_not_write else "in"

        return f"""\
  -- {direction.capitalize()} the {field_description}{type_comment}.
{comment}\
  procedure {direction}_{field_name}(
    signal net : inout network_t;
{self.get_array_index_port(register_array=register_array)}\
    value : {value_direction} {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master
  )\
"""

    @staticmethod
    def _should_be_able_to_access_field_as_integer(field: "RegisterField") -> bool:
        """
        Return True if the field is of a type where there should be procedures to read/write it
        casted as an integer.
        """
        return isinstance(field, BitVector) and isinstance(
            field.numerical_interpretation, (Signed, Unsigned)
        )

    def _implementations(self) -> str:
        """
        Get implementations of all procedures.
        """
        separator = self.get_separator_line(indent=2)
        vhdl = ""

        for register, register_array in self.iterate_registers():
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )
            implementations = []

            if register.mode.software_can_read:
                # Read the register as a plain SLV.
                implementations.append(
                    self._register_read_implementation(
                        register=register,
                        register_array=register_array,
                        value_type="reg_t",
                        value_conversion="reg_value",
                    )
                )

                # Read the register as a plain SLV casted to integer.
                implementations.append(
                    self._register_read_implementation(
                        register=register,
                        register_array=register_array,
                        value_type="integer",
                        value_conversion="to_integer(unsigned(reg_value))",
                    )
                )

                if register.fields:
                    # Read the register as a record.
                    implementations.append(
                        self._register_read_implementation(
                            register=register,
                            register_array=register_array,
                            value_type=f"{register_name}_t",
                            value_conversion=f"to_{register_name}(reg_value)",
                        )
                    )

                for field in register.fields:
                    # Read the field as its native type.
                    value_type = self.field_type_name(
                        register=register, register_array=register_array, field=field
                    )
                    implementations.append(
                        self._field_read_implementation(
                            register=register,
                            register_array=register_array,
                            field=field,
                            value_type=value_type,
                            value_conversion=f"reg_value.{field.name}",
                        )
                    )

                    if self._should_be_able_to_access_field_as_integer(field=field):
                        # Read the field casted to an integer.
                        implementations.append(
                            self._field_read_implementation(
                                register=register,
                                register_array=register_array,
                                field=field,
                                value_type="integer",
                                value_conversion=f"to_integer(reg_value.{field.name})",
                            )
                        )

            if register.mode.software_can_write:
                # Write the register as an integer.
                implementations.append(
                    self._register_write_implementation(
                        register=register,
                        register_array=register_array,
                        value_type="integer",
                        value_conversion="std_ulogic_vector(to_unsigned(value, reg_width))",
                    )
                )

                if register.fields:
                    # Write the register as a record.
                    implementations.append(
                        self._register_write_implementation(
                            register=register,
                            register_array=register_array,
                            value_type=f"{register_name}_t",
                            value_conversion="to_slv(value)",
                        )
                    )
                else:
                    # Write the register as a plain SLV.
                    # Only if there are no fields.
                    # See the signatures method for more info.
                    implementations.append(
                        self._register_write_implementation(
                            register=register,
                            register_array=register_array,
                            value_type="reg_t",
                            value_conversion="value",
                        )
                    )

                for field in register.fields:
                    # Write the field as its native type.
                    value_type = self.field_type_name(
                        register=register, register_array=register_array, field=field
                    )
                    implementations.append(
                        self._field_write_implementation(
                            register=register,
                            register_array=register_array,
                            field=field,
                            value_type=value_type,
                        )
                    )

                    if self._should_be_able_to_access_field_as_integer(field=field):
                        # Read the field casted to an integer.
                        implementations.append(
                            self._field_write_implementation(
                                register=register,
                                register_array=register_array,
                                field=field,
                                value_type="integer",
                            )
                        )

            vhdl += separator
            vhdl += "\n".join(implementations)
            vhdl += separator
            vhdl += "\n"

        return vhdl

    def _register_read_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        value_type: str,
        value_conversion: str,
    ) -> str:
        """
        Get implementation for a 'read_reg' procedure.
        """
        signature = self._register_read_write_signature(
            is_read_not_write=True,
            register=register,
            register_array=register_array,
            value_type=value_type,
        )

        return f"""\
{signature} is
{self.reg_index_constant(register=register, register_array=register_array)}\
{self.reg_address_constant()}\
    variable reg_value : reg_t := (others => '0');
  begin
    read_bus(
      net => net,
      bus_handle => bus_handle,
      address => std_logic_vector(reg_address),
      data => reg_value
    );
    value := {value_conversion};
  end procedure;
"""

    def _register_write_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        value_type: str,
        value_conversion: str,
    ) -> str:
        """
        Get implementation for a 'write_reg' procedure.
        """
        signature = self._register_read_write_signature(
            is_read_not_write=False,
            register=register,
            register_array=register_array,
            value_type=value_type,
        )

        return f"""\
{signature} is
{self.reg_index_constant(register=register, register_array=register_array)}\
{self.reg_address_constant()}\
    constant reg_value : reg_t := {value_conversion};
  begin
    write_bus(
      net => net,
      bus_handle => bus_handle,
      address => std_logic_vector(reg_address),
      data => reg_value
    );
  end procedure;
"""

    def _field_read_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        value_type: str,
        value_conversion: str,
    ) -> str:
        """
        Get implementation for a 'read_field' procedure.
        """
        signature = self._field_read_write_signature(
            is_read_not_write=True,
            register=register,
            register_array=register_array,
            field=field,
            value_type=value_type,
        )

        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )

        return f"""\
{signature} is
    variable reg_value : {register_name}_t := {register_name}_init;
  begin
    read_{register_name}(
      net => net,
{self.get_array_index_association(register_array=register_array)}\
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
    value := {value_conversion};
  end procedure;
"""

    def _field_write_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        value_type: str,
    ) -> str:
        """
        Get implementation for a 'write_field' procedure.
        """
        signature = self._field_read_write_signature(
            is_read_not_write=False,
            register=register,
            register_array=register_array,
            field=field,
            value_type=value_type,
        )
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )

        if self.field_setter_should_read_modify_write(register=register):
            set_base_value = f"""\
    read_{register_name}(
      net => net,
{self.get_array_index_association(register_array=register_array)}\
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
"""
        else:
            set_base_value = ""

        if value_type == "integer":
            field_name = self.qualified_field_name(
                register=register, register_array=register_array, field=field
            )
            field_width = f"{field_name}_width"

            if isinstance(field, BitVector) and isinstance(
                field.numerical_interpretation, Unsigned
            ):
                field_conversion = f"to_unsigned(value, {field_width})"
            elif isinstance(field, BitVector) and isinstance(
                field.numerical_interpretation, Signed
            ):
                field_conversion = f"to_signed(value, {field_width})"
            else:
                raise ValueError(f"Should not end up here for field: {field}")
        else:
            field_conversion = "value"

        return f"""\
{signature} is
    variable reg_value : {register_name}_t := {register_name}_init;
  begin
{set_base_value}\
    reg_value.{field.name} := {field_conversion};

    write_{register_name}(
      net => net,
{self.get_array_index_association(register_array=register_array)}\
      value => reg_value,
      base_address => base_address,
      bus_handle => bus_handle
    );
  end procedure;
"""
