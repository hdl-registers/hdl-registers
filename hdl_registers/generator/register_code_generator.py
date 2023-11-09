# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from abc import ABC, abstractmethod
from typing import Iterator

# First party libraries
from hdl_registers.register import Register
from hdl_registers.register_array import RegisterArray


class RegisterCodeGenerator(ABC):

    """
    Common functions for generating register code.
    """

    @staticmethod
    def _iterate_registers(register_objects) -> Iterator[tuple[Register, RegisterArray]]:
        """
        Iterate over all registers, plain or in array.
        """
        for register_object in register_objects:
            if isinstance(register_object, Register):
                yield (register_object, None)
            else:
                for register in register_object.registers:
                    yield (register, register_object)

    @staticmethod
    def _iterate_plain_registers(register_objects) -> Iterator[Register]:
        """
        Iterate over all plain registers (i.e. registers not in array).
        """
        for register_object in register_objects:
            if isinstance(register_object, Register):
                yield register_object

    @staticmethod
    def _iterate_register_arrays(register_objects) -> Iterator[RegisterArray]:
        """
        Iterate over all register arrays.
        """
        for register_object in register_objects:
            if isinstance(register_object, RegisterArray):
                yield register_object

    @staticmethod
    @abstractmethod
    def _comment(comment, indent):
        raise NotImplementedError("Should be overloaded in child class")

    def _comment_block(self, text, indent):
        """
        Create a comment block from a string with newlines.
        """
        text_lines = text.split("\n")

        # Very common that the last line is empty. An effect of TOML formatting with
        # multi-line strings. Remove to make the output look more clean.
        if text_lines[-1] == "":
            text_lines.pop()

        return "".join(self._comment(comment=line, indent=indent) for line in text_lines)

    @staticmethod
    def _to_pascal_case(snake_string):
        """
        Returns e.g., my_funny_string -> MyFunnyString
        """
        return snake_string.title().replace("_", "")
