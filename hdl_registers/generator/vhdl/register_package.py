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
from typing import TYPE_CHECKING, Any

# First party libraries
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.register import Register

if TYPE_CHECKING:
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register_array import RegisterArray

# Local folder libraries
from .vhdl_generator_common import VhdlGeneratorCommon


class VhdlRegisterPackageGenerator(VhdlGeneratorCommon):
    """
    Generate a base VHDL package with basic register information.
    See the :ref:`generator_vhdl` article for usage details.

    * For each register constant, the value as a native VHDL constant.
    * For each register, the index within the register map.
    * For each field in each register

      * Register bit index range definitions.
      * Native VHDL type corresponding to the field type.
      * Conversion of a field value to/from SLV.

    Also produces a register map constant, mapping indexes to modes, suitable for use with
    :ref:`reg_file.axi_lite_reg_file` or :class:`.VhdlAxiLiteWrapperGenerator`.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "VHDL register package"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_regs_pkg.vhd"

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete VHDL package with register and constant information.
        """
        pkg_name = f"{self.name}_regs_pkg"

        vhdl = f"""\
{self.header}
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.fixed_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;


package {pkg_name} is

"""
        if self.register_list.constants:
            vhdl += self._constants()

        if self.register_list.register_objects:
            vhdl += f"""\
{self._register_range()}\
{self._array_constants()}\
{self._register_indexes()}\
{self._register_map_head()}\
{self._field_declarations()}\
"""

        vhdl += "end package;\n"

        if self.register_list.register_objects:
            vhdl += f"""
package body {pkg_name} is

{self._array_index_function_implementations()}\
{self._register_map_body()}\
{self._field_conversion_implementations()}\
end package body;
"""

        return vhdl

    def _constants(self) -> str:
        """
        A set of VHDL constants, corresponding to the provided register constants.
        """
        vhdl = """\
  -- ---------------------------------------------------------------------------
  -- Values of register constants.
"""

        for constant in self.iterate_constants():
            if isinstance(constant, BooleanConstant):
                type_declaration = "boolean"
                value = str(constant.value).lower()
            elif isinstance(constant, IntegerConstant):
                type_declaration = "integer"
                value = str(constant.value)
            elif isinstance(constant, FloatConstant):
                # At least 64 bits (IEEE 1076-2008, 5.2.5.1).
                type_declaration = "real"
                # Note that casting a Python float to string guarantees full precision in the
                # resulting string: https://stackoverflow.com/a/60026172
                value = str(constant.value)
            elif isinstance(constant, StringConstant):
                type_declaration = "string"
                value = f'"{constant.value}"'
            elif isinstance(constant, UnsignedVectorConstant):
                type_declaration = f"unsigned({constant.width} - 1 downto 0)"

                if constant.is_hexadecimal_not_binary:
                    # Underscore separator is allowed in VHDL when defining a hexadecimal SLV.
                    value = f'x"{constant.value}"'
                else:
                    # But not when defining a binary SLV.
                    value = f'"{constant.value_without_separator}"'
            else:
                raise ValueError(f"Got unexpected constant type. {constant}")

            vhdl += (
                "  constant "
                f"{self.name}_constant_{constant.name} : {type_declaration} := {value};\n"
            )

        vhdl += "\n"

        return vhdl

    @property
    def _register_range_type_name(self) -> str:
        """
        Name of the type which is the legal index range of registers.
        """
        return f"{self.name}_reg_range"

    def _register_range(self) -> str:
        """
        A VHDL type that defines the legal range of register indexes.
        """
        last_index = self.register_list.register_objects[-1].index
        vhdl = f"""\
  -- ---------------------------------------------------------------------------
  -- The valid range of register indexes.
  subtype {self._register_range_type_name} is natural range 0 to {last_index};

"""
        return vhdl

    def _array_constants(self) -> str:
        """
        A list of constants defining how many times each register array is repeated.
        """
        vhdl = ""
        for register_array in self.iterate_register_arrays():
            array_name = self.qualified_register_array_name(register_array=register_array)

            vhdl += f"""\
  -- Number of times the '{register_array.name}' register array is repeated.
  constant {array_name}_array_length : natural := {register_array.length};
  -- Range for indexing '{register_array.name}' register array repetitions.
  subtype {array_name}_range is natural range 0 to {register_array.length - 1};

"""

        return vhdl

    def _array_register_index_function_signature(
        self, register: Register, register_array: "RegisterArray"
    ) -> str:
        """
        Signature for the function that returns a register index for the specified index in a
        register array.
        """
        array_name = self.qualified_register_array_name(register_array=register_array)
        vhdl = f"""\
  function {self.qualified_register_name(register, register_array)}(
    array_index : {array_name}_range
  ) return {self._register_range_type_name}"""
        return vhdl

    def _register_indexes(self) -> str:
        """
        A set of named constants for the register index of each register.
        """
        vhdl = "  -- Register indexes, within the list of registers.\n"

        for register, register_array in self.iterate_registers():
            if register_array is None:
                vhdl += (
                    f"  constant {self.qualified_register_name(register)} : "
                    f"natural := {register.index};\n"
                )
            else:
                vhdl += (
                    f"{self._array_register_index_function_signature(register, register_array)};\n"
                )

        vhdl += "\n"

        return vhdl

    def _register_map_head(self) -> str:
        """
        Get constants mapping the register indexes to register modes.
        """
        map_name = f"{self.name}_reg_map"

        vhdl = f"""\
  -- Declare 'reg_map' and 'regs_init' constants here but define them in body (deferred constants).
  -- So that functions have been elaborated when they are called.
  -- Needed for ModelSim compilation to pass.

  -- To be used as the 'regs' generic of 'axi_lite_reg_file.vhd'.
  constant {map_name} : reg_definition_vec_t({self._register_range_type_name});

  -- To be used for the 'regs_up' and 'regs_down' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.name}_regs_t is reg_vec_t({self._register_range_type_name});
  -- To be used as the 'default_values' generic of 'axi_lite_reg_file.vhd'.
  constant {self.name}_regs_init : {self.name}_regs_t;

  -- To be used for the 'reg_was_read' and 'reg_was_written' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.name}_reg_was_accessed_t is \
std_ulogic_vector({self._register_range_type_name});

"""

        return vhdl

    def _field_declarations(self) -> str:
        """
        For every field in every register (plain or in array):

        * Bit index range
        * VHDL type
        * width constant
        * conversion function declarations to/from type and SLV
        """
        vhdl = ""

        for register, register_array in self.iterate_registers():
            if not register.fields:
                continue

            register_description = self.register_description(
                register=register, register_array=register_array
            )

            vhdl += f"""\
  -- -----------------------------------------------------------------------------
  -- Fields in the {register_description}.
"""

            for field in register.fields:
                field_name = self.qualified_field_name(
                    register=register, register_array=register_array, field=field
                )
                field_is_bit = isinstance(field, Bit)

                vhdl += f"  -- Range of the '{field.name}' field.\n"
                if field_is_bit:
                    # A bit field's "range" is simply an index, so the indexing a register SLV
                    # gives a std_logic value.
                    vhdl += f"  constant {field_name} : natural := {field.base_index};\n"
                else:
                    # For other fields its an actual range.
                    vhdl += f"""\
  subtype {field_name} is natural \
range {field.width + field.base_index - 1} downto {field.base_index};
  -- Width of the '{field.name}' field.
  constant {field_name}_width : positive := {field.width};
  -- Type for the '{field.name}' field.
{self._field_type_declaration(field=field, field_name=field_name)}
"""

                vhdl += f"""\
  -- Default value of the '{field.name}' field.
  {self._field_init_value(field=field, field_name=field_name)}
{self._field_conversion_function_declarations(field=field, field_name=field_name)}
"""

        return vhdl

    def _field_type_declaration(self, field: "RegisterField", field_name: str) -> str:
        """
        Get a type declaration for the native VHDL type that corresponds to the field's type.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, Unsigned):
                return f"  subtype {field_name}_t is u_unsigned({field.width - 1} downto 0);"

            if isinstance(field.numerical_interpretation, Signed):
                return f"  subtype {field_name}_t is u_signed({field.width - 1} downto 0);"

            if isinstance(field.numerical_interpretation, UnsignedFixedPoint):
                return (
                    f"  subtype {field_name}_t is ufixed("
                    f"{field.numerical_interpretation.max_bit_index} downto "
                    f"{field.numerical_interpretation.min_bit_index});"
                )

            if isinstance(field.numerical_interpretation, SignedFixedPoint):
                return (
                    f"  subtype {field_name}_t is sfixed("
                    f"{field.numerical_interpretation.max_bit_index} downto "
                    f"{field.numerical_interpretation.min_bit_index});"
                )

            raise TypeError(f'Got unexpected bit vector type for field: "{field}".')

        if isinstance(field, Enumeration):
            # Enum element names in VHDL are exported to the surrounding scope, causing huge
            # risk of name clashes.
            # At the same time, we want the elements to have somewhat concise names so they are
            # easy to work with.
            # Compromise by prefixing the element names with the field name.
            element_names = [f"{field.name}_{element.name}" for element in field.elements]
            elements = ",\n    ".join(element_names)
            return f"""\
  type {field_name}_t is (
    {elements}
  );\
