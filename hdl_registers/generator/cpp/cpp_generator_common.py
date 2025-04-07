# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING

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
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator

if TYPE_CHECKING:
    from pathlib import Path

    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray
    from hdl_registers.register_list import RegisterList


class CppGeneratorCommon(RegisterCodeGenerator):
    """
    Class with common methods for generating C++ code.
    """

    COMMENT_START = "//"

    def __init__(self, register_list: RegisterList, output_folder: Path) -> None:
        super().__init__(register_list=register_list, output_folder=output_folder)

        self._class_name = self.to_pascal_case(snake_string=self.name)

    @staticmethod
    def _with_namespace(cpp_code_body: str) -> str:
        return f"""\
namespace fpga_regs
{{

{cpp_code_body}\
}} // namespace fpga_regs
"""

    def _constructor_signature(self) -> str:
        return (
            f"{self._class_name}(uintptr_t base_address, "
            "bool (*assertion_handler) (const std::string*))"
        )

    def _get_register_heading(
        self,
        register: Register,
        register_array: RegisterArray | None,
        separator: str,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)
        description = self._get_methods_description(
            register=register, register_array=register_array
        )
        return f"""
{separator}\
{indentation}// {description}
{indentation}// Mode '{register.mode.name}'.
{separator}\
"""

    def _get_methods_description(
        self, register: Register, register_array: RegisterArray | None
    ) -> str:
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        return f"Methods for the {register_description}."

    def _get_namespace(
        self,
        register: Register,
        register_array: RegisterArray | None = None,
        field: RegisterField | None = None,
    ) -> str:
        """
        Get namespace to use within the class for the attributes of the field or register that is
        pointed out by the arguments.
        """
        register_array_namespace = f"{register_array.name}::" if register_array else ""
        field_namespace = f"{field.name}::" if field else ""
        return f"{self.name}::{register_array_namespace}{register.name}::{field_namespace}"

    def _get_register_value_type(
        self, register: Register, register_array: RegisterArray | None
    ) -> str:
        """
        The name of the type used to represent the register value.
        """
        if register.fields:
            namespace = self._get_namespace(register=register, register_array=register_array)
            return f"{namespace}Value"

        return "uint32_t"

    def _get_field_value_type(
        self,
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        include_namespace: bool = True,
    ) -> str:
        """
        The name of the type used to represent the field value.
        """
        if isinstance(field, Bit):
            return "bool"

        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, Unsigned):
                return "uint32_t"

            if isinstance(field.numerical_interpretation, Signed):
                return "int32_t"

            if isinstance(field.numerical_interpretation, (UnsignedFixedPoint, SignedFixedPoint)):
                # This assumes that the target platform/compiler uses IEEE-754 single-precision for
                # 'float' and IEEE-754 double-precision for 'double'.
                # This is NOT guaranteed by the C++ standard.
                # The user is encouraged to check their platform's limits
                # with e.g. 'std::numeric_limits<float>::is_iec559'.
                # https://stackoverflow.com/questions/24157094
                return "double" if field.width > 24 else "float"

            raise ValueError(
                f"Unsupported numerical interpretation: {field.numerical_interpretation}"
            )

        if isinstance(field, Enumeration):
            # The name of an enum available in this field's attributes.
            namespace = (
                self._get_namespace(register=register, register_array=register_array, field=field)
                if include_namespace
                else ""
            )
            return f"{namespace}Enumeration"

        if isinstance(field, Integer):
            return "int32_t" if field.is_signed else "uint32_t"

        raise ValueError(f"Got unknown field type: {field}")

    @staticmethod
    def _register_getter_name(
        register: Register, register_array: RegisterArray | None, raw: bool
    ) -> str:
        register_array_name = f"_{register_array.name}" if register_array else ""
        raw_name = "_raw" if raw else ""
        return f"get{register_array_name}_{register.name}{raw_name}"

    def _register_getter_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        raw: bool = False,
        indent: int | None = None,
    ) -> str:
        function_name = self._register_getter_name(
            register=register, register_array=register_array, raw=raw
        )

        if register_array:
            indentation = self.get_indentation(indent=indent)
            array_index = f"""
{indentation}  size_t array_index
{indentation}\
"""
        else:
            array_index = ""

        return f"{function_name}({array_index}) const"

    @staticmethod
    def _field_getter_name(
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
    ) -> str:
        register_array_name = f"_{register_array.name}" if register_array else ""
        raw_name = "_from_raw" if from_raw else ""
        return f"get{register_array_name}_{register.name}_{field.name}{raw_name}"

    def _field_getter_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._field_getter_name(
            register=register, register_array=register_array, field=field, from_raw=from_raw
        )
        result = f"{function_name}("

        if from_raw:
            # Value is supplied by user
            result += f"\n{indentation}  uint32_t register_value\n{indentation}"
        elif register_array:
            # Value shall be read from bus, in which case we need to know array index if this
            # is an array
            result += f"\n{indentation}  size_t array_index\n{indentation}"

        result += ") const"

        return result

    @staticmethod
    def _field_to_raw_name(
        register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        array = f"{register_array.name}_" if register_array else ""
        return f"get_{array}{register.name}_{field.name}_to_raw"

    def _field_to_raw_signature(
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        field_type = self._get_field_value_type(
            register=register, register_array=register_array, field=field
        )
        function_name = self._field_to_raw_name(
            register=register, register_array=register_array, field=field
        )
        return f"{function_name}({field_type} field_value) const"

    @staticmethod
    def _register_setter_name(
        register: Register, register_array: RegisterArray | None, raw: bool
    ) -> str:
        array_name = f"_{register_array.name}" if register_array else ""
        raw_name = "_raw" if raw else ""

        return f"set{array_name}_{register.name}{raw_name}"

    def _register_setter_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        raw: bool = False,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._register_setter_name(
            register=register, register_array=register_array, raw=raw
        )

        array_index = f"{indentation}  size_t array_index,\n" if register_array else ""
        value_type = (
            "uint32_t"
            if raw
            else self._get_register_value_type(register=register, register_array=register_array)
        )

        return f"""\
{function_name}(
{array_index}\
{indentation}  {value_type} register_value
{indentation}) const\
"""

    @staticmethod
    def _field_setter_name(
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
    ) -> str:
        register_array_name = f"_{register_array.name}" if register_array else ""
        from_raw_name = "_from_raw" if from_raw else ""
        return f"set{register_array_name}_{register.name}_{field.name}{from_raw_name}"

    def _field_setter_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._field_setter_name(
            register=register, register_array=register_array, field=field, from_raw=from_raw
        )
        result = f"{function_name}(\n"

        if from_raw:
            # Current register value is supplied by user
            result += f"{indentation}  uint32_t register_value,\n"
        elif register_array:
            # Current register value shall be read from bus, in which case we need to know array
            # index if this is an array
            result += f"{indentation}  size_t array_index,\n"

        field_type = self._get_field_value_type(
            register=register, register_array=register_array, field=field
        )
        result += f"{indentation}  {field_type} field_value\n{indentation}) const"

        return result

    def _get_getter_comment(self, field: RegisterField | None = None, raw: bool = False) -> str:
        """
        Generate a comment for getter method documentation.
        """
        if field:
            if raw:
                raise ValueError("Invalid arguments")

            return self.comment(
                comment=f"Read the register and slice out the '{field.name}' field value.",
            )

        comment = ["Read the whole register value over the register bus."]
        if raw:
            comment.append(
                "This method returns the raw register value without any type conversion."
            )

        return self.comment_block(text=comment)

    def _get_setter_comment(
        self, register: Register, field: RegisterField | None = None, raw: bool = False
    ) -> str:
        """
        Generate a comment for setter method documentation.
        """
        if field:
            if raw:
                raise ValueError("Invalid arguments")

            comment = [f"Write the '{field.name}' field value."]
            if self.field_setter_should_read_modify_write(register=register):
                comment.append("Will read-modify-write the register.")
            else:
                comment.append("Will write the register with all other fields set as default.")

            return self.comment_block(text=comment)

        comment = ["Write the whole register value over the register bus."]

        if raw:
            comment.append(
                "This method takes a raw register value and does not perform any type conversion."
            )

        return self.comment_block(text=comment)

    def _get_from_raw_comment(self, field: RegisterField) -> str:
        """
        Generate a comment for a ``get_<field>_from_raw`` method documentation.
        """
        return self.comment_block(
            text=[
                f"Slice out the '{field.name}' field value from a given raw register value.",
                "Performs no operation on the register bus.",
            ]
        )

    def _get_to_raw_comment(self, field: RegisterField) -> str:
        """
        Generate a comment for a ``get_<field>_to_raw`` method documentation.
        """
        return self.comment_block(
            text=[
                f"Get the raw representation of a given '{field.name}' field value.",
                "Performs no operation on the register bus.",
            ]
        )
