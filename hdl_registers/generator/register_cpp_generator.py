# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

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
from hdl_registers.register import REGISTER_MODES
from hdl_registers.register_array import RegisterArray

# Local folder libraries
from .register_code_generator import RegisterCodeGenerator


class RegisterCppGenerator:
    """
    Generate a C++ class with register definitions and methods.

    There is only a very limited unit test of this class that checks the generated code.
    It is instead functionally tested in the file test_register_compilation.py.
    That test generates C++ code from an example register set, compiles it and performs some
    run-time assertions in a C++ program.
    That test is considered more meaningful and exhaustive than a unit test would be.
    """

    def __init__(self, module_name, generated_info):
        """
        Arguments:
            module_name (str): The name of the register map.
            generated_info (list(str)): Will be placed in the file headers.
        """
        self.module_name = module_name
        self.generated_info = generated_info

    def get_interface(self, register_objects, constants):
        """
        Get a complete C++ interface class header with all constant values and the signatures of
        all methods.

        Arguments:
            register_objects (list): Register arrays and registers to be included.
            constants (list(Constant)): Constants to be included.

        Returns:
            str: C++ code.
        """
        generator = InterfaceGenerator(
            module_name=self.module_name, generated_info=self.generated_info
        )
        return generator.get_interface(register_objects=register_objects, constants=constants)

    def get_header(self, register_objects):
        """
        Get a complete C++ class header for the implementation of all methods.

        Arguments:
            register_objects (list): Register arrays and registers to be included.

        Returns:
            str: C++ code.
        """
        generator = HeaderGenerator(
            module_name=self.module_name, generated_info=self.generated_info
        )
        return generator.get_header(register_objects=register_objects)

    def get_implementation(self, register_objects):
        """
        Get a complete C++ class implementation with all methods.

        Arguments:
            register_objects (list): Register arrays and registers to be included.

        Returns:
            str: C++ code.
        """
        generator = ImplementationGenerator(
            module_name=self.module_name, generated_info=self.generated_info
        )
        return generator.get_implementation(register_objects=register_objects)


class CommonGenerator(RegisterCodeGenerator):
    """
    Class with common methods for generating C++ code.
    Do not use this directly, should use :class:`.RegisterCppGenerator`:
    """

    # The most commonly used indentation.
    # The one used inside e.g. a class inside a namespace.
    default_indent = 4

    def __init__(self, module_name, generated_info):
        self.module_name = module_name

        self._class_name = self._to_pascal_case(module_name)
        self._file_header = "".join(
            [self._comment(header_line, indent=0) for header_line in generated_info]
        )

    @staticmethod
    def _get_separator_line(indent=default_indent):
        """
        Get a separator line, e.g. "  // ---------------------------------\n"
        """
        indentation = " " * indent
        result = f"{indentation}// "

        num_dash = 80 - len(result)
        result += "-" * num_dash
        result += "\n"
        return result

    @staticmethod
    def _comment(comment, indent=default_indent):
        """
        Defaults to the most commonly used indentation.
        """
        indentation = " " * indent
        return f"{indentation}// {comment}\n"

    def _comment_block(self, text, indent=default_indent):
        """
        Defaults to the most commonly used indentation.
        """
        return super()._comment_block(text=text, indent=indent)

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

    @staticmethod
    def _get_methods_description(register, register_array):
        result = f'Methods for the "{register.name}" register'
        if register_array:
            result += f' within the "{register_array.name}" register array'
        result += "."

        return result

    def _field_value_type_name(self, register, register_array, field):
        """
        The name of the type used to represent the field.
        """
        if isinstance(field, Enumeration):
            # The name of an enum available in this field's attributes.
            result = f"{self.module_name}::"
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

    def _register_getter_function_signature(self, register, register_array, indent=default_indent):
        function_name = self._register_getter_function_name(
            register=register, register_array=register_array
        )
        result = f"{function_name}("

        if register_array:
            indentation = " " * indent
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
        self, register, register_array, field, from_value, indent=default_indent
    ):
        indentation = " " * indent

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
    def _get_shift_and_mask(field):
        cpp_code = f"    const uint32_t shift = {field.base_index}uL;\n"
        cpp_code += f'    const uint32_t mask_at_base = 0b{"1" * field.width}uL;\n'
        cpp_code += "    const uint32_t mask_shifted = mask_at_base << shift;\n"
        cpp_code += "\n"
        return cpp_code

    @staticmethod
    def _get_checker(field):
        if isinstance(field, Integer):
            cpp_code = "    // Check that provided value is within the legal range of this field.\n"
            cpp_code += f"    assert(field_value >= {field.min_value});\n"
            cpp_code += f"    assert(field_value <= {field.max_value});\n"
            cpp_code += "\n"
            return cpp_code

        return ""

    @staticmethod
    def _register_setter_function_name(register, register_array):
        result = "set"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_setter_function_signature(self, register, register_array, indent=default_indent):
        indentation = " " * indent

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
        self, register, register_array, field, from_value, indent=default_indent
    ):
        indentation = " " * indent

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


