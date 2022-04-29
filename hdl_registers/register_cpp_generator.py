# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

from .register import REGISTER_MODES
from .register_array import RegisterArray
from .register_code_generator import RegisterCodeGenerator


class RegisterCppGenerator(RegisterCodeGenerator):
    """
    Generate a C++ class with register definitions and methods.

    There is no unit test of this class that checks the generated code. It is instead functionally
    tested in the file test_register_compilation.py. That test generates C++ code from an example
    register set, compiles it and performs some run-time assertions in a C++ program.
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
        self._class_name = self._to_pascal_case(module_name)

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
        cpp_code = f"class I{self._class_name}\n"
        cpp_code += "{\n"
        cpp_code += "public:\n"

        for constant in constants:
            cpp_code += self._comment("Register constant.", indentation=2)
            cpp_code += self._comment_block(constant.description, indentation=2)

            cpp_code += f"  static const int {constant.name} = {constant.value}L;\n"
        if constants:
            cpp_code += "\n"

        cpp_code += self._num_registers(register_objects)

        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                cpp_code += self._comment(
                    f'Length of the "{register_object.name}" register array', indentation=2
                )
                constant_name = self._array_length_constant_name(register_object)
                cpp_code += (
                    f"  static const size_t {constant_name} = {register_object.length}uL;\n\n"
                )

        cpp_code += f"  virtual ~I{self._class_name}() {{ }}\n"

        for register, register_array in self._iterate_registers(register_objects):
            cpp_code += f"\n{self._get_separator_line(indentation=2)}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            description += (
                f' Mode "{REGISTER_MODES[register.mode].mode_readable}". Register description:'
            )

            cpp_code += self._comment(comment=description, indentation=2)
            cpp_code += self._comment_block(register.description, indentation=2)
            cpp_code += "\n"

            if register.is_bus_readable:
                cpp_code += self._comment(
                    "Getter that will read the whole register's value over the register bus.",
                    indentation=2,
                )
                signature = self._register_getter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += f"  virtual uint32_t {signature} const = 0;\n\n"

            if register.is_bus_writeable:
                cpp_code += self._comment(
                    "Setter that will write the whole register's value over the register bus.",
                    indentation=2,
                )
                cpp_code += (
                    "  virtual void "
                    f"{self._setter_function_signature(register, register_array)} const = 0;\n\n"
                )

            cpp_code += self._field_interface(register, register_array)

        cpp_code += "};\n"

        cpp_code_top = f"""\
{self._file_header()}
#pragma once

#include <cassert>
#include <cstdint>
#include <cstdlib>

"""
        return cpp_code_top + self._with_namespace(cpp_code)

    def _num_registers(self, register_objects):
        # It is possible that we have constants but no registers
        num_registers = 0
        if register_objects:
            num_registers = register_objects[-1].index + 1

        cpp_code = self._comment("Number of registers within this register map.", indentation=2)
        cpp_code += f"  static const size_t num_registers = {num_registers}uL;\n\n"
        return cpp_code

    @staticmethod
    def _get_separator_line(indentation):
        """
        Get a separator line, e.g. "  // ---------------------------------\n"
        """
        result = " " * indentation + "// "
        num_dash = 80 - len(result)
        result += "-" * num_dash
        result += "\n"
        return result

    @staticmethod
    def _get_methods_description(register, register_array):
        result = f'Methods for the "{register.name}" register'
        if register_array:
            result += f' within the "{register_array.name}" register array'
        result += "."

        return result

    def get_header(self, register_objects):
        """
        Get a complete C++ class header for the implementation of all methods.

        Arguments:
            register_objects (list): Register arrays and registers to be included.

        Returns:
            str: C++ code.
        """
        cpp_code = f"class {self._class_name} : public I{self._class_name}\n"
        cpp_code += "{\n"

        cpp_code += "private:\n"
        cpp_code += "  volatile uint32_t *m_registers;\n\n"

        cpp_code += "public:\n"
        cpp_code += f"  {self._constructor_signature()};\n\n"
        cpp_code += f"  virtual ~{self._class_name}() {{ }}\n"

        def getter_function(signature):
            return f"  virtual uint32_t {signature} const override;\n"

        for register, register_array in self._iterate_registers(register_objects):
            cpp_code += f"\n{self._get_separator_line(indentation=2)}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            description += " See interface header for documentation."
            cpp_code += self._comment(comment=description, indentation=2)

            if register.is_bus_readable:
                signature = self._register_getter_function_signature(
                    register=register,
                    register_array=register_array,
                )
                cpp_code += getter_function(signature=signature)

                for field in register.fields:
                    signature = self._field_getter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=False,
                    )
                    cpp_code += getter_function(signature=signature)

                    signature = self._field_getter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=True,
                    )
                    cpp_code += getter_function(signature=signature)

            if register.is_bus_writeable:
                cpp_code += (
                    "  virtual void "
                    f"{self._setter_function_signature(register, register_array)} const override;\n"
                )

        cpp_code += "};\n"

        cpp_code_top = f"""\
{self._file_header()}
#pragma once

