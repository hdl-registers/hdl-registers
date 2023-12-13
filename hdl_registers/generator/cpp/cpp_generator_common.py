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
from typing import TYPE_CHECKING, Optional

# First party libraries
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.register_list import RegisterList

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class CppGeneratorCommon(RegisterCodeGenerator):
    """
    Class with common methods for generating C++ code.
    """

    COMMENT_START = "//"

    def __init__(self, register_list: RegisterList, output_folder: Path):
        super().__init__(register_list=register_list, output_folder=output_folder)

        self._class_name = self.to_pascal_case(snake_string=self.name)

    @staticmethod
    def _with_namespace(cpp_code_body: str) -> str:
        cpp_code = "namespace fpga_regs\n"
        cpp_code += "{\n\n"
        cpp_code += f"{cpp_code_body}"
        cpp_code += "} /* namespace fpga_regs */\n"
        return cpp_code

    def _constructor_signature(self) -> str:
        return f"{self._class_name}(volatile uint8_t *base_address)"

    def _get_methods_description(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        return f"Methods for the {register_description}."

    def _field_value_type_name(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
    ) -> str:
        """
        The name of the type used to represent the field.
        """
        if isinstance(field, Enumeration):
            # The name of an enum available in this field's attributes.
            result = f"{self.name}::"
            if register_array:
                result += f"{register_array.name}::"
            result += f"{register.name}::{field.name}::Enumeration"

            return result

        if isinstance(field, Integer) and field.is_signed:
            # Type that can represent negative values also.
            return "int32_t"

        # The default for most fields.
        return "uint32_t"

    @staticmethod
    def _register_getter_function_name(
        register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_getter_function_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        indent: Optional[int] = None,
    ) -> str:
        function_name = self._register_getter_function_name(
            register=register, register_array=register_array
        )
        result = f"{function_name}("

        if register_array:
            indentation = self.get_indentation(indent=indent)
            result += f"\n{indentation}  size_t array_index\n{indentation}"

        result += ")"

        return result

    @staticmethod
    def _field_getter_function_name(
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        from_value: bool,
    ) -> str:
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}_{field.name}"

        if from_value:
            result += "_from_value"

        return result

    def _field_getter_function_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        from_value: bool,
        indent: Optional[int] = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._field_getter_function_name(
            register=register, register_array=register_array, field=field, from_value=from_value
        )
        result = f"{function_name}("

        if from_value:
            # Value is supplied by user
            result += f"\n{indentation}  uint32_t register_value\n{indentation}"
        elif register_array:
            # Value shall be read from bus, in which case we need to know array index if this
            # is an array
            result += f"\n{indentation}  size_t array_index\n{indentation}"

        result += ")"

        return result

    @staticmethod
    def _register_setter_function_name(
        register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_setter_function_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        indent: Optional[int] = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._register_setter_function_name(
            register=register, register_array=register_array
        )
        result = f"{function_name}(\n"

        if register_array:
            result += f"{indentation}  size_t array_index,\n"

        result += f"{indentation}  uint32_t register_value\n{indentation})"

        return result

    @staticmethod
    def _field_setter_function_name(
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        from_value: bool,
    ) -> str:
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}_{field.name}"

        if from_value:
            result += "_from_value"

        return result

    def _field_setter_function_signature(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        field: "RegisterField",
        from_value: bool,
        indent: Optional[int] = None,
    ) -> str:
        indentation = self.get_indentation(indent=indent)

        function_name = self._field_setter_function_name(
            register=register, register_array=register_array, field=field, from_value=from_value
        )
        result = f"{function_name}(\n"

        if from_value:
            # Current register value is supplied by user
            result += f"{indentation}  uint32_t register_value,\n"
        elif register_array:
            # Current register value shall be read from bus, in which case we need to know array
            # index if this is an array
            result += f"{indentation}  size_t array_index,\n"

        type_name = self._field_value_type_name(
            register=register, register_array=register_array, field=field
        )
        result += f"{indentation}  {type_name} field_value\n{indentation})"

        return result
