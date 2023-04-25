# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register import Register
from .register_array import RegisterArray
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

    def _register_function_signature(self, register, register_array):
        return (
            "function "
            f"{self._register_name(register, register_array)}(array_index : natural) return natural"
        )

    def _register_indexes(self, register_objects):
        vhdl = ""
        for register, register_array in self._iterate_registers(register_objects):
            if register_array is None:
                vhdl += (
                    f"  constant {self._register_name(register)} : natural := {register.index};\n"
                )
            else:
                vhdl += f"  {self._register_function_signature(register, register_array)};\n"

        if vhdl:
            vhdl = f"  -- Register indexes, within the list of registers.\n{vhdl}\n"

        return vhdl

    def _array_length_constant_name(self, register_array):
        return f"{self.module_name}_{register_array.name}_array_length"

    def _array_constants(self, register_objects):
        vhdl = ""
        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                constant = self._array_length_constant_name(register_object)
                vhdl += f"  constant {constant} : natural := {register_object.length};\n"

        if vhdl:
            vhdl = f"  -- Number of times the register array is repeated.\n{vhdl}\n"

        return vhdl

    def _register_map(self, register_objects):
        if not register_objects:
            # It is possible that we have constants but no registers
            return ""

        map_name = f"{self.module_name}_reg_map"
        range_name = f"{self.module_name}_reg_range"

        last_index = register_objects[-1].index
        vhdl = f"""\
  -- Declare register map constants here, but define them in body.
  -- This is done so that functions have been elaborated when they are called.
  subtype {range_name} is natural range 0 to {last_index};
  -- To be used as the 'regs' generic of 'axi_lite_reg_file.vhd'.
  constant {map_name} : reg_definition_vec_t({range_name});

  -- To be used for the 'regs_up' and 'regs_down' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.module_name}_regs_t is reg_vec_t({range_name});
  -- To be used as the 'default_values' generic of 'axi_lite_reg_file.vhd'.
  constant {self.module_name}_regs_init : {self.module_name}_regs_t;

  -- To be used for the 'reg_was_read' and 'reg_was_written' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.module_name}_reg_was_accessed_t is std_ulogic_vector({range_name});

"""

        return vhdl

    def _register_map_body(self, register_objects):
        if not register_objects:
            # It is possible that we have constants but no registers
            return ""

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

            vhdl += f"  -- Bit indexes of fields within the '{register.name}' register"
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
  subtype {name}_t is {field.field_type.vhdl_typedef(bit_width=field.width)};
"""
            vhdl += "\n"

        return vhdl

    def _array_index_functions(self, register_objects):
        vhdl = ""
        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                num_registers = len(register_object.registers)
                array_length = self._array_length_constant_name(register_object)
                for register in register_object.registers:
                    vhdl += f"""\
  {self._register_function_signature(register, register_object)} is
  begin
    assert array_index < {array_length}
      report "Array index out of bounds: " & natural'image(array_index)
      severity failure;
    return {register_object.base_index} + array_index * {num_registers} + {register.index};
  end function;

"""

        return vhdl

    def _constants(self, constants):
        vhdl = ""
        for constant in constants:
            if constant.is_boolean:
                type_name = "boolean"
                value = str(constant.value).lower()
            elif constant.is_integer:
                type_name = "integer"
                value = constant.value
            elif constant.is_float:
                type_name = "real"
                value = constant.value
            elif constant.is_string:
                type_name = "string"
                value = f'"{constant.value}"'
            else:
                raise ValueError(f"Got unexpected constant type. {constant}")

            vhdl += (
                "  constant "
                f"{self.module_name}_constant_{constant.name} : {type_name} := {value};\n"
            )

        if vhdl:
            vhdl = f"  -- Register constants.\n{vhdl}\n"

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

{self._register_indexes(register_objects)}\
{self._array_constants(register_objects)}\
{self._register_map(register_objects)}\
{self._register_fields(register_objects)}\
{self._constants(constants)}\
end package;

package body {pkg_name} is

{self._array_index_functions(register_objects)}\
{self._register_map_body(register_objects)}\
end package body;
"""

        return vhdl
