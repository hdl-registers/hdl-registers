# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.register_array import RegisterArray

from .cpp_generator_common import CppGeneratorCommon

if TYPE_CHECKING:
    from pathlib import Path

    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register


class CppInterfaceGenerator(CppGeneratorCommon):
    """
    Generate a C++ interface header, suitable for mocking in a unit test environment.
    See the :ref:`generator_cpp` article for usage details.

    The interface header will contain:

    * Attribute constants for each register and field, such as width, default value, etc.

    * Enumeration types for all :ref:`field_enumeration`.

    * Constant values for all :ref:`register constants <constant_overview>`.

    * for each register, signature of getter and setter methods for reading/writing the register as
      an ``uint``.

    * for each field in each register, signature of getter and setter methods for reading/writing
      the field as its native type (enumeration, positive/negative int, etc.).

      * The setter will read-modify-write the register to update only the specified field,
        depending on the mode of the register.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "C++ interface header"

    DEFAULT_INDENTATION_LEVEL = 4

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"i_{self.name}.h"

    def get_code(
        self,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> str:
        """
        Get a complete C++ interface header with constants, types, attributes and methods for
        accessing registers and fields.
        """
        cpp_code = f"""{self._get_attributes()}\
  class I{self._class_name}
  {{
  public:
"""
        cpp_code += self._constants()

        cpp_code += self._num_registers()

        cpp_code += f"    virtual ~I{self._class_name}() {{}}\n\n"

        for register, register_array in self.iterate_registers():
            cpp_code += f"{self.get_separator_line()}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            description += f" Mode '{register.mode.name}'."

            cpp_code += self.comment(comment=description)
            cpp_code += "\n"

            if register.mode.software_can_read:
                cpp_code += self.comment(
                    "Getter that will read the whole register's value over the register bus."
                )
                signature = self._register_getter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += f"    virtual uint32_t {signature} const = 0;\n\n"

            if register.mode.software_can_write:
                cpp_code += self.comment(
                    "Setter that will write the whole register's value over the register bus."
                )
                signature = self._register_setter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += f"    virtual void {signature} const = 0;\n\n"

            cpp_code += self._field_interface(register, register_array)

        cpp_code += "  };\n\n"

        cpp_code_top = """\
#pragma once

#include <sstream>
#include <cstdint>
#include <cstdlib>

"""
        return cpp_code_top + self._with_namespace(cpp_code)

    def _constants(self) -> str:
        cpp_code = ""

        for constant in self.iterate_constants():
            if isinstance(constant, BooleanConstant):
                type_declaration = " bool"
                value = str(constant.value).lower()
            elif isinstance(constant, IntegerConstant):
                type_declaration = " int"
                value = str(constant.value)
            elif isinstance(constant, FloatConstant):
                # Expand "const" to "constexpr", which is needed for static floats:
                # https://stackoverflow.com/questions/9141950/
                # Use "double", to match the VHDL type which is at least 64 bits
                # (IEEE 1076-2008, 5.2.5.1).
                type_declaration = "expr double"
                # Note that casting a Python float to string guarantees full precision in the
                # resulting string: https://stackoverflow.com/a/60026172
                value = str(constant.value)
            elif isinstance(constant, StringConstant):
                # Expand "const" to "constexpr", which is needed for static string literals.
                type_declaration = "expr auto"
                value = f'"{constant.value}"'
            elif isinstance(constant, UnsignedVectorConstant):
                type_declaration = " auto"
                value = f"{constant.prefix}{constant.value_without_separator}"
            else:
                raise TypeError(f"Got unexpected constant type: {constant}")

            cpp_code += self.comment("Register constant.")
            cpp_code += f"    static const{type_declaration} {constant.name} = {value};\n"

        if cpp_code:
            cpp_code += "\n"

        return cpp_code

    def _num_registers(self) -> str:
        # It is possible that we have constants but no registers
        num_registers = 0
        if self.register_list.register_objects:
            num_registers = self.register_list.register_objects[-1].index + 1

        cpp_code = self.comment("Number of registers within this register list.")
        cpp_code += f"    static const size_t num_registers = {num_registers}uL;\n\n"
        return cpp_code

    def _field_interface(self, register: Register, register_array: RegisterArray | None) -> str:
        def get_function(return_type: str, signature: str) -> str:
            return f"    virtual {return_type} {signature} const = 0;\n"

        cpp_code = ""
        for field in register.fields:
            field_type = self._get_field_value_type(
                register=register, register_array=register_array, field=field
            )
            field_description = self.field_description(
                register=register, register_array=register_array, field=field
            )

            if register.mode.software_can_read:
                comment = [
                    f"Getter for the {field_description},",
                    "which will read register value over the register bus.",
                ]
                cpp_code += self.comment_block(text=comment)

                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=False,
                )
                cpp_code += get_function(return_type=field_type, signature=signature)

                comment = [f"Getter for the {field_description},", "given a register value."]
                cpp_code += self.comment_block(text=comment)

                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=True,
                )
                cpp_code += get_function(return_type=field_type, signature=signature)

            if register.mode.software_can_write:
                comment = [f"Setter for the {field_description},"]
                if self.field_setter_should_read_modify_write(register=register):
                    comment.append("which will read-modify-write over the register bus.")
                else:
                    comment.append(
                        "which will set the field to the given value, "
                        "and everything else to default."
                    )

                cpp_code += self.comment_block(text=comment)

                signature = self._field_setter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=False,
                )
                cpp_code += get_function(return_type="void", signature=signature)

                comment = [
                    f"Setter for the {field_description},",
                    "given a register value, which will return an updated value.",
                ]
                cpp_code += self.comment_block(text=comment)

                signature = self._field_setter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=True,
                )
                cpp_code += get_function(return_type="uint32_t", signature=signature)

            cpp_code += "\n"

        return cpp_code

    @staticmethod
    def _get_default_value(field: RegisterField) -> str:
        """
        Get the field's default value formatted in a way suitable for C++ code.
        """
        if isinstance(field, (Bit, BitVector)):
            return f"0b{field.default_value}"

        if isinstance(field, Enumeration):
            return f"Enumeration::{field.default_value.name}"

        if isinstance(field, Integer):
            return str(field.default_value)

        raise ValueError(f'Unknown field type for "{field.name}" field: {type(field)}')

    def _get_attributes(self) -> str:
        if not self.register_list.register_objects:
            # Don't create a namespace if the register list contains only constants.
            return ""

        attributes_cpp: list[str] = []
        for register_object in self.iterate_register_objects():
            if isinstance(register_object, RegisterArray):
                attributes_cpp.append(
                    self._get_register_array_attributes(register_array=register_object)
                )
            elif register_object.fields:
                attributes_cpp.append(
                    self._get_register_attributes(register=register_object, indent=4)
                )

        attribute_cpp = "\n".join(attributes_cpp)
        return f"""\
  namespace {self.name}
  {{

{attribute_cpp}
  }} // namespace {self.name}

"""

    def _get_register_attributes(self, register: Register, indent: int) -> str:
        if not register.fields:
            raise ValueError("Should not end up here if the register has no fields.")

        fields_cpp: list[str] = []

        for field in register.fields:
            indentation = self.get_indentation(indent=indent + 2)
            field_type = self._get_field_value_type(
                register=register, register_array=None, field=field, include_namespace=False
            )

            if isinstance(field, Enumeration):
                separator = "\n" + " " * (indent + 6)
                name_value_pairs = "".join(
                    [f"{separator}{element.name} = {element.value}," for element in field.elements]
                )
                typedef = f"""
{indentation}  // The valid elements for this enumeration field.
{indentation}  enum Enumeration
{indentation}  {{\
{name_value_pairs}
{indentation}  }};
"""
            else:
                typedef = ""

            # If 'width' is 32, '1 << width' is a 33-bit unsigned number.
            # The C++ standard requires an "int" to be at least 16 bits, "long" at least 32,
            # and "long long" at least 64.
            # Hence in order to avoid overflow, we have to use "uLL".
            # Once '1' is subtracted from the shifted value, it will always fit in 32 unsigned bits.
            fields_cpp.append(f"""\
{indentation}// Attributes for the '{field.name}' field.
{indentation}namespace {field.name}
{indentation}{{
{indentation}  // The number of bits that the field occupies.
{indentation}  static const size_t width = {field.width};
{indentation}  // The bit index of the lowest bit in the field.
{indentation}  static const size_t shift = {field.base_index};
{indentation}  // The bit mask of the field, at index zero.
{indentation}  static const uint32_t mask_at_base = (1uLL << width) - 1;
{indentation}  // The bit mask of the field, at the bit index where the field is located.
{indentation}  static const uint32_t mask_shifted = mask_at_base << shift;
{typedef}
{indentation}  // Initial value of the field at device startup/reset.
{indentation}  static const {field_type} default_value = {self._get_default_value(field=field)};
{indentation}}}
""")

        indentation = self.get_indentation(indent=indent)
        register_cpp = "\n".join(fields_cpp)

        return f"""\
{indentation}// Attributes for the '{register.name}' register.
{indentation}namespace {register.name} {{
{register_cpp}\
{indentation}}}
"""

    def _get_register_array_attributes(self, register_array: RegisterArray) -> str:
        registers_cpp = [
            self._get_register_attributes(register=register, indent=6)
            for register in register_array.registers
            if register.fields
        ]
        register_cpp = "\n".join(registers_cpp)

        return f"""\
    // Attributes for the '{register_array.name}' register array.
    namespace {register_array.name}
    {{
      // Number of times the registers of the array are repeated.
      static const auto array_length = {register_array.length};

{register_cpp}\
    }}
"""
