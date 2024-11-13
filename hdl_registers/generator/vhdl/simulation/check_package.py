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
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.numerical_interpretation import Fixed
from hdl_registers.register_mode import SoftwareAccessDirection

# Local folder libraries
from .vhdl_simulation_generator_common import VhdlSimulationGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class VhdlSimulationCheckPackageGenerator(VhdlSimulationGeneratorCommon):
    """
    Generate VHDL code with simulation procedures to check the values of registers and fields.
    See the :ref:`generator_vhdl` article for usage details.

    * For each readable register, procedures that check that the register's current value is equal
      to a given expected value.
      Expected value can be provided as

      1. bit vector,

      2. integer, or

      3. native VHDL record type as given by :class:`.VhdlRecordPackageGenerator`.

    * For each field in each readable register, a procedure that checks that the register field's
      current value is equal to a given natively-typed value.

    Uses VUnit Verification Component calls, via the procedures from
    :class:`.VhdlSimulationReadWritePackageGenerator`.

    The generated VHDL file needs also the generated packages from
    :class:`.VhdlRegisterPackageGenerator` and :class:`.VhdlRecordPackageGenerator`.
    """

    __version__ = "1.2.0"

    SHORT_DESCRIPTION = "VHDL simulation check package"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_register_check_pkg.vhd"

    def create(self, **kwargs: Any) -> Path:
        """
        See super class for API details.

        Overloaded here because this package file shall only be created if the register list
        actually has any registers.
        """
        return self._create_if_there_are_registers_otherwise_delete_file(**kwargs)

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a package with methods for checking register/field values.
        """
        package_name = self.output_file.stem

        vhdl = f"""\
{self.header}
library ieee;
use ieee.fixed_pkg.all;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

library vunit_lib;
use vunit_lib.bus_master_pkg.bus_master_t;
use vunit_lib.check_pkg.all;
use vunit_lib.checker_pkg.all;
use vunit_lib.com_types_pkg.network_t;
use vunit_lib.string_ops.hex_image;

library common;
use common.addr_pkg.addr_t;

library reg_file;
use reg_file.reg_file_pkg.reg_t;
use reg_file.reg_operations_pkg.regs_bus_master;

