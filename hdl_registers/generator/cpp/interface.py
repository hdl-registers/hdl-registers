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
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.field.bit import Bit
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

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete C++ interface header with constants, types, attributes and methods for
        accessing registers and fields.
        """
        cpp_code = ""

        for register, register_array in self.iterate_registers():
            field_cpp_code = ""

            for field in register.fields:
                field_cpp_code += self._field_attributes(
                    register=register, register_array=register_array, field=field
                )

            cpp_code += field_cpp_code
            if field_cpp_code:
                cpp_code += "\n"

        for register_array in self.iterate_register_arrays():
            cpp_code += self._register_array_attributes(register_array=register_array)

        cpp_code += f"  class I{self._class_name}\n"
        cpp_code += "  {\n"
        cpp_code += "  public:\n"

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

        cpp_code_top = f"""\
{self.header}
#pragma once

#include <cassert>
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
                raise ValueError(f"Got unexpected constant type. {constant}")

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

        cpp_code = self.comment("Number of registers within this register map.")
        cpp_code += f"    static const size_t num_registers = {num_registers}uL;\n\n"
        return cpp_code

    def _field_interface(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        def function(return_type_name: str, signature: str) -> str:
            return f"    virtual {return_type_name} {signature} const = 0;\n"

        cpp_code = ""
        for field in register.fields:
            field_description = self.field_description(
                register=register, register_array=register_array, field=field
            )
            field_type_name = self._field_value_type_name(
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
                cpp_code += function(return_type_name=field_type_name, signature=signature)

                comment = [f"Getter for the {field_description},", "given a register value."]
                cpp_code += self.comment_block(text=comment)

                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=True,
                )
                cpp_code += function(return_type_name=field_type_name, signature=signature)

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
                cpp_code += function(return_type_name="void", signature=signature)

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
                cpp_code += function(return_type_name="uint32_t", signature=signature)

            cpp_code += "\n"

        return cpp_code

    @staticmethod
    def _get_default_value(field: "RegisterField") -> str:
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

    def _field_attributes(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        field_description = self.field_description(
            register=register, register_array=register_array, field=field
        )
        cpp_code = self.comment(f"Attributes for the {field_description}.", indent=2)

        array_namespace = f"::{register_array.name}" if register_array else ""
        namespace = f"{self.name}{array_namespace}::{register.name}::{field.name}"

        cpp_code += f"  namespace {namespace}\n"
        cpp_code += "  {\n"
        cpp_code += f"    static const auto width = {field.width};\n"

        if isinstance(field, Enumeration):
            name_value_pairs = [f"{element.name} = {element.value}," for element in field.elements]
            separator = "\n      "
            cpp_code += f"""\
    enum Enumeration
    {{
      {separator.join(name_value_pairs)}
    }};
"""

        cpp_code += (
            f"    static const auto default_value = {self._get_default_value(field=field)};\n"
        )
        cpp_code += "  }\n"

        return cpp_code

    def _register_array_attributes(self, register_array: "RegisterArray") -> str:
        return f"""\
  // Attributes for the "{register_array.name}" register array.
  namespace {self.name}::{register_array.name}
  {{
    // Number of times the registers of the array are repeated.
    static const auto array_length = {register_array.length};
  }};

"""
