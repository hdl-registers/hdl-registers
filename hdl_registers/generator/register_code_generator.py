# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import datetime
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Union

# Third party libraries
from tsfpga.git_utils import get_git_commit, git_commands_are_available
from tsfpga.svn_utils import get_svn_revision_information, svn_commands_are_available
from tsfpga.system_utils import create_file, read_file

# First party libraries
from hdl_registers import __version__

if TYPE_CHECKING:
    # First party libraries
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
        Will be used when printing status messages.

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
          def output_file(self) -> Path:
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
        Generate the result file if needed.
        I.e. call :meth:`.create` if :meth:`.should_create` is ``True``.

        This method is recommended rather than :meth:`.create` in time-critical scenarios,
        such as before a user simulation run.
        The :meth:`.should_create` check is very fast (0.5 ms on a decent computer with a typical
        register list), while a typical register generator is quite slow by comparison.
        Hence it makes sense to run this method in order to save execution time.
        This increased speed gives a much nicer user experience.

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
        Will be True if any of these conditions are true:

        * File does not exist.
        * Generator version of artifact does not match current code version.
        * Artifact hash does not match :meth:`.RegisterList.object_hash` of the current
          register list.
          I.e. something has changed since the previous file was generated.

        The version and hash checks above are dependent on the artifact file having a header
        as given by :meth:`.header`.
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
        Returns the matching strings in a tuple. Either field can be ``None`` if nothing found.
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
        Get file header informing the user that the file is automatically generated,
        The information from :meth:`.generated_source_info` formatted as a comment block.
        """
        result = ""
        for line in self.generated_source_info:
            result += f"{self.COMMENT_START} {line}{self.COMMENT_END}\n"

        return result

    @property
    def generated_source_info(self) -> list[str]:
        """
        Return lines informing the user that the file is automatically generated,
        Containing info about the source of the generated register information.
        """
        # Default: Get git SHA from the user's current working directory.
        directory = Path(".")

        time_info = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        file_info = ""
        if self.register_list.source_definition_file is not None:
            # If the source definition file does exist, get git SHA from that directory instead.
            directory = self.register_list.source_definition_file.parent
            file_info = f" from file {self.register_list.source_definition_file.name}"

        commit_info = ""
        if git_commands_are_available(directory=directory):
            commit_info = f" at commit {get_git_commit(directory=directory)}"
        elif svn_commands_are_available(cwd=directory):
            commit_info = f" at revision {get_svn_revision_information(cwd=directory)}"

        info = f"Generated {time_info}{file_info}{commit_info}."

        return [
            f"This file is automatically generated by hdl_registers version {__version__}.",
            info,
            f"Register hash {self.register_list.object_hash}.",
        ]
