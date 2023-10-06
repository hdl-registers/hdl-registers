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
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.register import REGISTER_MODES, Register

# Local folder libraries
from .register_code_generator import RegisterCodeGenerator


class RegisterCGenerator(RegisterCodeGenerator):
    """
    Generate a C code header with register information.

    There is no unit test of this class that checks the generated code. It is instead functionally
    tested in the file test_register_compilation.py. That test generates C code from an example
    register set, compiles it and performs some run-time assertions in a C program.
    That test is considered more meaningful and exhaustive than a unit test would be.
    """

    # The most commonly used indentation.
    # For code at the top level.
    default_indent = 0

    def __init__(self, module_name, generated_info):
        """
        Arguments:
            module_name (str): The name of the register map.
            generated_info (list(str)): Will be placed in the file headers.
        """
        self.module_name = module_name
        self.generated_info = generated_info

    def get_header(self, register_objects, constants):
        """
        Get a complete C header with all constants and all registers.

        Arguments:
            register_objects (list): Register arrays and registers to be included.
            constants (list(Constant)): Constants to be included.

        Returns:
            str: C code.
        """
        define_name = self.module_name.upper() + "_REGS_H"

        c_code = f"""\
{self._file_header()}
#ifndef {define_name}
#define {define_name}

{self._constants(constants)}
{self._number_of_registers(register_objects)}
{self._register_struct(register_objects)}
{self._register_defines(register_objects)}\
#endif {self._comment(define_name)}"""

        return c_code

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

    def _file_header(self):
        return "".join([self._comment(header_line) for header_line in self.generated_info])

    def _register_struct(self, register_objects):
        array_structs = ""

        register_struct_type = f"{self.module_name}_regs_t"
        register_struct = self._comment("Type for this register map.")
        register_struct += f"typedef struct {register_struct_type}\n"
        register_struct += "{\n"
        for register_object in register_objects:
            if isinstance(register_object, Register):
                register_struct += self._comment(
                    f'Mode "{REGISTER_MODES[register_object.mode].mode_readable}".', indent=2
                )
                register_struct += f"  uint32_t {register_object.name};\n"

            else:
                array_struct_type = f"{self.module_name}_{register_object.name}_t"

                array_structs += self._comment(
                    f'Type for the "{register_object.name}" register array.'
                )
                array_structs += f"typedef struct {array_struct_type}\n"
                array_structs += "{\n"
                for register in register_object.registers:
                    array_structs += self._comment(
                        f'Mode "{REGISTER_MODES[register.mode].mode_readable}".', indent=2
                    )
                    array_structs += f"  uint32_t {register.name};\n"
                array_structs += f"}} {array_struct_type};\n\n"

                register_struct += (
                    f"  {array_struct_type} {register_object.name}[{register_object.length}];\n"
                )
        register_struct += f"}} {register_struct_type};\n"
        return array_structs + register_struct

    def _number_of_registers(self, register_objects):
        # It is possible that we have constants but no registers
        num_regs = 0
        if register_objects:
            num_regs = register_objects[-1].index + 1

        c_code = self._comment("Number of registers within this register map.")
        c_code += f"#define {self.module_name.upper()}_NUM_REGS ({num_regs}u)\n"

        return c_code

    def _register_defines(self, register_objects):
        c_code = ""
        for register, register_array in self._iterate_registers(register_objects):
            c_code += self._addr_define(register, register_array)
            c_code += self._field_definitions(register, register_array)
            c_code += "\n"

        return c_code

    def _addr_define(self, register, register_array):
        name = self._register_define_name(register, register_array)

        comment = f'Address of the "{register.name}" register'
        if register_array:
            comment += (
                f' within the "{register_array.name}" register array '
                f"(array_index < {register_array.length})"
            )
        comment += f'.\nMode "{REGISTER_MODES[register.mode].mode_readable}".'

        c_code = self._comment_block(comment)

        if register_array:
            c_code += (
                f"#define {name}_INDEX(array_index) ({register_array.base_index}u + "
                f"(array_index) * {len(register_array.registers)}u + {register.index}u)\n"
            )
            c_code += f"#define {name}_ADDR(array_index) (4u * {name}_INDEX(array_index))\n"
        else:
            c_code += f"#define {name}_INDEX ({register.index}u)\n"
            c_code += f"#define {name}_ADDR (4u * {name}_INDEX)\n"

        return c_code

    def _field_definitions(self, register, register_array):
        register_name = self._register_define_name(register, register_array)
        register_string = f'"{register.name}" register'
        if register_array is not None:
            register_string += f' within the "{register_array.name}" register array'

        c_code = ""
        for field in register.fields:
            c_code += self._comment(
                f'Attributes for the "{field.name}" field in the {register_string}.'
            )

            field_name = f"{register_name}_{field.name.upper()}"
            c_code += f"#define {field_name}_SHIFT ({field.base_index}u)\n"
            c_code += f'#define {field_name}_MASK (0b{"1" * field.width}u << {field.base_index}u)\n'
            c_code += f"#define {field_name}_MASK_INVERSE (~{field_name}_MASK)\n"

            if isinstance(field, Enumeration):
                # Enums in C export their enumerators to the surrounding scope, causing huge risk of
                # name clashes.
                # Hence we give the enumerators long names qualified with the register name, etc.
                name_value_pairs = [
                    f"{field_name}_{element.name.upper()} = {element.value},"
                    for element in field.elements
                ]
                separator = "\n  "

                c_code += f"""\
enum {self._to_pascal_case(field_name)}
{{
  {separator.join(name_value_pairs)}
}};
"""

        return c_code

    def _register_define_name(self, register, register_array):
        if register_array is None:
            name = f"{self.module_name}_{register.name}"
        else:
            name = f"{self.module_name}_{register_array.name}_{register.name}"
        return name.upper()

    def _constants(self, constants):
        c_code = ""
        for constant in constants:
            constant_name = f"{self.module_name.upper()}_{constant.name.upper()}"

            # Most of the types are a simple "#define". But some are special, where we explicitly
            # set the declaration.
            declaration = ""

            if isinstance(constant, BooleanConstant):
                value = str(constant.value).lower()
            elif isinstance(constant, IntegerConstant):
                # No suffix -> "int", i.e. signed integer of at least 32 bits.
                value = str(constant.value)
            elif isinstance(constant, FloatConstant):
                # No suffix -> "double" (https://stackoverflow.com/questions/13276862).
                # Matches the VHDL type which is at least 64 bits (IEEE 1076-2008, 5.2.5.1).
                # Note that casting a Python float to string guarantees full precision in the
                # resulting string: https://stackoverflow.com/a/60026172
                value = str(constant.value)
            elif isinstance(constant, StringConstant):
                # C string literal: Raw value enclosed in double quotation marks.
                declaration = f'char *{constant_name} = "{constant.value}";'
            elif isinstance(constant, UnsignedVectorConstant):
                # "unsigned" and "long" as suffix.
                # Makes it possible to use large numbers for e.g. base addresses.
                value = f"{constant.prefix}{constant.value_without_separator}UL"
            else:
                raise ValueError(f"Got unexpected constant type. {constant}")

            c_code += self._comment(f'Value of register constant "{constant.name}".')

            if declaration:
                c_code += f"{declaration}\n"
            else:
                # Default: simple "#define"
                c_code += f"#define {constant_name} ({value})\n"

        return c_code
