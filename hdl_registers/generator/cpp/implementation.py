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
        file_name = self.output_file.name

        def get_macro(name: str) -> str:
            macro_name = f"_{name}_ASSERT_TRUE"
            guard_name = f"NO_REGISTER_{name}_ASSERT"
            name_space = " " * (38 - len(name))
            file_name_space = " " * (44 - len(file_name))
            base = """\
#ifdef {guard_name}

#define {macro_name}(expression, message) ((void)0)

#else // Not {guard_name}.

// This macro is called by the register code to check for runtime errors.
#define {macro_name}(expression, message) {name_space}\\
  {{                                                                              \\
    if (!static_cast<bool>(expression)) {{                                        \\
      std::ostringstream diagnostics;                                            \\
      diagnostics << "{file_name}:" << __LINE__ {file_name_space}\\
                  << ": " << message << ".";                                     \\
      std::string diagnostic_message = diagnostics.str();                        \\
      m_assertion_handler(&diagnostic_message);                                  \\
    }}                                                                            \\
  }}

#endif // {guard_name}.
"""
            return base.format(
                guard_name=guard_name,
                macro_name=macro_name,
                name=name,
                name_space=name_space,
                file_name=file_name,
                file_name_space=file_name_space,
            )

        setter_assert = get_macro(name="SETTER")
        getter_assert = get_macro(name="GETTER")
        array_index_assert = get_macro(name="ARRAY_INDEX")
        return f"""\
{setter_assert}
{getter_assert}
{array_index_assert}
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

    def _get_field_checker(
        self, field: RegisterField, setter_or_getter: Literal["setter", "getter"]
    ) -> str:
        if isinstance(field, Bit):
            # Values is represented as boolean in C++, and in HDL it is a single bit.
            # Can not be out of range in either direction.
            return ""

        if isinstance(field, BitVector):
            if setter_or_getter == "getter":
                # HDL can by definition not use bits outside the field.
                return ""

            # If the maximum value is the natural maximum value of the field, this check is moot.
            # Add guard for this in the future.
            # https://github.com/hdl-registers/hdl-registers/issues/169
            max_value = field.numerical_interpretation.max_value

            # Minimum value check would be moot if unsigned, since the C++ type used will
            # be 'uint32_t'.
            min_value = (
                None
                if isinstance(field.numerical_interpretation, Unsigned)
                else field.numerical_interpretation.min_value
            )

            return self._get_checker(
                field_name=field.name,
                setter_or_getter=setter_or_getter,
                min_value=min_value,
                max_value=max_value,
            )

        if isinstance(field, Enumeration):
            # There should be a check that getter value is within range.
            # Unless, the maximum value is the natural maximum value of the field.
            # https://github.com/hdl-registers/hdl-registers/issues/169
            return ""

        if isinstance(field, Integer):
            # If the maximum value is the natural maximum value of the field, this check is moot.
            # But only for getters, the setter can still be out of range
            # unless the field width is 32.
            # Add guard for this in the future.
            # https://github.com/hdl-registers/hdl-registers/issues/169
            max_value = field.max_value

            # Minimum value check would be moot if unsigned and minimum value zero, since the C++
            # type used will be 'uint32_t'.
            # Note that there is the case where the field is unsigned, but has a minimum allowed
            # value that is greater than zero.
            # In that case, the minimum value check is still needed.
            #
            # If the minimum value is the natural minimum value of the field, signed or unsigned,
            # this check is moot.
            # Add guard for this in the future.
            # https://github.com/hdl-registers/hdl-registers/issues/169
            min_value = field.min_value if field.is_signed or field.min_value != 0 else None

            return self._get_checker(
                field_name=field.name,
                setter_or_getter=setter_or_getter,
                min_value=min_value,
                max_value=max_value,
            )

        raise TypeError(f"Got unexpected field type: {field}")

    def _get_checker(
        self,
        field_name: str,
        setter_or_getter: Literal["setter", "getter"],
        min_value: str | None = None,
        max_value: str | None = None,
    ) -> str:
        checks: list[str] = []
        if min_value is not None:
            checks.append(f"field_value >= {min_value}")
        if max_value is not None:
            checks.append(f"field_value <= {max_value}")
        check = " && ".join(checks)

        if not check:
            return ""

        macro = f"_{setter_or_getter.upper()}_ASSERT_TRUE"

        return f"""\
    {macro}(
      {check},
      "Got '{field_name}' value out of range: " << field_value
    );

"""

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
            # The '0' is needed in case there are no other fields than the one we are writing.
            default_values = ["0"]
            for loop_field in register.fields:
                if loop_field.name != field.name:
                    namespace = self._get_namespace(
                        register=register, register_array=register_array, field=loop_field
                    )
                    default_values.append(f"{namespace}default_value_raw")

            default_value = " | ".join(default_values)
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