#include "i_{self.module_name}.h"

"""
        return cpp_code_top + self._with_namespace(cpp_code)

    def get_implementation(self, register_objects):
        """
        Get a complete C++ class implementation with all methods.

        Arguments:
            register_objects (list): Register arrays and registers to be included.

        Returns:
            str: C++ code.
        """
        cpp_code = f"{self._class_name}::{self._constructor_signature()}\n"
        cpp_code += "    : m_registers(reinterpret_cast<volatile uint32_t *>(base_address))\n"
        cpp_code += "{\n"
        cpp_code += "  // Empty\n"
        cpp_code += "}\n\n"

        for register, register_array in self._iterate_registers(register_objects):
            cpp_code += f"\n{self._get_separator_line(indentation=0)}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            description += " See interface header for documentation.\n"
            cpp_code += self._comment(comment=description, indentation=0)

            if register.is_bus_readable:
                cpp_code += self._register_getter_function(register, register_array)

                for field in register.fields:
                    cpp_code += self._field_getter_function(register, register_array, field=field)
                    cpp_code += self._field_getter_function_from_value(
                        register, register_array, field=field
                    )

            if register.is_bus_writeable:
                cpp_code += self._setter_function(register, register_array)

        cpp_code_top = f"{self._file_header()}\n"
        cpp_code_top += f'#include "include/{self.module_name}.h"\n\n'

        return cpp_code_top + self._with_namespace(cpp_code)

    def _field_interface(self, register, register_array):
        def getter_function(signature):
            return f"  virtual uint32_t {signature} const = 0;\n"

        cpp_code = ""
        for field in register.fields:
            register_description = f'in the "{register.name}" register'
            if register_array is not None:
                register_description += f' within the "{register_array.name}" register array'

            description = (
                f'Bitmask for the "{field.name}" field {register_description}. Field description:'
            )

            cpp_code += self._comment(description, indentation=2)
            cpp_code += self._comment_block(field.description, indentation=2)

            field_constant_name = self._get_field_constant_name(
                register=register, register_array=register_array, field=field
            )
            cpp_code += (
                f"  static const uint32_t {field_constant_name}_shift = {field.base_index}uL;\n"
            )
            cpp_code += (
                f"  static const uint32_t {field_constant_name}_mask = "
                f'0b{"1" * field.width}uL << {field.base_index}uL;\n'
            )

            if register.is_bus_readable:
                cpp_code += self._comment(
                    f'Getter for the "{field.name}" field {register_description},', indentation=2
                )
                cpp_code += self._comment(
                    "which will read register value over the register bus.", indentation=2
                )
                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=False,
                )
                cpp_code += getter_function(signature=signature)

                cpp_code += self._comment(
                    f'Getter for the "{field.name}" field {register_description},', indentation=2
                )
                cpp_code += self._comment("given the register's current value.", indentation=2)

                signature = self._field_getter_function_signature(
                    register=register,
                    register_array=register_array,
                    field=field,
                    from_value=True,
                )
                cpp_code += getter_function(signature=signature)

            cpp_code += "\n"

        return cpp_code

    @staticmethod
    def _get_field_constant_name(register, register_array, field):
        if register_array is None:
            return f"{register.name}_{field.name}"

        return f"{register_array.name}_{register.name}_{field.name}"

    @staticmethod
    def _array_length_constant_name(register_array):
        return f"{register_array.name}_array_length"

    @staticmethod
    def _with_namespace(cpp_code_body):
        cpp_code = "namespace fpga_regs\n"
        cpp_code += "{\n\n"
        cpp_code += f"{cpp_code_body}"
        cpp_code += "\n} /* namespace fpga_regs */\n"
        return cpp_code

    @staticmethod
    def _comment(comment, indentation=0):
        indent = " " * indentation
        return f"{indent}// {comment}\n"

    def _file_header(self):
        return "".join([self._comment(header_line) for header_line in self.generated_info])

    def _constructor_signature(self):
        return f"{self._class_name}(volatile uint8_t *base_address)"

    def _setter_function(self, register, register_array):
        cpp_code = (
            "void "
            f"{self._class_name}::{self._setter_function_signature(register, register_array)} "
            "const\n"
        )
        cpp_code += "{\n"
        if register_array is None:
            cpp_code += f"  m_registers[{register.index}] = value;\n"
        else:
            cpp_code += (
                f"  assert(array_index < {self._array_length_constant_name(register_array)});\n"
            )
            cpp_code += (
                f"  const size_t index = {register_array.base_index} "
                f"+ array_index * {len(register_array.registers)} + {register.index};\n"
            )
            cpp_code += "  m_registers[index] = value;\n"
        cpp_code += "}\n\n"
        return cpp_code

    @staticmethod
    def _setter_function_signature(register, register_array):
        if register_array is None:
            return f"set_{register.name}(uint32_t value)"
        return f"set_{register_array.name}_{register.name}(size_t array_index, uint32_t value)"

    def _register_getter_function(self, register, register_array):
        signature = self._register_getter_function_signature(
            register=register, register_array=register_array
        )
        cpp_code = f"uint32_t {self._class_name}::{signature} const\n"
        cpp_code += "{\n"
        if register_array is None:
            cpp_code += f"  return m_registers[{register.index}];\n"
        else:
            cpp_code += (
                f"  assert(array_index < {self._array_length_constant_name(register_array)});\n"
            )
            cpp_code += (
                f"  const size_t index = {register_array.base_index} "
                f"+ array_index * {len(register_array.registers)} + {register.index};\n"
            )
            cpp_code += "  return m_registers[index];\n"
        cpp_code += "}\n\n"
        return cpp_code

    def _field_getter_function(self, register, register_array, field):
        signature = self._field_getter_function_signature(
            register=register, register_array=register_array, field=field, from_value=False
        )

        cpp_code = f"uint32_t {self._class_name}::{signature} const\n"
        cpp_code += "{\n"

        register_getter_function_name = self._register_getter_function_name(
            register=register, register_array=register_array
        )

        field_getter_from_value_function_name = self._field_getter_function_name(
            register=register, register_array=register_array, field=field, from_value=True
        )

        cpp_code += f"  const uint32_t register_value = {register_getter_function_name}("
        if register_array:
            cpp_code += "array_index"
        cpp_code += ");\n"

        cpp_code += (
            f"  const uint32_t result = {field_getter_from_value_function_name}(register_value);\n"
        )
        cpp_code += "  return result;\n"
        cpp_code += "}\n\n"

        return cpp_code

    def _field_getter_function_from_value(self, register, register_array, field):
        signature = self._field_getter_function_signature(
            register=register, register_array=register_array, field=field, from_value=True
        )

        cpp_code = f"uint32_t {self._class_name}::{signature} const\n"
        cpp_code += "{\n"

        field_constant_name = self._get_field_constant_name(
            register=register, register_array=register_array, field=field
        )

        cpp_code += (
            f"  const uint32_t result_masked = register_value & {field_constant_name}_mask;\n"
        )
        cpp_code += (
            f"  const uint32_t result_shifted = result_masked >> {field_constant_name}_shift;\n"
        )
        cpp_code += "  return result_shifted;\n"
        cpp_code += "}\n\n"

        return cpp_code

    @staticmethod
    def _register_getter_function_name(register, register_array):
        result = "get"

        if register_array:
            result += f"_{register_array.name}"

        result += f"_{register.name}"

        return result

    def _register_getter_function_signature(self, register, register_array):
        function_name = self._register_getter_function_name(
            register=register, register_array=register_array
        )
        result = f"{function_name}("

        if register_array:
            result += "size_t array_index"

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

    def _field_getter_function_signature(self, register, register_array, field, from_value):
        function_name = self._field_getter_function_name(
            register=register, register_array=register_array, field=field, from_value=from_value
        )
        result = f"{function_name}("

        if from_value:
            # Value is supplied by user
            result += "uint32_t register_value"
        elif register_array:
            # Value shall be read from bus, in which case we need to know array index if this
            # is an array
            result += "size_t array_index"

        result += ")"

        return result
