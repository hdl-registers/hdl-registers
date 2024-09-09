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
from hdl_registers.register_modes import REGISTER_MODES

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.constant.constant import Constant
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register_list import RegisterList


class RegisterCodeGeneratorHelpers:
    """
    Various helper methods that make register code generation easier.
    """

    # Defined in 'RegisterCodeGenerator' class, which shall also be inherited wherever this class
    # is used.
    register_list: "RegisterList"
    name: str
    DEFAULT_INDENTATION_LEVEL: int
    COMMENT_START: str
    COMMENT_END: str

    def iterate_constants(self) -> Iterator["Constant"]:
        """
        Iterate of all constants in the register list.
        """
        yield from self.register_list.constants

    def iterate_register_objects(self) -> Iterator[Union[Register, RegisterArray]]:
        """
        Iterate over all register objects in the register list.
        I.e. all plain registers and all register arrays.
        """
        yield from self.register_list.register_objects

    def iterate_registers(self) -> Iterator[tuple[Register, Optional[RegisterArray]]]:
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

    def qualified_register_name(
        self, register: "Register", register_array: Optional["RegisterArray"] = None
    ) -> str:
        """
        Get the qualified register name, e.g. "<module name>_<register name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        if register_array is None:
            return f"{self.name}_{register.name}"

        register_array_name = self.qualified_register_array_name(register_array=register_array)
        return f"{register_array_name}_{register.name}"

    def qualified_register_array_name(self, register_array: "RegisterArray") -> str:
        """
        Get the qualified register array name, e.g. "<module name>_<register array name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        return f"{self.name}_{register_array.name}"

    def qualified_field_name(
        self,
        register: "Register",
        field: "RegisterField",
        register_array: Optional["RegisterArray"] = None,
    ) -> str:
        """
        Get the qualified field name, e.g. "<module name>_<register name>_<field_name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
        return f"{register_name}_{field.name}"

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

    def comment_block(self, text: list[str], indent: Optional[int] = None) -> str:
        """
        Create a comment block from a list of text lines.
        """
        return "".join(self.comment(comment=line, indent=indent) for line in text)

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
    def field_setter_should_read_modify_write(register: Register) -> bool:
        """
        Returns True if a field value setter should read-modify-write the register.

        Is only true if the register is of a writeable type where the software can also read back
        a previously-written value.
        Furthermore, read-modify-write only makes sense if there is more than one field, otherwise
        it is a waste of CPU cycles.
        """
        assert register.fields, "Should not end up here if the register has no fields."

        if register.mode == REGISTER_MODES["r_w"]:
            return len(register.fields) > 1

        if register.mode in [
            REGISTER_MODES["w"],
            REGISTER_MODES["wpulse"],
            REGISTER_MODES["r_wpulse"],
        ]:
            return False

        raise ValueError(f"Got non-writeable register: {register}")

    @staticmethod
    def to_pascal_case(snake_string: str) -> str:
        """
        Converts e.g., "my_funny_string" to "MyFunnyString".

        Pascal case is like camel case but with the initial character being capitalized.
        I.e. how classes are named in Python, C and C++.
        """
        return snake_string.title().replace("_", "")
