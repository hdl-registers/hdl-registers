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
        if isinstance(field, (Bit, BitVector)):
            return "uint32_t"

        if isinstance(field, Enumeration):
            if include_namespace:
                namespace = self._get_namespace(
                    register=register, register_array=register_array, field=field
                )
            else:
                namespace = ""

            # The name of an enum available in this field's attributes.
            return f"{namespace}Enumeration"

        if isinstance(field, Integer):
            return "int32_t" if field.is_signed else "uint32_t"

        raise ValueError(f"Got unknown field type: {field}")

    @staticmethod
    def _register_getter_function_name(
        register: Register, register_array: RegisterArray | None
    ) -> str:
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_getter_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        indent: int | None = None,
    ) -> str:
        function_name = self._register_getter_function_name(
            register=register, register_array=register_array
        )
        result = f"{function_name}("

        if register_array:
            indentation = self.get_indentation(indent=indent)
            result += f"\n{indentation}  size_t array_index\n{indentation}"

        result += ") const"

        return result

    @staticmethod
    def _field_getter_function_name(
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
    ) -> str:
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}_{field.name}"

        if from_raw:
            result += "_from_raw"

        return result

    def _field_getter_function_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._field_getter_function_name(
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
    def _field_to_raw_function_name(
        register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        array = f"{register_array.name}_" if register_array else ""
        return f"get_{array}{register.name}_{field.name}_to_raw"

    def _field_to_raw_function_signature(
        self, register: Register, register_array: RegisterArray | None, field: RegisterField
    ) -> str:
        field_type = self._get_field_value_type(
            register=register, register_array=register_array, field=field
        )
        function_name = self._field_to_raw_function_name(
            register=register, register_array=register_array, field=field
        )
        return f"{function_name}({field_type} field_value) const"

    @staticmethod
    def _register_setter_function_name(
        register: Register, register_array: RegisterArray | None
    ) -> str:
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_setter_function_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._register_setter_function_name(
            register=register, register_array=register_array
        )

        array_index = f"{indentation}  size_t array_index,\n" if register_array else ""
        value_type = self._get_register_value_type(register=register, register_array=register_array)

        return f"""\
{function_name}(
{array_index}\
{indentation}  {value_type} register_value
{indentation}) const\
"""

    @staticmethod
    def _field_setter_function_name(
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
    ) -> str:
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}_{field.name}"

        if from_raw:
            result += "_from_raw"

        return result

    def _field_setter_function_signature(
        self,
        register: Register,
        register_array: RegisterArray | None,
        field: RegisterField,
        from_raw: bool,
        indent: int | None = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._field_setter_function_name(
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

    def _get_getter_comment(self, field: RegisterField | None = None) -> str:
        """
        Generate a comment for getter method documentation.
        """
        if field:
            return self.comment(
                comment=f"Read the register and slice out the '{field.name}' field value.",
            )

        return self.comment(comment="Read the whole register value over the register bus.")

    def _get_setter_comment(self, register: Register, field: RegisterField | None = None) -> str:
        """
        Generate a comment for setter method documentation.
        """
        if field:
            comment = [f"Write the '{field.name}' field value."]
            if self.field_setter_should_read_modify_write(register=register):
                comment.append("Will read-modify-write the register.")
            else:
                comment.append("Will write the register with all other fields set as default.")

            return self.comment_block(text=comment)

        return self.comment(comment="Write the whole register value over the register bus.")

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
