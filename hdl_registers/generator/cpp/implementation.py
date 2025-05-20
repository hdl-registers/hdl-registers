# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

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

from .cpp_generator_common import CppGeneratorCommon

if TYPE_CHECKING:
    from pathlib import Path

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

    __version__ = "2.0.2"

    SHORT_DESCRIPTION = "C++ implementation"

    DEFAULT_INDENTATION_LEVEL = 2

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}.cpp"

    def get_code(
        self,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> str:
        """
        Get a complete C++ class implementation with all methods.
        """
        cpp_code = f"""\
{self._get_macros()}\
  {self._class_name}::{self._constructor_signature()}
      : m_registers(reinterpret_cast<volatile uint32_t *>(base_address)),
        m_assertion_handler(assertion_handler)
  {{
    // Empty
  }}
"""

        separator = self.get_separator_line()
        for register, register_array in self.iterate_registers():
            cpp_code += self._get_register_heading(
                register=register, register_array=register_array, separator=separator
            )

            methods_cpp: list[str] = []

            if register.mode.software_can_read:
                methods_cpp.append(
                    self._get_register_getter(register=register, register_array=register_array)
                )

                if register.fields:
                    # The main getter will perform type conversion.
                    # Provide a getter that returns the raw value also.
                    methods_cpp.append(
                        self._get_register_raw_getter(
                            register=register, register_array=register_array
                        )
                    )

                for field in register.fields:
                    methods_cpp.append(
                        self._get_field_getter(
                            register=register, register_array=register_array, field=field
                        )
                    )
                    methods_cpp.append(
                        self._get_field_getter_from_raw(register, register_array, field=field)
                    )

            if register.mode.software_can_write:
                methods_cpp.append(
                    self._get_register_setter(register=register, register_array=register_array)
                )

                if register.fields:
                    # The main getter will perform type conversion.
                    # Provide a setter that takes a raw value also.
                    methods_cpp.append(
                        self._get_register_raw_setter(
                            register=register, register_array=register_array
                        )
                    )

                for field in register.fields:
                    methods_cpp.append(
                        self._get_field_setter(
                            register=register, register_array=register_array, field=field
                        )
                    )
                    methods_cpp.append(
                        self._get_field_to_raw(register, register_array, field=field)
                    )

            cpp_code += "\n".join(methods_cpp)
            cpp_code += separator

        cpp_code += "\n"
        cpp_code_top = f'#include "include/{self.name}.h"\n\n'

        return cpp_code_top + self._with_namespace(cpp_code)

    def _get_macros(self) -> str:
        def get_macro(name: str) -> str:
            macro_name = f"_{name}_ASSERT_TRUE"
            return f"""\
#ifdef NO_REGISTER_{name}_ASSERT
  #define {macro_name}(expression, message) ((void)0)
#else
  #define {macro_name}(expression, message) (_ASSERT_TRUE(expression, message))
#endif
"""

        setter_assert = get_macro(name="SETTER")
        getter_assert = get_macro(name="GETTER")
        array_index_assert = get_macro(name="ARRAY_INDEX")

        file_name = self.output_file.name
        file_name_space = " " * (31 - len(file_name))
        assert_true = f"""\
#define _ASSERT_TRUE(expression, message)                                                      \\
  {{                                                                                            \\
    if (!static_cast<bool>(expression)) {{                                                      \\
      std::ostringstream diagnostics;                                                          \\
      diagnostics << "{file_name}:" << __LINE__ << ": " << message << "."; {file_name_space}\\
      std::string diagnostic_message = diagnostics.str();                                      \\
      m_assertion_handler(&diagnostic_message);                                                \\
    }}                                                                                          \\
  }}
"""

        return f"""\
// Macros called by the register code below to check for runtime errors.
{setter_assert}
{getter_assert}
{array_index_assert}
// Base macro called by the other macros.
{assert_true}
"""

    def _get_register_getter(self, register: Register, register_array: RegisterArray | None) -> str:
        comment = self._get_getter_comment()
        return_type = self._get_register_value_type(
            register=register, register_array=register_array
        )
        signature = self._register_getter_signature(
            register=register, register_array=register_array
        )

        if register.fields:
            raw_value = self._get_read_raw_value_call(
                register=register, register_array=register_array
            )

            fields = ""
            values: list[str] = []
            for field in register.fields:
                field_type = self._get_field_value_type(
                    register=register, register_array=register_array, field=field
                )
                getter_name = self._field_getter_name(
                    register=register, register_array=register_array, field=field, from_raw=True
                )
                fields += f"    const {field_type} {field.name}_value = {getter_name}(raw_value);\n"
                values.append(f"{field.name}_value")

            value = ", ".join(values)
            result = f"""\
{raw_value}
{fields}
    return {{{value}}};\
"""
        else:
            raw_value = self._get_read_raw_value_code(
                register=register, register_array=register_array
            )
            result = f"""\
{raw_value}
    return raw_value;\
"""

        return f"""\
{comment}\
  {return_type} {self._class_name}::{signature}
  {{
{result}
  }}
"""

    def _get_read_raw_value_call(
        self, register: Register, register_array: RegisterArray | None
    ) -> str:
        getter_name = self._register_getter_name(
            register=register, register_array=register_array, raw=True
        )
        array_index = "array_index" if register_array else ""
        return f"""\
    const uint32_t raw_value = {getter_name}({array_index});
"""

    def _get_read_raw_value_code(
        self,
        register: Register,
        register_array: RegisterArray | None,
        include_index: bool = True,
    ) -> str:
        index = (
            self._get_index(register=register, register_array=register_array)
            if include_index
            else ""
        )
        return f"""\
{index}\
    const uint32_t raw_value = m_registers[index];
"""

    def _get_index(self, register: Register, register_array: RegisterArray | None) -> str:
        if register_array:
            checker = f"""\
    _ARRAY_INDEX_ASSERT_TRUE(
      array_index < {self.name}::{register_array.name}::array_length,
      "Got '{register_array.name}' array index out of range: " << array_index
    );
"""
            index = (
                f"{register_array.base_index} "
                f"+ array_index * {len(register_array.registers)} + {register.index}"
            )
        else:
            checker = ""
            index = str(register.index)

        return f"""\
{checker}\
    const size_t index = {index};
"""

    def _get_register_raw_getter(
        self, register: Register, register_array: RegisterArray | None
    ) -> str:
        comment = self._get_getter_comment(raw=True)
        signature = self._register_getter_signature(
            register=register, register_array=register_array, raw=True
        )
        raw_value = self._get_read_raw_value_code(register=register, register_array=register_array)

        return f"""\
{comment}\
  uint32_t {self._class_name}::{signature}
  {{
{raw_value}
    return raw_value;
  }}
"""

    def _get_field_getter(
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        comment = self._get_getter_comment(field=field)
        field_type = self._get_field_value_type(
            register=register, register_array=register_array, field=field
        )
        signature = self._field_getter_signature(
            register=register,
            register_array=register_array,
            field=field,
            from_raw=False,
        )
        raw_value = self._get_read_raw_value_call(register=register, register_array=register_array)
        from_raw_name = self._field_getter_name(
            register=register, register_array=register_array, field=field, from_raw=True
        )

        return f"""\
{comment}\
  {field_type} {self._class_name}::{signature}
  {{
{raw_value}
    return {from_raw_name}(raw_value);
  }}
"""

    def _get_field_getter_from_raw(
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        namespace = self._get_namespace(
            register=register, register_array=register_array, field=field
        )
        comment = self._get_from_raw_comment(field=field)
        field_type = self._get_field_value_type(
            register=register, register_array=register_array, field=field
        )
        signature = self._field_getter_signature(
            register=register, register_array=register_array, field=field, from_raw=True
        )
        cast = self._get_from_raw_cast(field=field, field_type=field_type)
        checker = self._get_field_checker(field=field, setter_or_getter="getter")

        return f"""\
{comment}\
  {field_type} {self._class_name}::{signature}
  {{
    const uint32_t result_masked = register_value & {namespace}mask_shifted;
    const uint32_t result_shifted = result_masked >> {namespace}shift;

{cast}
{checker}\
    return field_value;
  }}
"""

    def _get_from_raw_cast(self, field: RegisterField, field_type: str) -> str:  # noqa: PLR0911
        no_cast = """\
    // No casting needed.
    const uint32_t field_value = result_shifted;
"""

        if isinstance(field, Bit):
            return """\
    // Convert to the result type.
    const bool field_value = static_cast<bool>(result_shifted);
"""

        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, Unsigned):
                return no_cast

            if isinstance(field.numerical_interpretation, Signed):
                return self._get_field_to_negative(field=field)

            if isinstance(field.numerical_interpretation, UnsignedFixedPoint):
                return self._get_field_to_real(
                    field=field, field_type=field_type, variable="result_shifted"
                )

            if isinstance(field.numerical_interpretation, SignedFixedPoint):
                return (
                    self._get_field_to_negative(field=field, variable="result_negative")
                    + "\n"
                    + self._get_field_to_real(
                        field=field, field_type=field_type, variable="result_negative"
                    )
                )

            raise TypeError(
                f"Got unexpected numerical interpretation type: {field.numerical_interpretation}"
            )

        if isinstance(field, Enumeration):
            return f"""\
    // "Cast" to the enum type.
    const auto field_value = {field_type}(result_shifted);
"""

        if isinstance(field, Integer):
            if field.is_signed:
                return self._get_field_to_negative(field=field)

            return no_cast

        raise TypeError(f"Got unexpected field type: {field}")

    def _get_field_to_negative(self, field: Integer, variable: str = "field_value") -> str:
        # Note that the shift result has maximum value of '1 << 31', which always
        # fits in a 32-bit unsigned integer.
        return f"""\
    const uint32_t sign_bit_mask = 1uL << {field.width - 1};
    int32_t {variable};
    if (result_shifted & sign_bit_mask)
    {{
      // Value is to be interpreted as negative.
      // This can be seen as a sign extension from the width of the field to the width of
      // the result variable.
      {variable} = result_shifted - 2 * sign_bit_mask;
    }}
    else
    {{
      // Value is positive.
      {variable} = result_shifted;
    }}
"""

    def _get_field_to_real(self, field: BitVector, field_type: str, variable: str) -> str:
        divisor = 2**field.numerical_interpretation.fraction_bit_width
        return f"""\
    const {field_type} result_real = static_cast<{field_type}>({variable});
    const {field_type} field_value = result_real / {divisor};
"""

    def _get_field_checker(self, field: str, setter_or_getter: Literal["setter", "getter"]) -> str:
        min_check, max_check = self._get_field_checker_limits(
            field=field, is_getter_not_setter=setter_or_getter == "getter"
        )

        checks: list[str] = []
        if min_check is not None:
            checks.append(f"field_value >= {min_check}")
        if max_check is not None:
            checks.append(f"field_value <= {max_check}")
        check = " && ".join(checks)

        if not check:
            return ""

        macro = f"_{setter_or_getter.upper()}_ASSERT_TRUE"
        return f"""\
    {macro}(
      {check},
      "Got '{field.name}' value out of range: " << field_value
    );

"""

    def _get_field_checker_limits(  # noqa: C901, PLR0911
        self, field: RegisterField, is_getter_not_setter: bool
    ) -> tuple[float | None, float | None]:
        """
        Return minimum and maximum values for checking.
        ``None`` if no check is needed.
        """
        width_matches_cpp_type = field.width == 32

        if isinstance(field, Bit):
            # Values is represented as boolean in C++, and in HDL it is a single bit.
            # Can not be out of range in either direction.
            return None, None

        if isinstance(field, BitVector):
            if is_getter_not_setter:
                # Result of bit slice can not be out of range by definition.
                return None, None

            if isinstance(field.numerical_interpretation, Unsigned):
                return (
                    # Min is always zero, and unsigned type is used in C++.
                    None,
                    None if width_matches_cpp_type else field.numerical_interpretation.max_value,
                )

            if isinstance(field.numerical_interpretation, Signed):
                return (
                    None if width_matches_cpp_type else field.numerical_interpretation.min_value,
                    None if width_matches_cpp_type else field.numerical_interpretation.max_value,
                )

            if isinstance(field.numerical_interpretation, (UnsignedFixedPoint, SignedFixedPoint)):
                # Value is represented as floating-point in C++, which is always a signed type.
                # And we have no guarantees about the range of the type.
                # Hence we must always check.
                return (
                    field.numerical_interpretation.min_value,
                    field.numerical_interpretation.max_value,
                )

            raise TypeError(
                f"Got unexpected numerical interpretation type: {field.numerical_interpretation}"
            )

        if isinstance(field, Enumeration):
            max_value = field.elements[-1].value

            _, max_is_native = self._get_checker_limits_are_native(
                field=field,
                min_value=0,
                max_value=max_value,
                is_signed=False,
            )

            if is_getter_not_setter:
                return (
                    None,
                    # Result of bit slice can not be out of range if native.
                    None if max_is_native else max_value,
                )

            return (
                # Assume that the C++ type used is unsigned.
                None,
                # In C++, while being typed, the setter argument could be out of range, regardless
                # if native limit or not.
                # We can not know the width of the C++ type used. Would depend on compiler/platform.
                max_value,
            )

        if isinstance(field, Integer):
            min_is_native, max_is_native = self._get_checker_limits_are_native(
                field=field,
                min_value=field.min_value,
                max_value=field.max_value,
                is_signed=field.is_signed,
            )

            if is_getter_not_setter:
                # Result of bit slice can not be out of range if native.
                return (
                    None if min_is_native else field.min_value,
                    None if max_is_native else field.max_value,
                )

            if field.is_signed:
                # Have to be checked in general, except for the corner case where
                # the field width matches the C++ type.
                return (
                    None if min_is_native and width_matches_cpp_type else field.min_value,
                    None if max_is_native and width_matches_cpp_type else field.max_value,
                )

            return (
                # Min is always zero, and unsigned type is used in C++.
                None,
                # Has to be checked in general, except for the corner case.
                None if max_is_native and width_matches_cpp_type else field.max_value,
            )

        raise TypeError(f"Got unexpected field type: {field}")

    def _get_checker_limits_are_native(
        self, field: RegisterField, min_value: float, max_value: float, is_signed: bool
    ) -> tuple[bool, bool]:
        if is_signed:
            native_min_value = -(2 ** (field.width - 1))
            native_max_value = 2 ** (field.width - 1) - 1
        else:
            native_min_value = 0
            native_max_value = 2**field.width - 1

        return min_value == native_min_value, max_value == native_max_value

    def _get_register_setter(self, register: Register, register_array: RegisterArray | None) -> str:
        comment = self._get_setter_comment(register=register)
        signature = self._register_setter_signature(
            register=register, register_array=register_array
        )

        if register.fields:
            cast = ""
            values: list[str] = []
            for field in register.fields:
                to_raw_name = self._field_to_raw_name(
                    register=register, register_array=register_array, field=field
                )
                cast += (
                    f"    const uint32_t {field.name}_value = "
                    f"{to_raw_name}(register_value.{field.name});\n"
                )
                values.append(f"{field.name}_value")

            value = " | ".join(values)
            cast += f"""\
    const uint32_t raw_value = {value};

"""
            set_raw_value = self._get_write_raw_value_call(
                register=register, register_array=register_array
            )
        else:
            cast = ""
            set_raw_value = self._get_write_raw_value_code(
                register=register, register_array=register_array
            )

        return f"""\
{comment}\
  void {self._class_name}::{signature}
  {{
{cast}\
{set_raw_value}\
  }}
"""

    def _get_write_raw_value_call(
        self, register: Register, register_array: RegisterArray | None
    ) -> str:
        setter_name = self._register_setter_name(
            register=register, register_array=register_array, raw=True
        )
        array_index = "array_index, " if register_array else ""
        return f"""\
    {setter_name}({array_index}raw_value);
"""

    def _get_write_raw_value_code(
        self,
        register: Register,
        register_array: RegisterArray | None,
        include_index: bool = True,
    ) -> str:
        index = (
            self._get_index(register=register, register_array=register_array)
            if include_index
            else ""
        )
        return f"""\
{index}\
    m_registers[index] = register_value;
"""

    def _get_register_raw_setter(
        self, register: Register, register_array: RegisterArray | None
    ) -> str:
        comment = self._get_setter_comment(register=register, raw=True)
        signature = self._register_setter_signature(
            register=register, register_array=register_array, raw=True
        )
        set_raw_value = self._get_write_raw_value_code(
            register=register, register_array=register_array
        )

        return f"""\
{comment}\
  void {self._class_name}::{signature}
  {{
{set_raw_value}\
  }}
"""

    def _get_field_setter(
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        comment = self._get_setter_comment(register=register, field=field)
        signature = self._field_setter_signature(
            register=register,
            register_array=register_array,
            field=field,
            from_raw=False,
        )
        index = self._get_index(register=register, register_array=register_array)

        if self.field_setter_should_read_modify_write(register=register):
            namespace = self._get_namespace(
                register=register, register_array=register_array, field=field
            )
            raw_value = self._get_read_raw_value_code(
                register=register, register_array=register_array, include_index=False
            )
            base_value = f"""\
{raw_value}\
    const uint32_t mask_shifted_inverse = ~{namespace}mask_shifted;
    const uint32_t base_value = raw_value & mask_shifted_inverse;
"""

        else:
            default_values = []
            for loop_field in register.fields:
                if loop_field.name != field.name:
                    namespace = self._get_namespace(
                        register=register, register_array=register_array, field=loop_field
                    )
                    default_values.append(f"{namespace}default_value_raw")

            # The '0' is needed in case there are no fields other than the one we are writing.
            default_value = " | ".join(default_values) if default_values else "0"
            base_value = f"""\
    const uint32_t base_value = {default_value};
"""

        to_raw_name = self._field_to_raw_name(
            register=register, register_array=register_array, field=field
        )
        write_raw_value = self._get_write_raw_value_code(
            register=register, register_array=register_array, include_index=False
        )

        return f"""\
{comment}\
  void {self._class_name}::{signature}
  {{
{index}
{base_value}\

    const uint32_t field_value_raw = {to_raw_name}(field_value);
    const uint32_t register_value = base_value | field_value_raw;

{write_raw_value}\
  }}
"""

    def _get_field_to_raw(
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        comment = self._get_to_raw_comment(field=field)
        signature = self._field_to_raw_signature(
            register=register, register_array=register_array, field=field
        )
        namespace = self._get_namespace(
            register=register, register_array=register_array, field=field
        )
        checker = self._get_field_checker(field=field, setter_or_getter="setter")
        cast, variable = self._get_to_raw_cast(
            register=register, register_array=register_array, field=field
        )

        return f"""\
{comment}\
  uint32_t {self._class_name}::{signature}
  {{
{checker}\
{cast}\
    const uint32_t field_value_shifted = {variable} << {namespace}shift;

    return field_value_shifted;
  }}
"""

    def _get_to_raw_cast(  # noqa: C901, PLR0911
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> tuple[str, str]:
        # Useful for values that are in an unsigned integer representation, but not
        # explicitly 'uint32_t'.
        cast_to_uint32 = """\
    const uint32_t field_value_casted = static_cast<uint32_t>(field_value);
"""

        def _get_reinterpret_as_uint32(variable: str = "field_value") -> str:
            # Reinterpret as unsigned and then mask out all the sign extended bits above
            # the field. Useful for signed integer values.
            # Signed to unsigned static cast produces no change in the bit pattern
            # https://stackoverflow.com/a/1751368
            namespace = self._get_namespace(
                register=register, register_array=register_array, field=field
            )
            return f"""\
    const uint32_t field_value_unsigned = (uint32_t){variable};
    const uint32_t field_value_masked = field_value_unsigned & {namespace}mask_at_base;
"""

        if isinstance(field, Bit):
            return (cast_to_uint32, "field_value_casted")

        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, Unsigned):
                return ("", "field_value")

            if isinstance(field.numerical_interpretation, Signed):
                return (_get_reinterpret_as_uint32(), "field_value_masked")

            value_type = self._get_field_value_type(
                register=register, register_array=register_array, field=field
            )
            multiplier = 2**field.numerical_interpretation.fraction_bit_width

            fixed_type = "int32_t" if field.numerical_interpretation.is_signed else "uint32_t"

            # Static cast implies truncation, which should guarantee that the
            # fixed-point representation fits in the field.
            to_fixed = f"""\
    const {value_type} field_value_multiplied = field_value * {multiplier};
    const {fixed_type} field_value_fixed = static_cast<{fixed_type}>(field_value_multiplied);
"""

            if isinstance(field.numerical_interpretation, UnsignedFixedPoint):
                return (to_fixed, "field_value_fixed")

            if isinstance(field.numerical_interpretation, SignedFixedPoint):
                return (
                    to_fixed + _get_reinterpret_as_uint32(variable="field_value_fixed"),
                    "field_value_masked",
                )

            raise TypeError(
                f"Got unexpected numerical interpretation: {field.numerical_interpretation}"
            )

        if isinstance(field, Enumeration):
            return (cast_to_uint32, "field_value_casted")

        if isinstance(field, Integer):
            if field.is_signed:
                return (_get_reinterpret_as_uint32(), "field_value_masked")

            return ("", "field_value")

        raise TypeError(f"Got unexpected field type: {field}")