class InterfaceGenerator(CommonGenerator):
    """
    Class to generate a C++ interface header.
    Do not use this directly, should use :class:`.RegisterCppGenerator`:
    """

    def get_interface(self, register_objects, constants):
        """
        Get a complete C++ interface class header. See :meth:`.RegisterCppGenerator.get_interface`
        for more details.
        """
        cpp_code = ""

        for register, register_array in self._iterate_registers(register_objects):
            field_cpp_code = ""

            for field in register.fields:
                field_cpp_code += self._field_attributes(
                    register=register, register_array=register_array, field=field
                )

            cpp_code += field_cpp_code
            if field_cpp_code:
                cpp_code += "\n"

        cpp_code += f"  class I{self._class_name}\n"
        cpp_code += "  {\n"
        cpp_code += "  public:\n"

        cpp_code += self._constants(constants=constants)

        cpp_code += self._num_registers(register_objects)

        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                cpp_code += self._comment(f'Length of the "{register_object.name}" register array')
                constant_name = self._array_length_constant_name(register_object)
                cpp_code += (
                    f"    static const size_t {constant_name} = {register_object.length}uL;\n\n"
                )

        cpp_code += f"    virtual ~I{self._class_name}() {{}}\n\n"

        for register, register_array in self._iterate_registers(register_objects):
            cpp_code += f"{self._get_separator_line()}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            description += f' Mode "{REGISTER_MODES[register.mode].mode_readable}".'

            cpp_code += self._comment(comment=description)
            cpp_code += "\n"

            if register.is_bus_readable:
                cpp_code += self._comment(
                    "Getter that will read the whole register's value over the register bus."
                )
                signature = self._register_getter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += f"    virtual uint32_t {signature} const = 0;\n\n"

            if register.is_bus_writeable:
                cpp_code += self._comment(
                    "Setter that will write the whole register's value over the register bus."
                )
                signature = self._register_setter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += f"    virtual void {signature} const = 0;\n\n"

            cpp_code += self._field_interface(register, register_array)

        cpp_code += "  };\n\n"

        cpp_code_top = f"""\
{self._file_header}
#pragma once

#include <cassert>
#include <cstdint>
#include <cstdlib>

"""
        return cpp_code_top + self._with_namespace(cpp_code)

    def _constants(self, constants):
        cpp_code = ""

        for constant in constants:
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

            cpp_code += self._comment("Register constant.")
            cpp_code += f"    static const{type_declaration} {constant.name} = {value};\n"

        if constants:
            cpp_code += "\n"

        return cpp_code

    def _num_registers(self, register_objects):
        # It is possible that we have constants but no registers
        num_registers = 0
        if register_objects:
            num_registers = register_objects[-1].index + 1

        cpp_code = self._comment("Number of registers within this register map.")
        cpp_code += f"    static const size_t num_registers = {num_registers}uL;\n\n"
        return cpp_code

    @staticmethod
    def _field_description(register, register_array, field):
        result = f'the "{field.name}" field in the "{register.name}" register'
        if register_array is not None:
            result += f' within the "{register_array.name}" register array'

        return result

    def _field_interface(self, register, register_array):
        def function(return_type_name, signature):
            return f"    virtual {return_type_name} {signature} const = 0;\n"

        cpp_code = ""
        for field in register.fields:
            field_description = self._field_description(
                register=register, register_array=register_array, field=field
            )
            field_type_name = self._field_value_type_name(
                register=register, register_array=register_array, field=field
            )

            if register.is_bus_readable:
                comment = (
                    f"Getter for {field_description},\n"
                    "which will read register value over the register bus."
                )

                cpp_code += self._comment_block(text=comment)

                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=False,
                )
                cpp_code += function(return_type_name=field_type_name, signature=signature)

                comment = f"Getter for {field_description},\ngiven the register's current value."
                cpp_code += self._comment_block(text=comment)

                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=True,
                )
                cpp_code += function(return_type_name=field_type_name, signature=signature)

            if register.is_bus_writeable:
                comment = f"Setter for {field_description},\n"
                if register.mode == "r_w":
                    comment += "which will read-modify-write over the register bus."
                elif register.mode in ["w", "wpulse", "r_wpulse"]:
                    comment += (
                        "which will set the field to the given value, and all other bits to zero."
                    )
                else:
                    raise ValueError(f"Can not handle this register's mode: {register}")

                cpp_code += self._comment_block(text=comment)

                signature = self._field_setter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=False,
                )
                cpp_code += function(return_type_name="void", signature=signature)

                comment = (
                    f"Setter for {field_description},\n"
                    "given the register's current value, which will return an updated value."
                )
                cpp_code += self._comment_block(text=comment)

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
    def _get_default_value(field):
        """
        Get the field's default value formatted in a way suitable for C++ code.
        """
        if isinstance(field, (Bit, BitVector)):
            return f"0b{field.default_value}"

        if isinstance(field, Enumeration):
            return f"Enumeration::{field.default_value.name}"

        if isinstance(field, Integer):
            return field.default_value

        raise ValueError(f'Unknown field type for "{field.name}" field: {type(field)}')

    def _field_attributes(self, register, register_array, field):
        field_description = self._field_description(
            register=register, register_array=register_array, field=field
        )
        cpp_code = self._comment_block(text=f"Attributes for {field_description}.", indent=2)

        array_namespace = f"::{register_array.name}" if register_array else ""
        namespace = f"{self.module_name}{array_namespace}::{register.name}::{field.name}"

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