"""

        if isinstance(field, Integer):
            return (
                f"  subtype {field_name}_t is integer "
                f"range {field.min_value} to {field.max_value};"
            )

        raise TypeError(f'Got unexpected type for field: "{field}".')

    def _field_init_value(self, field: "RegisterField", field_name: str) -> str:
        """
        Get an init value constant for the field.
        Uses the native VHDL type that corresponds to the field's type.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        result = f"constant {field_name}_init :"

        if isinstance(field, Bit):
            return f"{result} std_ulogic := '{field.default_value}';"

        if isinstance(field, BitVector):
            return f'{result} {field_name}_t := "{field.default_value}";'

        if isinstance(field, Enumeration):
            return f"{result} {field_name}_t := {field.name}_{field.default_value.name};"

        if isinstance(field, Integer):
            return f"{result} {field_name}_t := {field.default_value};"

        raise TypeError(f'Got unexpected type for field: "{field}".')

    def _field_conversion_function_declarations(
        self, field: "RegisterField", field_name: str
    ) -> str:
        """
        Function declarations for functions that convert the field's native VHDL representation
        to/from SLV.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        if isinstance(field, (Bit, BitVector)):
            return ""

        if isinstance(field, (Enumeration, Integer)):
            to_slv_name = self.field_to_slv_function_name(field=field, field_name=field_name)

            return f"""\
  -- Type for the '{field.name}' field as an SLV.
  subtype {field_name}_slv_t is std_ulogic_vector({field.width - 1} downto 0);
  -- Cast a '{field.name}' field value to SLV.
  function {to_slv_name}(data : {field_name}_t) return {field_name}_slv_t;
  -- Get a '{field.name}' field value from a register value.
  function to_{field_name}(data : reg_t) return {field_name}_t;
