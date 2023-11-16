# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path

# First party libraries
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers
from hdl_registers.register_list import RegisterList


class CppGeneratorCommon(RegisterCodeGenerator, RegisterCodeGeneratorHelpers):
    """
    Class with common methods for generating C++ code.
    """

    COMMENT_START = "//"

    def __init__(self, register_list: RegisterList, output_folder: Path):
        super().__init__(register_list=register_list, output_folder=output_folder)

        self._class_name = self.to_pascal_case(snake_string=self.name)

    @staticmethod
    def _with_namespace(cpp_code_body):
        cpp_code = "namespace fpga_regs\n"
        cpp_code += "{\n\n"
        cpp_code += f"{cpp_code_body}"
        cpp_code += "} /* namespace fpga_regs */\n"
        return cpp_code

    def _constructor_signature(self):
        return f"{self._class_name}(volatile uint8_t *base_address)"

    @staticmethod
    def _array_length_constant_name(register_array):
        return f"{register_array.name}_array_length"

    def _get_methods_description(self, register, register_array):
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        return f"Methods for the {register_description}."

    def _field_value_type_name(self, register, register_array, field):
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
    def _register_getter_function_name(register, register_array):
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_getter_function_signature(self, register, register_array, indent=None):
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
    def _field_getter_function_name(register, register_array, field, from_value):
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}_{field.name}"

        if from_value:
            result += "_from_value"

        return result

    def _field_getter_function_signature(
        self, register, register_array, field, from_value, indent=None
    ):
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
    def _register_setter_function_name(register, register_array):
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_setter_function_signature(self, register, register_array, indent=None):
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
    def _field_setter_function_name(register, register_array, field, from_value):
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}_{field.name}"

        if from_value:
            result += "_from_value"

        return result

    def _field_setter_function_signature(
        self, register, register_array, field, from_value, indent=None
    ):
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