class HeaderGenerator(CommonGenerator):
    """
    Class to generate a C++ header.
    Do not use this directly, should use :class:`.RegisterCppGenerator`:
    """

    def get_header(self, register_objects):
        """
        Get a complete C++ class header for the implementation of all methods.
        See :meth:`.RegisterCppGenerator.get_header` for more details.
        """
        cpp_code = f"  class {self._class_name} : public I{self._class_name}\n"
        cpp_code += "  {\n"

        cpp_code += "  private:\n"
        cpp_code += "    volatile uint32_t *m_registers;\n\n"

        cpp_code += "  public:\n"
        cpp_code += f"    {self._constructor_signature()};\n\n"
        cpp_code += f"    virtual ~{self._class_name}() {{}}\n"

        def function(return_type_name, signature):
            return f"    virtual {return_type_name} {signature} const override;\n"

        for register, register_array in self._iterate_registers(register_objects):
            cpp_code += f"\n{self._get_separator_line()}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            cpp_code += self._comment_block(
                text=f"{description}\nSee interface header for documentation."
            )

            if register.is_bus_readable:
                signature = self._register_getter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += function(return_type_name="uint32_t", signature=signature)

                for field in register.fields:
                    field_type_name = self._field_value_type_name(
                        register=register, register_array=register_array, field=field
                    )

                    signature = self._field_getter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=False,
                    )
                    cpp_code += function(return_type_name=field_type_name, signature=signature)

                    signature = self._field_getter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=True,
                    )
                    cpp_code += function(return_type_name=field_type_name, signature=signature)

            if register.is_bus_writeable:
                signature = self._register_setter_function_signature(
                    register=register, register_array=register_array
                )

                cpp_code += function(return_type_name="void", signature=signature)

                for field in register.fields:
                    signature = self._field_setter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=False,
                    )
                    cpp_code += function(return_type_name="void", signature=signature)

                    signature = self._field_setter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=True,
                    )
                    cpp_code += function(return_type_name="uint32_t", signature=signature)

        cpp_code += "  };\n"

        cpp_code_top = f"""\
{self._file_header}
#pragma once

#include "i_{self.module_name}.h"

"""
        return cpp_code_top + self._with_namespace(cpp_code)


