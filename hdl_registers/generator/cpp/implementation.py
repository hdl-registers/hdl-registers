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
from hdl_registers.field.integer import Integer

# Local folder libraries
from .cpp_generator_common import CppGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class CppImplementationGenerator(CppGeneratorCommon):
    """
    Generate a C++ class implementation.
    See the :ref:`generator_cpp` article for usage details.

    The class implementation will contain:

    * for each register, implementation of getter and setter methods for reading/writing the
      register as an ``uint``.

    * for each field in each register, implementation of getter and setter methods for
      reading/writing the field as its native type (enumeration, positive/negative int, etc.).

      * The setter will read-modify-write the register to update only the specified field,
        depending on the mode of the register.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "C++ implementation"

    DEFAULT_INDENTATION_LEVEL = 4

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}.cpp"

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete C++ class implementation with all methods.
        """
        cpp_code = f"  {self._class_name}::{self._constructor_signature()}\n"
        cpp_code += "      : m_registers(reinterpret_cast<volatile uint32_t *>(base_address))\n"
        cpp_code += "  {\n"
        cpp_code += "    // Empty\n"
        cpp_code += "  }\n\n"

        for register, register_array in self.iterate_registers():
            cpp_code += f"{self.get_separator_line(indent=2)}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            cpp_code += self.comment_block(
                text=[description, "See interface header for documentation."], indent=2
            )
            cpp_code += "\n"

            if register.mode.software_can_read:
                cpp_code += self._register_getter_function(register, register_array)

                for field in register.fields:
                    cpp_code += self._field_getter_function(register, register_array, field=field)
                    cpp_code += self._field_getter_function_from_value(
                        register, register_array, field=field
                    )

            if register.mode.software_can_write:
                cpp_code += self._register_setter_function(register, register_array)

                for field in register.fields:
                    cpp_code += self._field_setter_function(register, register_array, field=field)
                    cpp_code += self._field_setter_function_from_value(
                        register, register_array, field=field
                    )

        cpp_code_top = f"{self.header}\n"
        cpp_code_top += f'#include "include/{self.name}.h"\n\n'

        return cpp_code_top + self._with_namespace(cpp_code)

    def _register_setter_function(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        signature = self._register_setter_function_signature(
            register=register, register_array=register_array, indent=2
        )
        cpp_code = f"  void {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        if register_array:
            cpp_code += (
                f"    assert(array_index < {self.name}::{register_array.name}::array_length);\n"
            )
            cpp_code += (
                f"    const size_t index = {register_array.base_index} "
                f"+ array_index * {len(register_array.registers)} + {register.index};\n"
            )
        else:
            cpp_code += f"    const size_t index = {register.index};\n"

        cpp_code += "    m_registers[index] = register_value;\n"
        cpp_code += "  }\n\n"
        return cpp_code

    def _field_setter_function(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        signature = self._field_setter_function_signature(
            register=register,
            register_array=register_array,
            field=field,
            from_value=False,
            indent=2,
        )

        cpp_code = f"  void {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        if self.field_setter_should_read_modify_write(register=register):
            register_getter_function_name = self._register_getter_function_name(
                register=register, register_array=register_array
            )
            cpp_code += self.comment(
                comment="Get the current value of other fields by reading register on the bus."
            )
            current_register_value = f"{register_getter_function_name}("
            if register_array:
                current_register_value += "array_index"
            current_register_value += ")"

        else:
            cpp_code += self.comment(
                "Set everything except for the field to default when writing the value."
            )
            current_register_value = str(register.default_value)

        cpp_code += f"    const uint32_t current_register_value = {current_register_value};\n"

        signature = self._field_setter_function_name(
            register=register, register_array=register_array, field=field, from_value=True
        )
        cpp_code += (
            "    const uint32_t result_register_value = "
            f"{signature}(current_register_value, field_value);\n"
        )

        register_setter_function_name = self._register_setter_function_name(
            register=register, register_array=register_array
        )
        cpp_code += f"    {register_setter_function_name}("
        if register_array:
            cpp_code += "array_index, "
        cpp_code += "result_register_value);\n"

        cpp_code += "  }\n\n"

        return cpp_code

    def _field_setter_function_from_value(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        signature = self._field_setter_function_signature(
            register=register, register_array=register_array, field=field, from_value=True, indent=2
        )

        return f"""\
  uint32_t {self._class_name}::{signature} const\
  {{
{self._get_field_shift_and_mask(field=field)}\
{self._get_field_setter_value_checker(field=field)}\
    const uint32_t field_value_masked = field_value & mask_at_base;
    const uint32_t field_value_masked_and_shifted = field_value_masked << shift;

    const uint32_t mask_shifted_inverse = ~mask_shifted;
    const uint32_t register_value_masked = register_value & mask_shifted_inverse;

    const uint32_t result_register_value = register_value_masked | field_value_masked_and_shifted;

    return result_register_value;
  }}

"""

    @staticmethod
    def _get_field_shift_and_mask(field: "RegisterField") -> str:
        return f"""\
    const uint32_t shift = {field.base_index}uL;
    const uint32_t mask_at_base = 0b{"1" * field.width}uL;
    const uint32_t mask_shifted = mask_at_base << shift;

"""

    @staticmethod
    def _get_field_setter_value_checker(field: "RegisterField") -> str:
        comment = "// Check that field value is within the legal range."
        if isinstance(field, Integer):
            return f"""\
    {comment}
    assert(field_value >= {field.min_value});
    assert(field_value <= {field.max_value});

"""

        if isinstance(field, BitVector):
            return f"""\
    {comment}
    const uint32_t mask_at_base_inverse = ~mask_at_base;
    assert((field_value & mask_at_base_inverse) == 0);

"""

        return ""

    def _get_field_getter_value_checker(self, field: "RegisterField") -> str:
        if isinstance(field, Integer):
            return self._get_field_setter_value_checker(field=field)

        return ""

    def _register_getter_function(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        signature = self._register_getter_function_signature(
            register=register, register_array=register_array, indent=2
        )
        cpp_code = f"  uint32_t {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        if register_array:
            cpp_code += (
                f"    assert(array_index < {self.name}::{register_array.name}::array_length);\n"
            )
            cpp_code += (
                f"    const size_t index = {register_array.base_index} "
                f"+ array_index * {len(register_array.registers)} + {register.index};\n"
            )
        else:
            cpp_code += f"    const size_t index = {register.index};\n"

        cpp_code += "    const uint32_t result = m_registers[index];\n\n"
        cpp_code += "    return result;\n"
        cpp_code += "  }\n\n"
        return cpp_code

    def _field_getter_function(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        signature = self._field_getter_function_signature(
            register=register,
            register_array=register_array,
            field=field,
            from_value=False,
            indent=2,
        )

        field_type_name = self._field_value_type_name(
            register=register, register_array=register_array, field=field
        )

        cpp_code = f"  {field_type_name} {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        register_getter_function_name = self._register_getter_function_name(
            register=register, register_array=register_array
        )

        field_getter_from_value_function_name = self._field_getter_function_name(
            register=register, register_array=register_array, field=field, from_value=True
        )

        cpp_code += f"    const uint32_t register_value = {register_getter_function_name}("
        if register_array:
            cpp_code += "array_index"
        cpp_code += ");\n"

        cpp_code += (
            f"    const {field_type_name} field_value = "
            f"{field_getter_from_value_function_name}(register_value);\n"
        )
        cpp_code += "\n    return field_value;\n"
        cpp_code += "  }\n\n"

        return cpp_code

    def _field_getter_function_from_value(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        signature = self._field_getter_function_signature(
            register=register, register_array=register_array, field=field, from_value=True, indent=2
        )

        type_name = self._field_value_type_name(
            register=register, register_array=register_array, field=field
        )

        cpp_code = f"""\
  {type_name} {self._class_name}::{signature} const
  {{
{self._get_field_shift_and_mask(field=field)}\
    const uint32_t result_masked = register_value & mask_shifted;
    const uint32_t result_shifted = result_masked >> shift;

    {type_name} field_value;

"""

        if type_name == "uint32_t":
            cpp_code += """\
    // No casting needed.
    field_value = result_shifted;
"""

        else:
            if isinstance(field, Enumeration):
                cpp_code += f"""\
    // "Cast" to the enum type.
    field_value = {type_name}(result_shifted);
"""

            elif isinstance(field, Integer) and field.is_signed:
                cpp_code += f"""\
    const {type_name} sign_bit_mask = 1 << {field.width - 1};

    if (result_shifted & sign_bit_mask)
    {{
      // Value is to be interpreted as negative.
      // Sign extend it from the width of the field to the width of the return type.
      field_value = result_shifted - 2 * sign_bit_mask;
    }}
    else
    {{
      // Value is positive.
      field_value = result_shifted;
    }}
"""
            else:
                raise ValueError(f"Got unexpected field type: {type_name}")

        cpp_code += f"""
{self._get_field_getter_value_checker(field=field)}\
    return field_value;
  }}

"""

        return cpp_code
