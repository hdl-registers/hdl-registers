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
from hdl_registers.field.register_field_type import Fixed
from hdl_registers.generator.vhdl.vhdl_generator_common import BUS_ACCESS_DIRECTIONS

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

    * For each field in each readable register, a procedure that checks that the register field's
      current value is equal to a given expected value.

    Uses VUnit Verification Component calls, via the procedures from
    :class:`.VhdlSimulationReadWritePackageGenerator`.

    The generated VHDL file needs also the generated packages from
    :class:`.VhdlRegisterPackageGenerator` and :class:`.VhdlRecordPackageGenerator`.
    """

    __version__ = "1.0.0"

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
context vunit_lib.vc_context;
context vunit_lib.vunit_context;

library common;
use common.addr_pkg.all;

library reg_file;
use reg_file.reg_operations_pkg.all;

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

        for register, register_array in self.iterate_bus_accessible_registers(
            direction=BUS_ACCESS_DIRECTIONS["read"]
        ):
            declarations = []

            for field in register.fields:
                signature = self._field_check_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                )
                declarations.append(f"{signature};\n")

            if declarations:
                vhdl += separator
                vhdl += "\n".join(declarations)
                vhdl += separator
                vhdl += "\n"

        return vhdl

    def _field_check_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get signature for a 'check_X_equal' procedure.
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

        for register, register_array in self.iterate_bus_accessible_registers(
            direction=BUS_ACCESS_DIRECTIONS["read"]
        ):
            implementations = []

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

    def _field_check_implementation(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        Get implementation for a 'check_X_equal' procedure.
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
            isinstance(field, BitVector) and isinstance(field.field_type, Fixed)
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

                if isinstance(field, BitVector) and isinstance(field.field_type, Fixed):
                    return f'to_string({name}) & " (" & to_string(to_real({name})) & ")"'

                raise ValueError(f"Unsupported field type: {field}")

            check = f"""\
    if got /= expected then
      failing_check(
        checker=>default_checker,
        msg=>p_std_msg(
          check_result=>"Equality check failed",
          msg=>get_message,
          ctx=> (
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
