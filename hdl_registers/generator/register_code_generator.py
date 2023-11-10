# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Union

# Third party libraries
from tsfpga.system_utils import create_file, read_file

# First party libraries
from hdl_registers import __version__
from hdl_registers.register import Register
from hdl_registers.register_array import RegisterArray

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.constant.constant import Constant
    from hdl_registers.register_list import RegisterList


class RegisterCodeGenerator(ABC):

    """
    Abstract interface and common functions for generating register code.
    """

    @property
    @staticmethod
    @abstractmethod
    def SHORT_DESCRIPTION() -> str:  # pylint: disable=invalid-name
        """
        A short description of what this generator produces.

        Overload in child class by setting e.g.

        .. code-block:: python

          SHORT_DESCRIPTION = "C++ header"

        as a static class member at the top of the class.
        """

    @property
    @staticmethod
    @abstractmethod
    def COMMENT_START() -> str:  # pylint: disable=invalid-name
        """
        The character(s) that start a comment line in the programming language that we are
        generating code for.
        Will be used when printing status messages.

        Overload in child class by setting e.g.

        .. code-block:: python

          COMMENT_START = "#"

        as a static class member at the top of the class.
        """

    @property
    @abstractmethod
    def output_file(self) -> Path:
        """
        Result will be placed in this file.

        Overload in a child class to give the proper name to the code artifact.
        Probably using a combination of ``self.output_folder`` and ``self.name``.
        For example:

        .. code-block:: python

          @property
          def output_file(self):
              return self.output_folder / f"{self.name}_regs.html"
        """

    @abstractmethod
    def get_code(self, **kwargs) -> str:  # pylint: disable=unused-argument
        """
        Get the generated code as a string.

        Overload in a child class where the code generation is implemented.

        Arguments:
            kwargs: Further optional parameters that can be used.
                Can send any number of named arguments, per the requirements of :meth:`.get_code`
                of any custom generators that inherit this class.
        """

    # Optionally set a non-zero default indentation level, expressed in number of spaces, in a child
    # class for your code generator.
    # Will be used by e.g. the 'self.comment' method.
    DEFAULT_INDENTATION_LEVEL = 0

    # For some languages, comment lines have to be ended with special characters.
    # Optionally set this to a non-null string in a child class.
    # For best formatting, leave a space character at the start of this string.
    COMMENT_END = ""

    def __init__(self, register_list: "RegisterList", output_folder: Path):
        """
        Arguments:
            register_list: Registers and constants from this register list will be included
                in the generated artifacts.
            output_folder: Result file will be placed in this folder.
        """
        self.register_list = register_list
        self.output_folder = output_folder

        self.name = register_list.name

    def create(self, **kwargs):
        """
        Generate the result artifact.
        I.e. create the :meth:`.output_file` containing the result from :meth:`.get_code` method.

        Arguments:
            kwargs: Further optional parameters that will be sent on to the
                :meth:`.get_code` method.
                See :meth:`.get_code` for details.
        """
        print(f"Creating {self.SHORT_DESCRIPTION} file: {self.output_file}")

        code = self.get_code(**kwargs)

        # Will create the containing folder unless it already exists.
        create_file(file=self.output_file, contents=code)

    def create_if_needed(self, **kwargs) -> bool:
        """
        Generate the result file if needed, i.e. if :meth:`.should_create` is ``True``:

        Arguments:
            kwargs: Further optional parameters that will be sent on to the
                :meth:`.get_code` method.
                See :meth:`.get_code` for details.

        Return:
            True if artifacts where created, False otherwise.
        """
        if self.should_create:
            self.create(**kwargs)
            return True

        return False

    @property
    def should_create(self) -> bool:
        """
        Indicates if a (re-)create of artifacts is needed.
        Will be True if

        * artifact file does not exist,
        * generator version of artifact does not match current code version, or
        * :meth:`.RegisterList.object_hash` of artifact does not match the user-supplied
          register list, i.e. something has changed.
        """
        output_file = self.output_file

        if not output_file.exists():
            return True

        if (
            __version__,
            self.register_list.object_hash,
        ) != self._find_version_and_hash_of_existing_file(file_path=output_file):
            return True

        return False

    def _find_version_and_hash_of_existing_file(
        self, file_path: Path
    ) -> Union[None, tuple[str, str]]:
        """
        Returns ``None`` if nothing found, otherwise the matching strings in a tuple.
        """
        existing_file_content = read_file(file=file_path)

        result_version = None
        result_hash = None

        # This is either the very first line of the file, or starting on a new line.
        version_re = re.compile(
            (
                rf"(^|\n){self.COMMENT_START} This file is automatically generated by "
                rf"hdl_registers version (\S+)\.{self.COMMENT_END}\n"
            )
        )
        version_match = version_re.search(existing_file_content)
        if version_match:
            result_version = version_match.group(2)

        hash_re = re.compile(
            rf"\n{self.COMMENT_START} Register hash ([0-9a-f]+)\.{self.COMMENT_END}\n"
        )
        hash_match = hash_re.search(existing_file_content)
        if hash_match:
            result_hash = hash_match.group(1)

        return result_version, result_hash

    @property
    def header(self) -> str:
        """
        Get file header with version, register hash, time/date information, etc.
        Formatted as a comment block.
        """
        generated_source_info = "\n".join(self.register_list.generated_source_info)
        return self.comment_block(text=generated_source_info, indent=0)

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

    def get_indentation(self, indent: int = None) -> str:
        """
        Get the requested indentation in spaces.
        Will use the default indentation for this generator if not specified.
        """
        indent = self.DEFAULT_INDENTATION_LEVEL if indent is None else indent
        return " " * indent

    def get_separator_line(self, indent: int = None) -> str:
        """
        Get a separator line, e.g. ``# ---------------------------------``.
        """
        indentation = self.get_indentation(indent=indent)
        result = f"{indentation}{self.COMMENT_START} "

        num_dash = 80 - len(result) - len(self.COMMENT_END)
        result += "-" * num_dash
        result += f"{self.COMMENT_END}\n"

        return result

    def comment(self, comment: str, indent: int = None) -> str:
        """
        Create a one-line comment.
        """
        indentation = self.get_indentation(indent=indent)
        return f"{indentation}{self.COMMENT_START} {comment}{self.COMMENT_END}\n"

    def comment_block(self, text: str, indent: int = None) -> str:
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
    def register_description(register: Register, register_array: RegisterArray = None) -> str:
        """
        Get a comment describing the register.
        """
        result = f"'{register.name}' register"

        if register_array is None:
            return result

        return f"{result} within the '{register_array.name}' register array"

    @staticmethod
    def to_pascal_case(snake_string: str) -> str:
        """
        Converts e.g., "my_funny_string" to "MyFunnyString".

        Pascal case is like camel case but with the initial character being capitalized.
        I.e. how classes are named in Python, C and C++.
        """
        return snake_string.title().replace("_", "")
