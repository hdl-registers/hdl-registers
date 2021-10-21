# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from .register import Register


class RegisterCodeGenerator:

    """
    Common functions for generating register code.
    """

    @staticmethod
    def _iterate_registers(register_objects):
        for register_object in register_objects:
            if isinstance(register_object, Register):
                yield (register_object, None)
            else:
                for register in register_object.registers:
                    yield (register, register_object)

    @staticmethod
    def _comment(comment, indentation=0):
        raise NotImplementedError("Should be overloaded in child class")

    def _comment_block(self, text, indentation=0):
        """
        Create a comment block from a string with newlines.
        """
        text_lines = text.split("\n")

        # Very common that the last line is empty. An effect of TOML formatting with
        # multi-line strings. Remove to make the output look more clean.
        if text_lines[-1] == "":
            text_lines.pop()

        return "".join(self._comment(line, indentation=indentation) for line in text_lines)

    @staticmethod
    def _to_pascal_case(snake_string):
        """
        Returns e.g., my_funny_string -> MyFunnyString
        """
        return snake_string.title().replace("_", "")
