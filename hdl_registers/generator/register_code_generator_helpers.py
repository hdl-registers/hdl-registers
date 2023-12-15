# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import TYPE_CHECKING, Iterator, Optional, Union

# First party libraries
from hdl_registers.register import Register
from hdl_registers.register_array import RegisterArray

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.constant.constant import Constant
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register_list import RegisterList


class RegisterCodeGeneratorHelpers:
    """
    Various helper methods that make register code generation easier.
    """

    # Defined in RegisterCodeGenerator, which shall also be inherited wherever this class is used.
    register_list: "RegisterList"
    DEFAULT_INDENTATION_LEVEL: int
    COMMENT_START: str
    COMMENT_END: str

    def iterate_constants(self) -> Iterator["Constant"]:
        """
        Iterate of all constants in the register list.
        """
        for constant in self.register_list.constants:
            yield constant

    def iterate_register_objects(self) -> Iterator[Union[Register, RegisterArray]]:
        """
        Iterate over all register objects in the register list.
        I.e. all plain registers and all register arrays.
        """
        for register_object in self.register_list.register_objects:
            yield register_object

    def iterate_registers(self) -> Iterator[tuple[Register, Union[RegisterArray, None]]]:
        """
        Iterate over all registers, plain or in array, in the register list.

        Return:
            If the register is plain, the array return value in the tuple will be ``None``.
            If the register is in an array, the array return value will conversely be non-``None``.
        """
        for register_object in self.iterate_register_objects():
            if isinstance(register_object, Register):
                yield (register_object, None)
            else:
                for register in register_object.registers:
                    yield (register, register_object)

    def iterate_plain_registers(self) -> Iterator[Register]:
        """
        Iterate over all plain registers (i.e. registers not in array) in the register list.
        """
        for register_object in self.iterate_register_objects():
            if isinstance(register_object, Register):
                yield register_object

    def iterate_register_arrays(self) -> Iterator[RegisterArray]:
        """
        Iterate over all register arrays in the register list.
        """
        for register_object in self.iterate_register_objects():
            if isinstance(register_object, RegisterArray):
                yield register_object

    def get_indentation(self, indent: Optional[int] = None) -> str:
        """
        Get the requested indentation in spaces.
        Will use the default indentation for this generator if not specified.
        """
        indent = self.DEFAULT_INDENTATION_LEVEL if indent is None else indent
        return " " * indent

    def get_separator_line(self, indent: Optional[int] = None) -> str:
        """
        Get a separator line, e.g. ``# ---------------------------------``.
        """
        indentation = self.get_indentation(indent=indent)
        result = f"{indentation}{self.COMMENT_START} "

        num_dash = 80 - len(result) - len(self.COMMENT_END)
        result += "-" * num_dash
        result += f"{self.COMMENT_END}\n"

        return result

    def comment(self, comment: str, indent: Optional[int] = None) -> str:
        """
        Create a one-line comment.
        """
        indentation = self.get_indentation(indent=indent)
        return f"{indentation}{self.COMMENT_START} {comment}{self.COMMENT_END}\n"

    def comment_block(self, text: str, indent: Optional[int] = None) -> str:
        """
        Create a comment block from a string with newlines.
        """
        text_lines = text.split("\n")

        # Very common that the last line is empty.
        # An effect of TOML formatting with multi-line strings.
        # Remove to make the output look more clean.
        if text_lines[-1] == "":
            text_lines.pop()

        return "".join(self.comment(comment=line, indent=indent) for line in text_lines)

    @staticmethod
    def register_description(
        register: Register, register_array: Optional[RegisterArray] = None
    ) -> str:
        """
        Get a comment describing the register.
        """
        result = f"'{register.name}' register"

        if register_array is None:
            return result

        return f"{result} within the '{register_array.name}' register array"

    def field_description(
        self,
        register: Register,
        field: "RegisterField",
        register_array: Optional[RegisterArray] = None,
    ) -> str:
        """
        Get a comment describing the field.
        """
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        return f"'{field.name}' field in the {register_description}"

    @staticmethod
    def to_pascal_case(snake_string: str) -> str:
        """
        Converts e.g., "my_funny_string" to "MyFunnyString".

        Pascal case is like camel case but with the initial character being capitalized.
        I.e. how classes are named in Python, C and C++.
        """
        return snake_string.title().replace("_", "")