class ImplementationGenerator(CommonGenerator):
    """
    Class to generate a C++ implementation.
    Do not use this directly, should use :class:`.RegisterCppGenerator`:
    """

    def get_implementation(self, register_objects):
        """
        Get a complete C++ class implementation with all methods.
        See :meth:`.RegisterCppGenerator.get_implementation` for more details.
        """
        cpp_code = f"  {self._class_name}::{self._constructor_signature()}\n"
        cpp_code += "      : m_registers(reinterpret_cast<volatile uint32_t *>(base_address))\n"
        cpp_code += "  {\n"
        cpp_code += "    // Empty\n"
        cpp_code += "  }\n\n"

        for register, register_array in self._iterate_registers(register_objects):
            cpp_code += f"{self._get_separator_line(indent=2)}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            cpp_code += self._comment_block(
                text=f"{description}\nSee interface header for documentation.", indent=2
            )
            cpp_code += "\n"

            if register.is_bus_readable:
                cpp_code += self._register_getter_function(register, register_array)

                for field in register.fields:
                    cpp_code += self._field_getter_function(register, register_array, field=field)
                    cpp_code += self._field_getter_function_from_value(
                        register, register_array, field=field
                    )

            if register.is_bus_writeable:
                cpp_code += self._register_setter_function(register, register_array)

                for field in register.fields:
                    cpp_code += self._field_setter_function(register, register_array, field=field)
                    cpp_code += self._field_setter_function_from_value(
                        register, register_array, field=field
                    )

        cpp_code_top = f"{self._file_header}\n"
        cpp_code_top += f'#include "include/{self.module_name}.h"\n\n'

        return cpp_code_top + self._with_namespace(cpp_code)

    def _register_setter_function(self, register, register_array):
        signature = self._register_setter_function_signature(
            register=register, register_array=register_array, indent=2
        )
        cpp_code = f"  void {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        if register_array:
            cpp_code += (
                f"    assert(array_index < {self._array_length_constant_name(register_array)});\n"
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

    def _field_setter_function(self, register, register_array, field):
        signature = self._field_setter_function_signature(
            register=register,
            register_array=register_array,
            field=field,
            from_value=False,
            indent=2,
        )

        cpp_code = f"  void {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        if register.mode == "r_w":
            register_getter_function_name = self._register_getter_function_name(
                register=register, register_array=register_array
            )
            cpp_code += self._comment(
                comment="Get the current value of any other fields by reading register on the bus."
            )
            current_register_value = f"{register_getter_function_name}("
            if register_array:
                current_register_value += "array_index"
            current_register_value += ")"
        elif register.mode in ["w", "wpulse", "r_wpulse"]:
            cpp_code += self._comment_block(
                "This register type's currently written value can not be read back.\n"
                "Hence set all other bits to zero when writing the value."
            )
            current_register_value = 0
        else:
            raise ValueError(f"Can not handle this register's mode: {register}")

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

    def _field_setter_function_from_value(self, register, register_array, field):
        signature = self._field_setter_function_signature(
            register=register, register_array=register_array, field=field, from_value=True, indent=2
        )

        cpp_code = f"  uint32_t {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"
        cpp_code += self._get_shift_and_mask(field=field)
        cpp_code += self._get_checker(field=field)

        cpp_code += "    const uint32_t field_value_masked = field_value & mask_at_base;\n"
        cpp_code += (
            "    const uint32_t field_value_masked_and_shifted = field_value_masked << shift;\n\n"
        )

        cpp_code += "    const uint32_t mask_shifted_inverse = ~mask_shifted;\n"
        cpp_code += (
            "    const uint32_t register_value_masked = register_value & mask_shifted_inverse;\n\n"
        )

        cpp_code += (
            "    const uint32_t result_register_value = "
            "register_value_masked | field_value_masked_and_shifted;\n\n"
        )
        cpp_code += "    return result_register_value;\n"

        cpp_code += "  }\n\n"

        return cpp_code

    def _register_getter_function(self, register, register_array):
        signature = self._register_getter_function_signature(
            register=register, register_array=register_array, indent=2
        )
        cpp_code = f"  uint32_t {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        if register_array:
            cpp_code += (
                f"    assert(array_index < {self._array_length_constant_name(register_array)});\n"
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

    def _field_getter_function(self, register, register_array, field):
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
            f"    const {field_type_name} result = "
            f"{field_getter_from_value_function_name}(register_value);\n"
        )
        cpp_code += "\n    return result;\n"
        cpp_code += "  }\n\n"

        return cpp_code

    def _field_getter_function_from_value(self, register, register_array, field):
        signature = self._field_getter_function_signature(
            register=register, register_array=register_array, field=field, from_value=True, indent=2
        )

        type_name = self._field_value_type_name(
            register=register, register_array=register_array, field=field
        )

        cpp_code = f"  {type_name} {self._class_name}::{signature} const\n"
        cpp_code += "  {\n"

        cpp_code += self._get_shift_and_mask(field=field)

        cpp_code += "    const uint32_t result_masked = register_value & mask_shifted;\n"
        cpp_code += "    const uint32_t result_shifted = result_masked >> shift;\n\n"

        if type_name == "uint32_t":
            # No casting needed, simply return the value.
            cpp_code += "    return result_shifted;\n"

        else:
            if isinstance(field, Enumeration):
                # "Cast" to the enum type.
                cpp_code += f"    const auto result = {type_name}(result_shifted);\n\n"
            elif isinstance(field, Integer) and field.is_signed:
                cpp_code += f"""\
    const {type_name} sign_bit_mask = 1 << {field.width - 1};

    if (result_shifted & sign_bit_mask)
    {{
      // Value is to be interpreted as negative.
      // Sign extend it from the width of the field to the width of the return type.
      const {type_name} result = result_shifted - 2 * sign_bit_mask;
      return result;
    }}

    // Value is positive.
    const {type_name} result = result_shifted;
"""
            else:
                raise ValueError(f"Got unexpected field type: {type_name}")

            cpp_code += "    return result;\n"

        cpp_code += "  }\n\n"

        return cpp_code
