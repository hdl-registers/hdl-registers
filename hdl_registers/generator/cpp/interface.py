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
        cpp_code += self._get_constants()

        cpp_code += self._get_num_registers()

        cpp_code += f"    virtual ~I{self._class_name}() {{}}\n"

        separator = self.get_separator_line()

        for register, register_array in self.iterate_registers():
            cpp_code += self._get_register_heading(
                register=register, register_array=register_array, separator=separator
            )

            if register.mode.software_can_read:
                cpp_code += self._get_getters(register=register, register_array=register_array)

                if register.mode.software_can_write:
                    # Add empty line between getter and setter interfaces.
                    cpp_code += "\n"

            if register.mode.software_can_write:
                cpp_code += self._get_setters(register=register, register_array=register_array)

            cpp_code += separator

        cpp_code += "  };\n\n"

        cpp_code_top = """\
#pragma once

#include <sstream>
#include <cstdint>
#include <cstdlib>

"""
        return cpp_code_top + self._with_namespace(cpp_code)

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

        attributes_cpp: list[str] = []
        struct_values_cpp: list[str] = []
        default_values_cpp: list[str] = []

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
                field_type_struct = f"{field.name}::Enumeration"
            else:
                typedef = ""
                field_type_struct = field_type

            default_value = self._get_default_value(field=field)
            default_value_raw = self._get_default_value(field=field, raw=True)

            # If 'width' is 32, '1 << width' is a 33-bit unsigned number.
            # The C++ standard requires an "int" to be at least 16 bits, "long" at least 32,
            # and "long long" at least 64.
            # Hence in order to avoid overflow, we have to use "uLL".
            # Once '1' is subtracted from the shifted value, it will always fit in 32 unsigned bits.
            attributes_cpp.append(f"""\
{indentation}// Attributes for the '{field.name}' field.
{indentation}namespace {field.name}
{indentation}{{
{indentation}  // The number of bits that the field occupies.
{indentation}  static const size_t width = {field.width};
{indentation}  // The bit index of the lowest bit in the field.
{indentation}  static const size_t shift = {field.base_index};
{indentation}  // The bit mask of the field, at index zero.
{indentation}  static const uint32_t mask_at_base = (1uLL << width) - 1;
{indentation}  // The bit mask of the field, at the field's bit index.
{indentation}  static const uint32_t mask_shifted = mask_at_base << shift;
{typedef}
{indentation}  // Initial value of the field at device startup/reset.
{indentation}  static const {field_type} default_value = {default_value};
{indentation}  // Raw representation of the initial value, at the the field's bit index.
{indentation}  static const uint32_t default_value_raw = {default_value_raw} << shift;
{indentation}}}
""")
            struct_values_cpp.append(f"{indentation}  {field_type_struct} {field.name};")
            default_values_cpp.append(f"{indentation}  {field.name}::default_value,")

        indentation = self.get_indentation(indent=indent)
        attribute_cpp = "\n".join(attributes_cpp)
        struct_value_cpp = "\n".join(struct_values_cpp)
        default_value_cpp = "\n".join(default_values_cpp)

        return f"""\
{indentation}// Attributes for the '{register.name}' register.
{indentation}namespace {register.name} {{
{attribute_cpp}
{indentation}  // Struct that holds the value of each field in the register,
{indentation}  // in a native C++ representation.
{indentation}  struct Value {{
{struct_value_cpp}
{indentation}  }};
{indentation}  // Initial value of the register at device startup/reset.
{indentation}  const Value default_value = {{
{default_value_cpp}
{indentation}  }};
{indentation}}}
"""

    @staticmethod
    def _get_default_value(field: RegisterField, raw: bool = False) -> str:  # noqa: PLR0911
        """
        Get the field's default value formatted in a way suitable for C++ code.
        """
        if isinstance(field, Bit):
            if raw:
                return field.default_value

            return "true" if field.default_value == "1" else "false"

        if isinstance(field, BitVector):
            if raw:
                return f"0b{field.default_value}uL"

            # Note that casting a Python float to string guarantees full precision in the
            # resulting string: https://stackoverflow.com/a/60026172
            return str(
                field.numerical_interpretation.convert_from_unsigned_binary(
                    unsigned_binary=int(field.default_value, base=2)
                )
            )

        if isinstance(field, Enumeration):
            if raw:
                return f"{field.default_value.value}uL"

            return f"Enumeration::{field.default_value.name}"

        if isinstance(field, Integer):
            if raw:
                return f"{field.default_value_uint}uL"
            return str(field.default_value)

        raise ValueError(f'Unknown field type for "{field.name}" field: {type(field)}')

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

    def _get_constants(self) -> str:
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

    def _get_num_registers(self) -> str:
        # It is possible that we have constants but no registers
        num_registers = 0
        if self.register_list.register_objects:
            num_registers = self.register_list.register_objects[-1].index + 1

        cpp_code = self.comment("Number of registers within this register list.")
        cpp_code += f"    static const size_t num_registers = {num_registers}uL;\n\n"
        return cpp_code

    def _get_getters(self, register: Register, register_array: RegisterArray | None) -> str:
        def get_function(comment: str, return_type: str, signature: str) -> str:
            return f"""\
{comment}\
    virtual {return_type} {signature} = 0;
"""

        cpp_code: list[str] = []

        register_type = self._get_register_value_type(
            register=register, register_array=register_array
        )
        signature = self._register_getter_signature(
            register=register, register_array=register_array
        )
        cpp_code.append(
            get_function(
                comment=self._get_getter_comment(),
                return_type=register_type,
                signature=signature,
            )
        )

        if register.fields:
            # The main getter will perform type conversion.
            # Provide a getter that returns the raw value also.
            signature = self._register_getter_signature(
                register=register, register_array=register_array, raw=True
            )
            cpp_code.append(
                get_function(
                    comment=self._get_getter_comment(raw=True),
                    return_type="uint32_t",
                    signature=signature,
                )
            )

        for field in register.fields:
            field_type = self._get_field_value_type(
                register=register, register_array=register_array, field=field
            )

            signature = self._field_getter_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=False,
            )
            cpp_code.append(
                get_function(
                    comment=self._get_getter_comment(field=field),
                    return_type=field_type,
                    signature=signature,
                )
            )

        return "\n".join(cpp_code)

    def _get_setters(self, register: Register, register_array: RegisterArray | None) -> str:
        def get_function(comment: str, signature: str) -> str:
            return f"{comment}    virtual void {signature} = 0;\n"

        cpp_code: list[str] = []

        signature = self._register_setter_signature(
            register=register, register_array=register_array
        )
        cpp_code.append(
            get_function(
                comment=self._get_setter_comment(register=register),
                signature=signature,
            )
        )

        if register.fields:
            # The main setter will perform type conversion.
            # Provide a setter that takes a raw value also.
            signature = self._register_setter_signature(
                register=register, register_array=register_array, raw=True
            )
            cpp_code.append(
                get_function(
                    comment=self._get_setter_comment(register=register, raw=True),
                    signature=signature,
                )
            )

        for field in register.fields:
            signature = self._field_setter_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=False,
            )
            cpp_code.append(
                get_function(
                    comment=self._get_setter_comment(register=register, field=field),
                    signature=signature,
                )
            )

        return "\n".join(cpp_code)
