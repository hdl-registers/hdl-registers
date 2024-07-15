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
from typing import TYPE_CHECKING, Any, Optional

# First party libraries
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.register import Register
from hdl_registers.register_list import RegisterList

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register_array import RegisterArray

# There is no unit test of this class that checks the generated code. It is instead functionally
# tested in the file 'test_compiled_c_code.py'. That test generates C code from an example
# register set, compiles it and performs some run-time assertions in a C program.
# That test is considered more meaningful and exhaustive than a unit test would be.


class CHeaderGenerator(RegisterCodeGenerator):
    """
    Generate a C header.
    See the :ref:`generator_c` article for usage details.

    The header will contain:

    * Constant values for all :ref:`register constants <constant_overview>`.

    * Enumeration types for all :ref:`field_enumeration`.

    * A ``struct`` type with all registers as members, which can be memory mapped directly.

    * For each register, ``#define`` constants with the index and address of the register.

    * For each field in each register, ``#define`` constants with the bit shift, bit mask and
      inverse bit mask of the field.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "C header"

    COMMENT_START = "//"

    # The most commonly used indentation.
    # For code at the top level.
    DEFAULT_INDENTATION_LEVEL = 0

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / self._file_name

    def __init__(
        self, register_list: RegisterList, output_folder: Path, file_name: Optional[str] = None
    ):
        """
        For argument description, please see the super class.

        Arguments:
            file_name: Optionally specify an explicit result file name.
                If not specified, the name will be derived from the name of the register list.
        """
        super().__init__(register_list=register_list, output_folder=output_folder)

        self._file_name = f"{self.name}_regs.h" if file_name is None else file_name

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete C header with all constants and all registers.
        """
        define_name = f"{self.name.upper()}_REGS_H"

        c_code = f"""\
{self.header}
#ifndef {define_name}
#define {define_name}

{self._constants()}
{self._number_of_registers()}
{self._register_struct()}
{self._register_defines()}\
#endif {self.comment(define_name)}"""

        return c_code

    def _register_struct(self) -> str:
        array_structs = ""

        register_struct_type = f"{self.name}_regs_t"

        register_struct = self.comment("Type for this register map.")
        register_struct += f"typedef struct {register_struct_type}\n"
        register_struct += "{\n"

        for register_object in self.iterate_register_objects():
            if isinstance(register_object, Register):
                register_struct += self.comment(f'Mode "{register_object.mode.name}".', indent=2)
                register_struct += f"  uint32_t {register_object.name};\n"

            else:
                array_struct_type = f"{self.name}_{register_object.name}_t"

                array_structs += self.comment(
                    f"Type for the '{register_object.name}' register array."
                )
                array_structs += f"typedef struct {array_struct_type}\n"
                array_structs += "{\n"
                for register in register_object.registers:
                    array_structs += self.comment(f"Mode '{register.mode.name}'.", indent=2)
                    array_structs += f"  uint32_t {register.name};\n"
                array_structs += f"}} {array_struct_type};\n\n"

                register_struct += (
                    f"  {array_struct_type} {register_object.name}[{register_object.length}];\n"
                )

        register_struct += f"}} {register_struct_type};\n"

        return array_structs + register_struct

    def _number_of_registers(self) -> str:
        # It is possible that we have constants but no registers
        num_regs = 0
        if self.register_list.register_objects:
            num_regs = self.register_list.register_objects[-1].index + 1

        c_code = self.comment("Number of registers within this register map.")
        c_code += f"#define {self.name.upper()}_NUM_REGS ({num_regs}u)\n"

        return c_code

    def _register_defines(self) -> str:
        c_code = ""
        for register, register_array in self.iterate_registers():
            c_code += self._addr_define(register, register_array)
            c_code += self._field_definitions(register, register_array)
            c_code += "\n"

        return c_code

    def _addr_define(self, register: Register, register_array: Optional["RegisterArray"]) -> str:
        name = self.qualified_register_name(
            register=register, register_array=register_array
        ).upper()

        register_description = self.register_description(
            register=register, register_array=register_array
        )

        register_array_comment = (
            f" (array_index < {register_array.length})" if register_array else ""
        )
        comment = [
            f"Address of the {register_description}{register_array_comment}.",
            f"Mode '{register.mode.name}'.",
        ]
        c_code = self.comment_block(comment)

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

    def _field_definitions(
        self, register: Register, register_array: Optional["RegisterArray"]
    ) -> str:
        c_code = ""
        for field in register.fields:
            field_description = self.field_description(
                register=register, register_array=register_array, field=field
            )
            c_code += self.comment(f"Attributes for the {field_description}.")

            name = self.qualified_field_name(
                register=register, field=field, register_array=register_array
            ).upper()
            c_code += f"#define {name}_SHIFT ({field.base_index}u)\n"
            c_code += f'#define {name}_MASK (0b{"1" * field.width}u << {field.base_index}u)\n'
            c_code += f"#define {name}_MASK_INVERSE (~{name}_MASK)\n"

            if isinstance(field, Enumeration):
                # Enums in C export their enumerators to the surrounding scope, causing huge risk of
                # name clashes.
                # Hence we give the enumerators long names qualified with the register name, etc.
                name_value_pairs = [
                    f"{name}_{element.name.upper()} = {element.value},"
                    for element in field.elements
                ]
                separator = "\n  "

                c_code += f"""\
enum {self.to_pascal_case(name)}
{{
  {separator.join(name_value_pairs)}
}};
"""

        return c_code

    def _constants(self) -> str:
        c_code = ""

        def define(name: str, value: str) -> str:
            return f"#define {name} ({value})\n"

        for constant in self.iterate_constants():
            c_code += self.comment(f"Value of register constant '{constant.name}'.")

            constant_name = f"{self.name.upper()}_{constant.name.upper()}"

            if isinstance(constant, BooleanConstant):
                c_code += define(constant_name, str(constant.value).lower())
            elif isinstance(constant, IntegerConstant):
                # No suffix -> "int", i.e. signed integer of at least 32 bits.
                c_code += define(constant_name, str(constant.value))
            elif isinstance(constant, FloatConstant):
                # No suffix -> "double" (https://stackoverflow.com/questions/13276862).
                # Matches the VHDL type which is at least 64 bits (IEEE 1076-2008, 5.2.5.1).
                # Note that casting a Python float to string guarantees full precision in the
                # resulting string: https://stackoverflow.com/a/60026172
                c_code += define(constant_name, str(constant.value))
            elif isinstance(constant, StringConstant):
                # C string literal: Raw value enclosed in double quotation marks.
                # Without "static", we get a linker warning about multiple definitions
                # despite the multiple-include guard.
                # See here https://stackoverflow.com/a/9196883 for some other information.
                c_code += f'static char *{constant_name} = "{constant.value}";\n'
            elif isinstance(constant, UnsignedVectorConstant):
                # "unsigned" and "long" as suffix.
                # Makes it possible to use large numbers for e.g. base addresses.
                c_code += define(
                    constant_name, f"{constant.prefix}{constant.value_without_separator}UL"
                )
            else:
                raise ValueError(f"Got unexpected constant type. {constant}")

        return c_code
