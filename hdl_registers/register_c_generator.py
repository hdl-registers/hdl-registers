# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from .register import Register, REGISTER_MODES
from .register_code_generator import RegisterCodeGenerator


class RegisterCGenerator(RegisterCodeGenerator):
    """
    Generate a C code header with register information.

    There is no unit test of this class that checks the generated code. It is instead functionally
    tested in the file test_register_compilation.py. That test generates C code from an example
    register set, compiles it and performs some run-time assertions in a C program.
    That test is considered more meaningful and exhaustive than a unit test would be.
    """

    def __init__(self, module_name, generated_info):
        self.module_name = module_name
        self.generated_info = generated_info

    def get_header(self, register_objects, constants):
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
    def _comment(comment, indentation=0):
        indent = " " * indentation
        return f"{indent}// {comment}\n"

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
                register_struct += self._comment_block(register_object.description, indentation=2)
                register_struct += self._comment(
                    f'Mode "{REGISTER_MODES[register_object.mode].mode_readable}".', indentation=2
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
                    array_structs += self._comment_block(register.description, indentation=2)
                    array_structs += self._comment(
                        f'Mode "{REGISTER_MODES[register.mode].mode_readable}".', indentation=2
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
        mode_string = f'Mode "{REGISTER_MODES[register.mode].mode_readable}".'

        if register_array is None:
            c_code = self._comment(f'Address of the "{register.name}" register. {mode_string}')
            c_code += self._comment_block(register.description)

            c_code += f"#define {name}_INDEX ({register.index}u)\n"
            c_code += f"#define {name}_ADDR (4u * {name}_INDEX)\n"
        else:
            title = (
                f'Address of the "{register.name}" register within the "{register_array.name}"'
                f" register array (array_index < {register_array.length}). {mode_string}"
            )
            c_code = self._comment(title)
            c_code += self._comment_block(register.description)

            c_code += (
                f"#define {name}_INDEX(array_index) ({register_array.base_index}u + "
                f"(array_index) * {len(register_array.registers)}u + {register.index}u)\n"
            )
            c_code += f"#define {name}_ADDR(array_index) (4u * {name}_INDEX(array_index))\n"

        return c_code

    def _field_definitions(self, register, register_array):
        register_name = self._register_define_name(register, register_array)
        register_string = f'"{register.name}" register'
        if register_array is not None:
            register_string += f' within the "{register_array.name}" register array'

        c_code = ""
        for field in register.fields:
            c_code += self._comment(
                f'Mask and shift for the "{field.name}" field in the {register_string}.'
            )
            c_code += self._comment_block(field.description)

            field_name = f"{register_name}_{field.name.upper()}"
            c_code += f"#define {field_name}_SHIFT ({field.base_index}u)\n"
            c_code += (
                f"#define {field_name}_MASK " f'(0b{"1" * field.width}u << {field.base_index}u)\n'
            )

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
            c_code += self._comment(f'Register constant "{constant.name}".')
            c_code += self._comment_block(constant.description)
            c_code += (
                f"#define {self.module_name.upper()}_{constant.name.upper()} ({constant.value})\n"
            )
        return c_code
