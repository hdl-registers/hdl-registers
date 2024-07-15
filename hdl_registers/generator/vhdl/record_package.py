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
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.register_mode import HardwareAccessDirection, SoftwareAccessDirection

# Local folder libraries
from .vhdl_generator_common import VhdlGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class VhdlRecordPackageGenerator(VhdlGeneratorCommon):
    """
    Generate a VHDL package with register record types containing natively-typed members for
    each register field.
    See the :ref:`generator_vhdl` article for usage details.

    * For each register, plain or in array, a record with natively-typed members for each
      register field.
    * For each register array, a correctly-ranged array of records for the registers in
      that array.
    * Combined record with all the registers and register arrays.
      One each for registers in the up direction and in the down direction.
    * Constants with default values for all of the above types.
    * Conversion functions to/from ``std_logic_vector`` representation for all of the
      above types.

    The generated VHDL file needs also the generated package
    from :class:`.VhdlRegisterPackageGenerator`.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "VHDL record package"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_register_record_pkg.vhd"

    def create(self, **kwargs: Any) -> Path:
        """
        See super class for API details.

        Overloaded here because this package file shall only be created if the register list
        actually has any registers.
        """
        return self._create_if_there_are_registers_otherwise_delete_file(**kwargs)

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete VHDL package with register record types.
        """
        package_name = self.output_file.stem

        vhdl = f"""\
{self.header}
library ieee;
use ieee.fixed_pkg.all;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library reg_file;
use reg_file.reg_file_pkg.reg_t;

use work.{self.name}_regs_pkg.all;


package {package_name} is

"""

        if self.register_list.register_objects:
            vhdl += f"""\
{self._register_field_records()}\
{self._register_records()}\
{self._register_was_accessed()}\
"""

        vhdl += "end package;\n"

        if self.register_list.register_objects:
            vhdl += f"""
package body {package_name} is

{self._register_field_record_conversion_implementations()}\
{self._register_record_conversion_implementations()}\
{self._register_was_accessed_conversion_implementations()}\
end package body;
"""

        return vhdl

    def _register_field_records(self) -> str:
        """
        For every register (plain or in array) that has at least one field:

        * Record with members for each field that are of the correct native VHDL type.
        * Default value constant for the above record.
        * Function to convert the above record to SLV.
        * Function to convert a register SLV to the above record.
        """
        vhdl = """\
  -- -----------------------------------------------------------------------------
  -- Record with correctly-typed members for each field in each register.
"""

        for register, register_array in self.iterate_registers():
            if not register.fields:
                continue

            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )
            register_description = self.register_description(
                register=register, register_array=register_array
            )

            record = ""
            init = []

            for field in register.fields:
                field_name = self.qualified_field_name(
                    register=register, register_array=register_array, field=field
                )
                init.append(f"{field.name} => {field_name}_init")

                field_type_name = self.field_type_name(
                    register=register, register_array=register_array, field=field
                )
                record += f"    {field.name} : {field_type_name};\n"

            init_str = "    " + ",\n    ".join(init)

            vhdl += f"""\
  -- Fields in the {register_description} as a record.
  type {register_name}_t is record
{record}\
  end record;
  -- Default value for the {register_description} as a record.
  constant {register_name}_init : {register_name}_t := (
{init_str}
  );
  -- Convert a record of the {register_description} to SLV.
  function to_slv(data : {register_name}_t) return reg_t;
  -- Convert an SLV register value to the record for the {register_description}.
  function to_{register_name}(data : reg_t) return {register_name}_t;

"""

        return vhdl

    def _register_records(self) -> str:
        """
        Get two records,
        * One with all the registers that are in the 'up' direction.
        * One with all the registers that are in the 'down' direction.

        Along with conversion function declarations to/from SLV.

        In order to create the above records, we have to create partial-array records for each
        register array.
        One record for 'up' and one for 'down', with all registers in the array that are in
        that direction.
        """
        vhdl = ""

        direction = HardwareAccessDirection.UP

        if self.has_any_hardware_accessible_register(direction=direction):
            vhdl += self._array_field_records(direction=direction)
            vhdl += self._get_register_record(direction=direction)
            vhdl += f"""\
  -- Convert record with everything in the '{direction.name.lower()}' direction to SLV \
register list.
  function to_slv(data : {self.name}_regs_{direction.name.lower()}_t) return {self.name}_regs_t;

"""

        direction = HardwareAccessDirection.DOWN

        if self.has_any_hardware_accessible_register(direction=direction):
            vhdl += self._array_field_records(direction=direction)
            vhdl += self._get_register_record(direction=direction)
            vhdl += f"""\
  -- Convert SLV register list to record with everything in the \
'{direction.name.lower()}' direction.
  function to_{self.name}_regs_{direction.name.lower()}(data : {self.name}_regs_t) \
return {self.name}_regs_{direction.name.lower()}_t;

"""

        return vhdl

    def _array_field_records(self, direction: "HardwareAccessDirection") -> str:
        """
        For every register array that has at least one register in the specified direction:

        * Record with members for each register in the array that is in the specified direction.
        * Default value constant for the above record.
        * VHDL vector type of the above record, ranged per the range of the register array.

        This function assumes that the register map has registers in the given direction.
        """
        vhdl = ""

        for array in self.iterate_hardware_accessible_register_arrays(direction=direction):
            array_name = self.qualified_register_array_name(register_array=array)
            vhdl += f"""\
  -- Registers of the '{array.name}' array that are in the '{direction.name.lower()}' direction.
  type {array_name}_{direction.name.lower()}_t is record
"""

            vhdl_array_init = []
            for register in self.iterate_hardware_accessible_array_registers(
                register_array=array, direction=direction
            ):
                vhdl += self._record_member_declaration_for_register(
                    register=register, register_array=array
                )

                register_name = self.qualified_register_name(
                    register=register, register_array=array
                )
                init = f"{register_name}_init" if register.fields else "(others => '0')"
                vhdl_array_init.append(f"{register.name} => {init}")

            init = "    " + ",\n    ".join(vhdl_array_init)
            vhdl += f"""\
  end record;
  -- Default value of the above record.
  constant {array_name}_{direction.name.lower()}_init : {array_name}_{direction.name.lower()}_t := (
{init}
  );
  -- VHDL array of the above record, ranged per the length of the '{array.name}' \
register array.
  type {array_name}_{direction.name.lower()}_vec_t is array (0 to {array.length - 1}) of \
{array_name}_{direction.name.lower()}_t;

"""

        heading = f"""\
  -- -----------------------------------------------------------------------------
  -- Below is a record with correctly typed and ranged members for all registers, register arrays
  -- and fields that are in the '{direction.name.lower()}' direction.
"""
        if vhdl:
            heading += f"""\
  -- But first, records for the registers of each register array the are in \
the '{direction.name.lower()}' direction.
"""

        return f"{heading}{vhdl}"

    def _get_register_record(self, direction: "HardwareAccessDirection") -> str:
        """
        Get the record that contains all registers and arrays in the specified direction.
        Also default value constant for this record.

        This function assumes that the register map has registers in the given direction.
        """
        record_init = []
        vhdl = f"""\
  -- Record with everything in the '{direction.name.lower()}' direction.
  type {self.name}_regs_{direction.name.lower()}_t is record
"""

        for array in self.iterate_hardware_accessible_register_arrays(direction=direction):
            array_name = self.qualified_register_array_name(register_array=array)

            vhdl += f"    {array.name} : {array_name}_{direction.name.lower()}_vec_t;\n"
            record_init.append(
                f"{array.name} => (others => {array_name}_{direction.name.lower()}_init)"
            )

        for register in self.iterate_hardware_accessible_plain_registers(direction=direction):
            vhdl += self._record_member_declaration_for_register(register=register)

            if register.fields:
                register_name = self.qualified_register_name(register=register)
                record_init.append(f"{register.name} => {register_name}_init")
            else:
                record_init.append(f"{register.name} => (others => '0')")

        init = "    " + ",\n    ".join(record_init)

        return f"""\
{vhdl}\
  end record;
  -- Default value of the above record.
  constant {self.name}_regs_{direction.name.lower()}_init : \
{self.name}_regs_{direction.name.lower()}_t := (
{init}
  );
"""

    def _record_member_declaration_for_register(
        self, register: "Register", register_array: Optional["RegisterArray"] = None
    ) -> str:
        """
        Get the record member declaration line for a register that shall be part of the record.
        """
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )

        if register.fields:
            return f"    {register.name} : {register_name}_t;\n"

        return f"    {register.name} : reg_t;\n"

    def _register_was_accessed(self) -> str:
        """
        Get record for 'reg_was_read' and 'reg_was_written' ports.
        Should include only the registers that are actually readable/writeable.
        """
        vhdl = ""

        for direction in SoftwareAccessDirection:
            if self.has_any_software_accessible_register(direction=direction):
                vhdl += self._register_was_accessed_record(direction=direction)

        return vhdl

    def _register_was_accessed_record(self, direction: "SoftwareAccessDirection") -> str:
        """
        Get the record for 'reg_was_read' or 'reg_was_written'.
        """
        vhdl = f"""\
  -- ---------------------------------------------------------------------------
  -- Below is a record with a status bit for each {direction.value.name_adjective} register in the \
register map.
  -- It can be used for the 'reg_was_{direction.value.name_past}' port of a register file wrapper.
"""

        for array in self.iterate_software_accessible_register_arrays(direction=direction):
            array_name = self.qualified_register_array_name(register_array=array)
            vhdl += f"""\
  -- One status bit for each {direction.value.name_adjective} register in the '{array.name}' \
register array.
  type {array_name}_was_{direction.value.name_past}_t is record
"""

            for register in self.iterate_software_accessible_array_registers(
                register_array=array, direction=direction
            ):
                vhdl += f"    {register.name} : std_ulogic;\n"

            vhdl += f"""\
  end record;
  -- Default value of the above record.
  constant {array_name}_was_{direction.value.name_past}_init : \
{array_name}_was_{direction.value.name_past}_t := (others => '0');
  -- Vector of the above record, ranged per the length of the '{array.name}' \
register array.
  type {array_name}_was_{direction.value.name_past}_vec_t is array (0 to {array.length - 1}) \
of {array_name}_was_{direction.value.name_past}_t;

"""

        vhdl += f"""\
  -- Combined status mask record for all {direction.value.name_adjective} register.
  type {self.name}_reg_was_{direction.value.name_past}_t is record
"""

        array_init = []
        for array in self.iterate_software_accessible_register_arrays(direction=direction):
            array_name = self.qualified_register_array_name(register_array=array)

            vhdl += f"    {array.name} : {array_name}_was_{direction.value.name_past}_vec_t;\n"
            array_init.append(
                f"{array.name} => (others => {array_name}_was_{direction.value.name_past}_init)"
            )

        has_at_least_one_register = False
        for register in self.iterate_software_accessible_plain_registers(direction=direction):
            vhdl += f"    {register.name} : std_ulogic;\n"
            has_at_least_one_register = True

        init_arrays = ("    " + ",\n    ".join(array_init)) if array_init else ""
        init_registers = "    others => '0'" if has_at_least_one_register else ""
        separator = ",\n" if (init_arrays and init_registers) else ""

        vhdl += f"""\
  end record;
  -- Default value for the above record.
  constant {self.name}_reg_was_{direction.value.name_past}_init : \
{self.name}_reg_was_{direction.value.name_past}_t := (
{init_arrays}{separator}{init_registers}
  );
  -- Convert an SLV 'reg_was_{direction.value.name_past}' from generic register file \
to the record above.
  function to_{self.name}_reg_was_{direction.value.name_past}(
    data : {self.name}_reg_was_accessed_t
  ) return {self.name}_reg_was_{direction.value.name_past}_t;

"""

        return vhdl

    def _register_field_record_conversion_implementations(self) -> str:
        """
        Implementation of functions that convert a register record with native field types
        to/from SLV.
        """
        vhdl = ""

        def _get_functions(register: "Register", register_array: Optional["RegisterArray"]) -> str:
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )

            to_slv = ""
            to_record = ""

            for field in register.fields:
                field_name = self.qualified_field_name(
                    register=register, register_array=register_array, field=field
                )
                field_to_slv = self.field_to_slv(
                    field=field, field_name=field_name, value=f"data.{field.name}"
                )
                to_slv += f"    result({field_name}) := {field_to_slv};\n"

                if isinstance(field, Bit):
                    to_record += f"    result.{field.name} := data({field_name});\n"

                elif isinstance(field, BitVector):
                    to_record += f"    result.{field.name} := {field_name}_t(data({field_name}));\n"

                elif isinstance(field, (Enumeration, Integer)):
                    to_record += f"    result.{field.name} := to_{field_name}(data);\n"

                else:
                    raise TypeError(f'Got unexpected field type: "{field}".')

            # Set "don't care" on the bits that have no field, so that a register value comparison
            # can be true even if there is junk in the unused bits.
            return f"""\
  function to_slv(data : {register_name}_t) return reg_t is
    variable result : reg_t := (others => '-');
  begin
{to_slv}
    return result;
  end function;

  function to_{register_name}(data : reg_t) return {register_name}_t is
    variable result : {register_name}_t := {register_name}_init;
  begin
{to_record}
    return result;
  end function;

"""

        for register, register_array in self.iterate_registers():
            if register.fields:
                vhdl += _get_functions(register=register, register_array=register_array)

        return vhdl

    def _register_record_conversion_implementations(self) -> str:
        """
        Conversion function implementations to/from SLV for the records containing all
        registers and arrays in 'up'/'down' direction.
        """
        vhdl = ""

        if self.has_any_hardware_accessible_register(direction=HardwareAccessDirection.UP):
            vhdl += self._register_record_up_to_slv()

        if self.has_any_hardware_accessible_register(direction=HardwareAccessDirection.DOWN):
            vhdl += self._get_registers_down_to_record_function()

        return vhdl

    def _register_record_up_to_slv(self) -> str:
        """
        Conversion function implementation for converting a record of all the 'up' registers
        to a register SLV list.

        This function assumes that the register map has registers in the given direction.
        """
        to_slv = ""

        for register, register_array in self.iterate_hardware_accessible_registers(
            direction=HardwareAccessDirection.UP
        ):
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )

            if register_array is None:
                result = f"    result({register_name})"
                record = f"data.{register.name}"

                if register.fields:
                    to_slv += f"{result} := to_slv({record});\n"
                else:
                    to_slv += f"{result} := {record};\n"

            else:
                for array_idx in range(register_array.length):
                    result = f"    result({register_name}({array_idx}))"
                    record = f"data.{register_array.name}({array_idx}).{register.name}"

                    if register.fields:
                        to_slv += f"{result} := to_slv({record});\n"
                    else:
                        to_slv += f"{result} := {record};\n"

        return f"""\
  function to_slv(data : {self.name}_regs_up_t) return {self.name}_regs_t is
    variable result : {self.name}_regs_t := {self.name}_regs_init;
  begin
{to_slv}
    return result;
  end function;

"""

    def _get_registers_down_to_record_function(self) -> str:
        """
        Conversion function implementation for converting all the 'down' registers
        in a register SLV list to record.

        This function assumes that the register map has registers in the given direction.
        """
        to_record = ""

        for register, register_array in self.iterate_hardware_accessible_registers(
            direction=HardwareAccessDirection.DOWN
        ):
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )

            if register_array is None:
                result = f"    result.{register.name}"
                data = f"data({register_name})"

                if register.fields:
                    to_record += f"{result} := to_{register_name}({data});\n"
                else:
                    to_record += f"{result} := {data};\n"

            else:
                for array_idx in range(register_array.length):
                    result = f"    result.{register_array.name}({array_idx}).{register.name}"
                    data = f"data({register_name}({array_idx}))"

                    if register.fields:
                        to_record += f"{result} := to_{register_name}({data});\n"
                    else:
                        to_record += f"{result} := {data};\n"

        return f"""\
  function to_{self.name}_regs_down(data : {self.name}_regs_t) return \
{self.name}_regs_down_t is
    variable result : {self.name}_regs_down_t := {self.name}_regs_down_init;
  begin
{to_record}
    return result;
  end function;

"""

    def _register_was_accessed_conversion_implementations(self) -> str:
        """
        Get conversion functions from SLV 'reg_was_read'/'reg_was_written' to record types.
        """
        vhdl = ""

        for direction in SoftwareAccessDirection:
            if self.has_any_software_accessible_register(direction=direction):
                vhdl += self._register_was_accessed_conversion_implementation(direction=direction)

        return vhdl

    def _register_was_accessed_conversion_implementation(
        self, direction: "SoftwareAccessDirection"
    ) -> str:
        """
        Get a conversion function  from SLV 'reg_was_read'/'reg_was_written' to record type.
        """
        vhdl = f"""\
  function to_{self.name}_reg_was_{direction.value.name_past}(
    data : {self.name}_reg_was_accessed_t
  ) return {self.name}_reg_was_{direction.value.name_past}_t is
    variable result : {self.name}_reg_was_{direction.value.name_past}_t := \
{self.name}_reg_was_{direction.value.name_past}_init;
  begin
"""

        for register in self.iterate_software_accessible_plain_registers(direction=direction):
            register_name = self.qualified_register_name(register=register)
            vhdl += f"    result.{register.name} := data({register_name});\n"

        for array in self.iterate_register_arrays():
            for register in self.iterate_software_accessible_array_registers(
                register_array=array, direction=direction
            ):
                register_name = self.qualified_register_name(
                    register=register, register_array=array
                )

                for array_index in range(array.length):
                    vhdl += (
                        f"    result.{array.name}({array_index}).{register.name} := "
                        f"data({register_name}(array_index=>{array_index}));\n"
                    )

        return f"""\
{vhdl}
    return result;
  end function;

"""