use work.{self.name}_register_read_write_pkg.all;
use work.{self.name}_register_record_pkg.all;
use work.{self.name}_regs_pkg.all;


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
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )
            declarations = []

            # Check the register value as a plain SLV casted to integer.
            signature = self._register_check_signature(
                register=register, register_array=register_array, value_type="integer"
            )
            declarations.append(f"{signature};\n")

            if register.fields:
                # Check the register value as a record.
                signature = self._register_check_signature(
                    register=register,
                    register_array=register_array,
                    value_type=f"{register_name}_t",
                )
                declarations.append(f"{signature};\n")
            else:
                # Check the register value as a plain SLV.
                # This one is made available only if there are no fields.
                # This is because there can be a signature ambiguity if both are available
                # that some compilers can not resolve.
                # Namely e.g. value=>(field_name => '1').
                # Where the field is a std_logic.
                # GHDL gets confused in this case between using the signature with the record
                # or the one with SLV.
                signature = self._register_check_signature(
                    register=register, register_array=register_array, value_type="reg_t"
                )
                declarations.append(f"{signature};\n")

            for field in register.fields:
                # Check the value of each field.
                signature = self._field_check_signature(
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

    def _register_check_signature(
        self, register: "Register", register_array: Optional["RegisterArray"], value_type: str
    ) -> str:
        """
        Get signature for a 'check_X_equal' procedure for register values.
        """
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        # If it is not either of these, then it is the native type which shall not have a comment
        # since it is the default.
        type_comment = (
            " as a plain SLV"
            if value_type == "reg_t"
            else " as a plain SLV casted to integer" if value_type == "integer" else ""
        )

        return f"""\
  -- Check that the current value of the {register_description}
  -- equals the given 'expected' value{type_comment}.
  procedure check_{register_name}_equal(
    signal net : inout network_t;
{self.get_array_index_port(register_array=register_array)}\
    expected : in {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master;
    message : in string := ""
  )\
"""

    def _field_check_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get signature for a 'check_X_equal' procedure for field values.
        """
        value_type = self.field_type_name(
            register=register, register_array=register_array, field=field
        )

        field_name = self.qualified_field_name(
            register=register, register_array=register_array, field=field
        )
        field_description = self.field_description(
            register=register, field=field, register_array=register_array
        )

        return f"""\
  -- Check that the current value of the {field_description}
  -- equals the given 'expected' value.
  procedure check_{field_name}_equal(
    signal net : inout network_t;
{self.get_array_index_port(register_array=register_array)}\
    expected : in {value_type};
    base_address : in addr_t := (others => '0');
    bus_handle : in bus_master_t := regs_bus_master;
    message : in string := ""
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
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )
            implementations = []

            # Check the register value as a plain SLV casted to integer.
            implementations.append(
                self._register_check_implementation(
                    register=register, register_array=register_array, value_type="integer"
                )
            )

            if register.fields:
                # Check the register value as a record.
                implementations.append(
                    self._register_check_implementation(
                        register=register,
                        register_array=register_array,
                        value_type=f"{register_name}_t",
                    )
                )
            else:
                # Check the register value as a plain SLV.
                implementations.append(
                    self._register_check_implementation(
                        register=register, register_array=register_array, value_type="reg_t"
                    )
                )

            # Check the value of each field.
            for field in register.fields:
                implementations.append(
                    self._field_check_implementation(
                        register=register, register_array=register_array, field=field
                    )
                )

            if implementations:
                vhdl += separator
                vhdl += "\n".join(implementations)
                vhdl += separator
                vhdl += "\n"

        return vhdl

    def _register_check_implementation(
        self, register: "Register", register_array: Optional["RegisterArray"], value_type: str
    ) -> str:
        """
        Get implementation for a 'check_X_equal' procedure for field values.
        """
        signature = self._register_check_signature(
            register=register, register_array=register_array, value_type=value_type
        )
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )

        if value_type not in ["reg_t", "integer"]:
            # These value types do not work with the standard VUnit check procedures, because
            # they are custom types.
            # They also can not be casted to string directly.
            check = """\
    if got /= expected then
      failing_check(
        checker => default_checker,
        msg => p_std_msg(
          check_result => "Equality check failed",
          msg => get_message,
          ctx => (
            "Got " & to_string(to_slv(got)) & ". Expected " & to_string(to_slv(expected)) & "."
          )
        )
      );
    end if;"""

        else:
            check = "    check_equal(got=>got, expected=>expected, msg=>get_message);"

        return f"""\
{signature} is
{self.get_register_array_message(register_array=register_array)}\
{self.get_base_address_message()}\
    constant base_message : string := (
      "Checking the '{register.name}' register"
      & register_array_message
      & base_address_message
      & "."
    );
{self.get_message()}\

    variable got : {value_type};
  begin
    read_{register_name}(
      net => net,
{self.get_array_index_association(register_array=register_array)}\
      value => got,
      base_address => base_address,
      bus_handle => bus_handle
    );

{check}
  end procedure;
"""

    def _field_check_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get implementation for a 'check_X_equal' procedure for field values.
        """
        signature = self._field_check_signature(
            register=register, register_array=register_array, field=field
        )
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
        field_name = self.qualified_field_name(
            register=register, register_array=register_array, field=field
        )
        value_type = self.field_type_name(
            register=register, register_array=register_array, field=field
        )

        if isinstance(field, Enumeration) or (
            isinstance(field, BitVector) and isinstance(field.numerical_interpretation, Fixed)
        ):
            # These field types do not work with the standard VUnit check procedures.
            # Enumeration because it is a custom type.
            # ufixed and sfixed could for all intents and purposes be supported in VUnit,
            # but they are not at the moment (4.7.0).
            # Instead, do a custom check, with error reporting in the same way as in check_equal
            # procedures in VUnit.
            # The VUnit check also has a logging upon a passing check, but we skip that so we do
            # not have to copy so much code.
            def to_string(name: str) -> str:
                if isinstance(field, Enumeration):
                    return f"to_string({name})"

                if isinstance(field, BitVector) and isinstance(
                    field.numerical_interpretation, Fixed
                ):
                    return f'to_string({name}) & " (" & to_string(to_real({name}), "%f") & ")"'

                raise ValueError(f"Unsupported field type: {field}")

            check = f"""\
    if got /= expected then
      failing_check(
        checker => default_checker,
        msg => p_std_msg(
          check_result => "Equality check failed",
          msg => get_message,
          ctx => (
            "Got " & {to_string("got")} & "."
            & " Expected " & {to_string("expected")} & "."
          )
        )
      );
    end if;"""

        else:
            check = "    check_equal(got=>got, expected=>expected, msg=>get_message);"

        return f"""\
{signature} is
{self.get_register_array_message(register_array=register_array)}\
{self.get_base_address_message()}\
    constant base_message : string := (
      "Checking the '{field.name}' field in the '{register.name}' register"
      & register_array_message
      & base_address_message
      & "."
    );
{self.get_message()}\

    variable got_reg : {register_name}_t := {register_name}_init;
    variable got : {value_type} := {field_name}_init;
  begin
    read_{register_name}(
      net => net,
{self.get_array_index_association(register_array=register_array)}\
      value => got_reg,
      base_address => base_address,
      bus_handle => bus_handle
    );
    got := got_reg.{field.name};

{check}
  end procedure;
"""
