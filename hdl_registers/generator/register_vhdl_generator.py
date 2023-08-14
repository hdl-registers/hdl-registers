# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.integer import Integer
from hdl_registers.field.register_field import RegisterField
from hdl_registers.field.register_field_type import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.register import Register
from hdl_registers.register_array import RegisterArray

# Local folder libraries
from .register_code_generator import RegisterCodeGenerator


class RegisterVhdlGenerator(RegisterCodeGenerator):
    """
    Generate a VHDL package with register information.
    """

    def __init__(self, module_name, generated_info):
        """
        Arguments:
            module_name (str): The name of the register map.
            generated_info (list(str)): Will be placed in the file headers.
        """
        self.module_name = module_name
        self.generated_info = generated_info

    @staticmethod
    def _comment(comment, indentation=0):
        indent = " " * indentation
        return f"{indent}-- {comment}\n"

    def _header(self):
        return "".join([self._comment(header_line) for header_line in self.generated_info])

    def _register_name(self, register, register_array=None):
        if register_array is None:
            return f"{self.module_name}_{register.name}"
        return f"{self.module_name}_{register_array.name}_{register.name}"

    @property
    def _register_range_type_name(self):
        """
        Name of the type which is the legal index of registers.
        """
        return f"{self.module_name}_reg_range"

    def _register_function_signature(self, register, register_array):
        vhdl = f"""\
  function {self._register_name(register, register_array)}(
    array_index : natural range 0 to {self._array_length_constant_name(register_array)} - 1
  ) return {self._register_range_type_name}"""
        return vhdl

    def _register_indexes(self, register_objects):
        vhdl = "  -- Register indexes, within the list of registers.\n"

        for register, register_array in self._iterate_registers(register_objects):
            if register_array is None:
                vhdl += (
                    f"  constant {self._register_name(register)} : natural := {register.index};\n"
                )
            else:
                vhdl += f"{self._register_function_signature(register, register_array)};\n"

        vhdl += "\n"

        return vhdl

    def _array_length_constant_name(self, register_array):
        return f"{self.module_name}_{register_array.name}_array_length"

    def _register_range(self, register_objects):
        last_index = register_objects[-1].index
        vhdl = f"""\
  -- The valid range of register indexes.
  subtype {self._register_range_type_name} is natural range 0 to {last_index};

"""
        return vhdl

    def _array_constants(self, register_objects):
        vhdl = ""
        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                constant = self._array_length_constant_name(register_object)
                vhdl += (
                    f"  -- Number of times the '{register_object.name}' "
                    "register array is repeated.\n"
                )
                vhdl += f"  constant {constant} : natural := {register_object.length};\n"

        if vhdl:
            vhdl += "\n"

        return vhdl

    def _register_map_head(self):
        map_name = f"{self.module_name}_reg_map"

        vhdl = f"""\
  -- Declare 'reg_map' and 'regs_init' constants here, but define them in body.
  -- This is done so that functions have been elaborated when they are called.

  -- To be used as the 'regs' generic of 'axi_lite_reg_file.vhd'.
  constant {map_name} : reg_definition_vec_t({self._register_range_type_name});

  -- To be used for the 'regs_up' and 'regs_down' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.module_name}_regs_t is reg_vec_t({self._register_range_type_name});
  -- To be used as the 'default_values' generic of 'axi_lite_reg_file.vhd'.
  constant {self.module_name}_regs_init : {self.module_name}_regs_t;

  -- To be used for the 'reg_was_read' and 'reg_was_written' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.module_name}_reg_was_accessed_t is \
std_ulogic_vector({self._register_range_type_name});

"""

        return vhdl

    def _register_map_body(self, register_objects):
        map_name = f"{self.module_name}_reg_map"
        range_name = f"{self.module_name}_reg_range"

        register_definitions = []
        default_values = []
        vhdl_array_index = 0
        for register_object in register_objects:
            if isinstance(register_object, Register):
                idx = self._register_name(register_object)
                opening = f"{vhdl_array_index} => "

                register_definitions.append(
                    f"{opening}(idx => {idx}, reg_type => {register_object.mode})"
                )
                default_values.append(f'{opening}"{register_object.default_value:032b}"')

                vhdl_array_index = vhdl_array_index + 1
            else:
                for array_index in range(register_object.length):
                    for register in register_object.registers:
                        idx = f"{self._register_name(register, register_object)}({array_index})"
                        opening = f"{vhdl_array_index} => "

                        register_definitions.append(
                            f"{opening}(idx => {idx}, reg_type => {register.mode})"
                        )
                        default_values.append(f'{opening}"{register.default_value:032b}"')

                        vhdl_array_index = vhdl_array_index + 1

        array_element_separator = ",\n    "
        vhdl = f"""\
  constant {map_name} : reg_definition_vec_t({range_name}) := (
    {array_element_separator.join(register_definitions)}
  );

  constant {self.module_name}_regs_init : {self.module_name}_regs_t := (
    {array_element_separator.join(default_values)}
  );

"""

        return vhdl

    def _register_fields(self, register_objects):
        vhdl = ""
        for register, register_array in self._iterate_registers(register_objects):
            if not register.fields:
                continue

            vhdl += f"  -- Fields within the '{register.name}' register"
            if register_array is not None:
                vhdl += f" within the '{register_array.name}' register array"
            vhdl += ".\n"

            for field in register.fields:
                name = f"{self._register_name(register, register_array)}_{field.name}"

                if field.width == 1:
                    vhdl += f"  constant {name} : natural := {field.base_index};\n"
                else:
                    vhdl += f"""\
  subtype {name} is natural range {field.width + field.base_index - 1} downto {field.base_index};
  constant {name}_width : positive := {field.width};
  subtype {name}_t is {self._field_typedef(field=field)};
"""
            vhdl += "\n"

        return vhdl

    def _field_typedef(self, field: "RegisterField"):
        if isinstance(field, Bit):
            return "std_ulogic"

        if isinstance(field, Integer):
            return f"integer range {field.min_value} to {field.max_value}"

        if isinstance(field, BitVector):
            if isinstance(field.field_type, Unsigned):
                return f"u_unsigned({field.width - 1} downto 0)"

            if isinstance(field.field_type, Signed):
                return f"u_signed({field.width - 1} downto 0)"

            if isinstance(field.field_type, UnsignedFixedPoint):
                return (
                    "ufixed("
                    f"{field.field_type.max_bit_index} downto {field.field_type.min_bit_index})"
                )

            if isinstance(field.field_type, SignedFixedPoint):
                return (
                    "sfixed("
                    f"{field.field_type.max_bit_index} downto {field.field_type.min_bit_index})"
                )

            raise TypeError(f'Got unexpected type for field: "{field}".')

        raise TypeError(f'Got unexpected type for field: "{field}".')

    def _array_index_functions(self, register_objects):
        vhdl = ""
        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                num_registers = len(register_object.registers)
                for register in register_object.registers:
                    vhdl += f"""\
{self._register_function_signature(register, register_object)} is
  begin
    return {register_object.base_index} + array_index * {num_registers} + {register.index};
  end function;

"""

        return vhdl

    def _constants(self, constants):
        vhdl = "  -- Register constant values.\n"

        for constant in constants:
            if isinstance(constant, BooleanConstant):
                type_declaration = "boolean"
                value = str(constant.value).lower()
            elif isinstance(constant, IntegerConstant):
                type_declaration = "integer"
                value = constant.value
            elif isinstance(constant, FloatConstant):
                type_declaration = "real"
                value = constant.value
            elif isinstance(constant, StringConstant):
                type_declaration = "string"
                value = f'"{constant.value}"'
            elif isinstance(constant, UnsignedVectorConstant):
                type_declaration = f"unsigned({constant.width} - 1 downto 0)"
                prefix = "x" if constant.is_hexadecimal_not_binary else ""
                value = f'{prefix}"{constant.value}"'
            else:
                raise ValueError(f"Got unexpected constant type. {constant}")

            vhdl += (
                "  constant "
                f"{self.module_name}_constant_{constant.name} : {type_declaration} := {value};\n"
            )

        vhdl += "\n"

        return vhdl

    def get_package(self, register_objects, constants):
        """
        Get a complete VHDL package with register and constant information.

        Arguments:
            register_objects (list): Register arrays and registers to be included.
            constants (list(Constant)): Constants to be included.

        Returns:
            str: VHDL code.
        """
        pkg_name = f"{self.module_name}_regs_pkg"

        vhdl = f"""\
{self._header()}
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.fixed_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;


package {pkg_name} is

"""

        if register_objects:
            vhdl += f"""\
{self._register_range(register_objects)}\
{self._array_constants(register_objects)}\
{self._register_indexes(register_objects)}\
{self._register_map_head()}\
{self._register_fields(register_objects)}"""

        if constants:
            vhdl += self._constants(constants)

        vhdl += "end package;\n"

        if register_objects:
            vhdl += f"""
package body {pkg_name} is

{self._array_index_functions(register_objects)}\
{self._register_map_body(register_objects)}\
end package body;
"""

        return vhdl