"""

        raise TypeError(f'Got unexpected type for field: "{field}".')

    def _array_index_function_implementations(self) -> str:
        """
        Implementation for the functions that return a register index for the specified index in a
        register array.
        """
        vhdl = ""
        for register_array in self.iterate_register_arrays():
            num_registers = len(register_array.registers)
            for register in register_array.registers:
                vhdl += f"""\
{self._array_register_index_function_signature(register, register_array)} is
  begin
    return {register_array.base_index} + array_index * {num_registers} + {register.index};
  end function;

"""

        return vhdl

    def _register_map_body(self) -> str:
        """
        Get the body of the register map definition constants.
        """
        map_name = f"{self.name}_reg_map"
        range_name = f"{self.name}_reg_range"

        register_definitions = []
        default_values = []
        vhdl_array_index = 0
        for register_object in self.iterate_register_objects():
            if isinstance(register_object, Register):
                idx = self.qualified_register_name(register_object)
                opening = f"{vhdl_array_index} => "

                register_definitions.append(
                    f"{opening}(idx => {idx}, reg_type => {register_object.mode.shorthand})"
                )
                default_values.append(f'{opening}"{register_object.default_value:032b}"')

                vhdl_array_index = vhdl_array_index + 1

            else:
                for array_index in range(register_object.length):
                    for register in register_object.registers:
                        regiser_name = self.qualified_register_name(register, register_object)
                        idx = f"{regiser_name}({array_index})"
                        opening = f"{vhdl_array_index} => "

                        register_definitions.append(
                            f"{opening}(idx => {idx}, reg_type => {register.mode.shorthand})"
                        )
                        default_values.append(f'{opening}"{register.default_value:032b}"')

                        vhdl_array_index = vhdl_array_index + 1

        array_element_separator = ",\n    "
        vhdl = f"""\
  constant {map_name} : reg_definition_vec_t({range_name}) := (
    {array_element_separator.join(register_definitions)}
  );

  constant {self.name}_regs_init : {self.name}_regs_t := (
    {array_element_separator.join(default_values)}
  );

"""

        return vhdl

    def _field_conversion_implementations(self) -> str:
        """
        Implementation of functions that convert a register field's native VHDL representation
        to/from SLV.
        """
        vhdl = ""

        for register, register_array in self.iterate_registers():
            for field in register.fields:
                if isinstance(field, (Bit, BitVector)):
                    # Skip all field types that do not have any functions that need to
                    # be implemented.
                    continue

                name = self.qualified_field_name(
                    register=register, register_array=register_array, field=field
                )
                to_slv_name = self.field_to_slv_function_name(field=field, field_name=name)

                if isinstance(field, Enumeration):
                    to_slv = f"""\
    constant data_int : natural := {name}_t'pos(data);
    constant result : {name}_slv_t := std_ulogic_vector(
      to_unsigned(data_int, {name}_width)
    );
"""
                    from_slv = f"""\
    constant field_slv : {name}_slv_t := data({name});
    constant field_int : natural := to_integer(unsigned(field_slv));
    constant result : {name}_t := {name}_t'val(field_int);
"""
                elif isinstance(field, Integer):
                    vector_type = "signed" if field.is_signed else "unsigned"
                    to_slv = f"""\
    constant result : {name}_slv_t := std_ulogic_vector(to_{vector_type}(data, {name}_width));
"""
                    from_slv = f"""\
    constant result : integer := to_integer({vector_type}(data({name})));
"""
                else:
                    raise TypeError(f'Got unexpected field type: "{field}".')

                vhdl += f"""\
  -- Cast a '{field.name}' field value to SLV.
  function {to_slv_name}(data : {name}_t) return {name}_slv_t is
{to_slv}\
  begin
    return result;
  end function;

  -- Get a '{field.name}' field value from a register value.
  function to_{name}(data : reg_t) return {name}_t is
{from_slv}\
  begin
    return result;
  end function;

"""

        return vhdl
