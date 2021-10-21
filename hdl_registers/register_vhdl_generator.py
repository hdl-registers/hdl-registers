# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------


from .register import Register
from .register_array import RegisterArray
from .register_code_generator import RegisterCodeGenerator


class RegisterVhdlGenerator(RegisterCodeGenerator):
    """
    Generate a VHDL package with register information.
    """

    def __init__(self, module_name, generated_info):
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
            vhdl += "\n"

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
            vhdl += "\n"

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
  constant {map_name} : reg_definition_vec_t({range_name});

  subtype {self.module_name}_regs_t is reg_vec_t({range_name});
  constant {self.module_name}_regs_init : {self.module_name}_regs_t;

  subtype {self.module_name}_reg_was_accessed_t is std_logic_vector({range_name});

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
                default_values.append(
                    f"{opening}std_logic_vector(to_signed({register_object.default_value}, 32))"
                )

                vhdl_array_index = vhdl_array_index + 1
            else:
                for array_index in range(register_object.length):
                    for register in register_object.registers:
                        idx = f"{self._register_name(register, register_object)}({array_index})"
                        opening = f"{vhdl_array_index} => "

                        register_definitions.append(
                            f"{opening}(idx => {idx}, reg_type => {register.mode})"
                        )
                        default_values.append(
                            f"{opening}std_logic_vector(to_signed({register.default_value}, 32))"
                        )

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
            for field in register.fields:
                name = f"{self._register_name(register, register_array)}_{field.name}"

                if field.width == 1:
                    vhdl += f"  constant {name} : natural := {field.base_index};\n"
                else:
                    vhdl += f"""\
  subtype {name} is natural range {field.width + field.base_index - 1} downto {field.base_index};
  constant {name}_width : positive := {field.width};
"""

            if register.fields:
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
            vhdl += (
                "  constant "
                f"{self.module_name}_constant_{constant.name} : integer := {constant.value};\n"
            )
        if vhdl:
            vhdl += "\n"

        return vhdl

    def get_package(self, register_objects, constants):
        pkg_name = f"{self.module_name}_regs_pkg"

        vhdl = f"""\
{self._header()}
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

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
