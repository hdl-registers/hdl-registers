# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import datetime
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Third party libraries
from tsfpga.git_utils import get_git_commit, git_commands_are_available
from tsfpga.svn_utils import get_svn_revision_information, svn_commands_are_available
from tsfpga.system_utils import create_file, path_relative_to, read_file

# First party libraries
from hdl_registers import __version__ as hdl_registers_version

# Local folder libraries
from .register_code_generator_helpers import RegisterCodeGeneratorHelpers
from .reserved_keywords import RESERVED_KEYWORDS

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register_list import RegisterList


class RegisterCodeGenerator(ABC, RegisterCodeGeneratorHelpers):
    """
    Abstract interface and common functions for generating register code.
    Should be inherited by all custom code generators.

    Note that this base class also inherits from :class:`.RegisterCodeGeneratorHelpers`,
    meaning some useful methods are available in subclasses.
    """

    @property
    @abstractmethod
    def SHORT_DESCRIPTION(self) -> str:  # pylint: disable=invalid-name
        """
        A short description of what this generator produces.
        Will be used when printing status messages.

        Overload in subclass by setting e.g.

        .. code-block:: python

          SHORT_DESCRIPTION = "C++ header"

        as a static class member at the top of the class.
        """

    @property
    @abstractmethod  # type: ignore[override]
    def COMMENT_START(self) -> str:  # pylint: disable=invalid-name
        """
        The character(s) that start a comment line in the programming language that we are
        generating code for.

        Overload in subclass by setting e.g.

        .. code-block:: python

          COMMENT_START = "#"

        as a static class member at the top of the class.
        """

    @property
    @abstractmethod
    def output_file(self) -> Path:
        """
        Result will be placed in this file.

        Overload in a subclass to give the proper name to the code artifact.
        Probably using a combination of ``self.output_folder`` and ``self.name``.
        For example:

        .. code-block:: python

          @property
          def output_file(self) -> Path:
              return self.output_folder / f"{self.name}_regs.html"
        """

    @abstractmethod
    def get_code(self, **kwargs: Any) -> str:  # pylint: disable=unused-argument
        """
        Get the generated code as a string.

        Overload in a subclass where the code generation is implemented.

        Arguments:
            kwargs: Further optional parameters that can be used.
                Can send any number of named arguments, per the requirements of :meth:`.get_code`
                of any custom generators that inherit this class.
        """

    # Optionally set a non-zero default indentation level, expressed in number of spaces, in a
    # subclass for your code generator.
    # Will be used by e.g. the 'self.comment' method.
    DEFAULT_INDENTATION_LEVEL = 0

    # For some languages, comment lines have to be ended with special characters.
    # Optionally set this to a non-null string in a subclass.
    # For best formatting, leave a space character at the start of this string.
    COMMENT_END = ""

    # For a custom code generator, overload this value in a subclass.
    # This version number of the custom code generator class is added to the file header of
    # generated artifacts.
    # Changing the number will trigger a re-generate of all artifacts when 'create_if_needed'
    # is called.
    __version__ = "0.0.1"

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

    def create(self, **kwargs: Any) -> Path:
        """
        Generate the result artifact.
        I.e. create the :meth:`.output_file` containing the result from :meth:`.get_code` method.

        Arguments:
            kwargs: Further optional parameters that will be sent on to the
                :meth:`.get_code` method.
                See :meth:`.get_code` for details.

        Return:
            The path to the created file, i.e. :meth:`.output_file`.
        """
        output_file = self.output_file

        try:
            path_to_print = path_relative_to(path=output_file, other=Path("."))
        except ValueError:
            # Fails on Windows if CWD and the file are on different drives.
            path_to_print = output_file
        print(f"Creating {self.SHORT_DESCRIPTION} file: {path_to_print}")

        self._sanity_check()

        code = self.get_code(**kwargs)

        # Will create the containing folder unless it already exists.
        create_file(file=output_file, contents=code)

        return output_file

    def create_if_needed(self, **kwargs: Any) -> tuple[bool, Path]:
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
            Tuple, where first element is a boolean status, and second element is the path to the
            artifact that may or may not have been created.

            The boolean is the return value of :meth:`.should_create`.

            The path is the :meth:`.output_file` and is set always, even if the file was
            not created.
        """
        if self.should_create:
            create_path = self.create(**kwargs)
            return True, create_path

        return False, self.output_file

    @property
    def should_create(self) -> bool:
        """
        Indicates if a (re-)create of artifacts is needed.
        Will be True if any of these conditions are true:

        * Output file does not exist.
        * Generator version of artifact does not match current code version.
        * Artifact hash does not match :meth:`.RegisterList.object_hash` of the current
          register list.
          I.e. something in the register list has changed since the previous file was generated
          (e.g. a new register added).

        The version and hash checks above are dependent on the artifact file having a header
        as given by :meth:`.header`.
        """
        output_file = self.output_file

        if not output_file.exists():
            return True

        if (
            hdl_registers_version,
            self.__version__,
            self.register_list.object_hash,
        ) != self._find_versions_and_hash_of_existing_file(file_path=output_file):
            return True

        return False

    def _find_versions_and_hash_of_existing_file(
        self, file_path: Path
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Returns the matching strings in a tuple. Either field can be ``None`` if nothing found.
        """
        existing_file_content = read_file(file=file_path)

        result_package_version = None
        result_generator_version = None
        result_hash = None

        # This is either the very first line of the file, or starting on a new line.
        package_version_re = re.compile(
            (
                rf"(^|\n){self.COMMENT_START} This file is automatically generated by "
                rf"hdl-registers version (\S+)\.{self.COMMENT_END}\n"
            )
        )
        package_version_match = package_version_re.search(existing_file_content)
        if package_version_match:
            result_package_version = package_version_match.group(2)

        generator_version_re = re.compile(
            rf"\n{self.COMMENT_START} Code generator {self.__class__.__name__} "
            rf"version (\S+).{self.COMMENT_END}\n",
        )
        generator_version_match = generator_version_re.search(existing_file_content)
        if generator_version_match:
            result_generator_version = generator_version_match.group(1)

        hash_re = re.compile(
            rf"\n{self.COMMENT_START} Register hash ([0-9a-f]+)\.{self.COMMENT_END}\n"
        )
        hash_match = hash_re.search(existing_file_content)
        if hash_match:
            result_hash = hash_match.group(1)

        return result_package_version, result_generator_version, result_hash

    @property
    def header(self) -> str:
        """
        Get file header informing the user that the file is automatically generated.
        Basically the information from :meth:`.generated_source_info` formatted as a comment block.
        """
        return self.comment_block(text=self.generated_source_info, indent=0)

    @property
    def generated_source_info(self) -> list[str]:
        """
        Return lines informing the user that the file is automatically generated.
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
            (
                "This file is automatically generated by hdl-registers "
                f"version {hdl_registers_version}."
            ),
            f"Code generator {self.__class__.__name__} version {self.__version__}.",
            info,
            f"Register hash {self.register_list.object_hash}.",
        ]

    def _sanity_check(self) -> None:
        """
        Do some basic checks that no naming errors are present.
        Will raise exception if there is any error.

        In general, the user will know if these errors are present when the generated code is
        compiled/used since it will probably crash.
        But it is better to warn early, rather than the user finding out when compiling headers
        after a 1 hour FPGA build.

        We run this check at creation time, always and for every single generator.
        Hence the user will hopefully get warned when they generate e.g. a VHDL package at the start
        of the FPGA build that a register uses a reserved C++ name.
        This check takes roughly 140 us on a decent computer with a typical register list.
        Hence it is not a big deal that it might be run more than once for each register list.

        It is better to have it here in the generator rather than in the parser:
        1. Here it runs only when necessary, not adding time to parsing which is often done in
           real time.
        2. We also catch things that were added with the Python API.
        """
        self._check_reserved_keywords()
        self._check_for_name_clashes()

    def _check_reserved_keywords(self) -> None:
        """
        Check that no item in the register list matches a reserved keyword in any of the targeted
        generator languages.
        To minimize the risk that a generated artifact does not compile.
        """

        def check(name: str, description: str) -> None:
            if name.lower() in RESERVED_KEYWORDS:
                message = (
                    f'Error in register list "{self.name}": '
                    f'{description} name "{name}" is a reserved keyword.'
                )
                raise ValueError(message)

        for constant in self.register_list.constants:
            check(name=constant.name, description="Constant")

        for register, _ in self.iterate_registers():
            check(name=register.name, description="Register")

            for field in register.fields:
                check(name=field.name, description="Field")

        for register_array in self.iterate_register_arrays():
            check(name=register_array.name, description="Register array")

    def _check_for_name_clashes(self) -> None:
        """
        Check that there are no name clashes between items in the register list.
        To minimize the risk that a generated artifact does not compile.
        """
        self._check_for_constant_name_clashes()
        self._check_for_top_level_name_clashes()
        self._check_for_field_name_clashes()
        self._check_for_qualified_name_clashes()

    def _check_for_constant_name_clashes(self) -> None:
        """
        Check that there are no constants with the same name.
        """
        constant_names = set()
        for constant in self.register_list.constants:
            if constant.name in constant_names:
                message = (
                    f'Error in register list "{self.name}": '
                    f'Duplicate constant name "{constant.name}".'
                )
                raise ValueError(message)

            constant_names.add(constant.name)

    def _check_for_top_level_name_clashes(self) -> None:
        """
        Check that there are no
        * duplicate register names,
        * duplicate register array names,
        * register array names that clash with register names.
        """
        plain_register_names = set()
        for register in self.iterate_plain_registers():
            if register.name in plain_register_names:
                message = (
                    f'Error in register list "{self.name}": '
                    f'Duplicate plain register name "{register.name}".'
                )
                raise ValueError(message)

            plain_register_names.add(register.name)

        register_array_names = set()
        for register_array in self.iterate_register_arrays():
            if register_array.name in register_array_names:
                message = (
                    f'Error in register list "{self.name}": '
                    f'Duplicate register array name "{register_array.name}".'
                )
                raise ValueError(message)

            if register_array.name in plain_register_names:
                message = (
                    f'Error in register list "{self.name}": '
                    f'Register array "{register_array.name}" may not have same name as register.'
                )
                raise ValueError(message)

            register_array_names.add(register_array.name)

    def _check_for_field_name_clashes(self) -> None:
        """
        Check that no register contains fields with the same name.
        """
        for register, register_array in self.iterate_registers():
            field_names = set()

            for field in register.fields:
                if field.name in field_names:
                    register_description = (
                        f"{register_array.name}.{register.name}"
                        if register_array
                        else register.name
                    )
                    message = (
                        f'Error in register list "{self.name}": '
                        f'Duplicate field name "{field.name}" in register "{register_description}".'
                    )
                    raise ValueError(message)

                field_names.add(field.name)

    def _check_for_qualified_name_clashes(self) -> None:
        """
        Check that there are no name clashes when names of registers and fields are qualified.

        The register 'apa_hest' will give a conflict with the field 'apa.hest' since both will get
        e.g. a VHDL simulation method 'read_apa_hest'.
        Hence we need to check for these conflicts.
        """
        qualified_names = set()

        for register, register_array in self.iterate_registers():
            register_name = self.qualified_register_name(
                register=register, register_array=register_array
            )
            register_description = (
                f"{register_array.name}.{register.name}" if register_array else register.name
            )

            if register_name in qualified_names:
                message = (
                    f'Error in register list "{self.name}": '
                    f'Qualified name of register "{register_description}" '
                    f'("{register_name}") clashes with another item.'
                )
                raise ValueError(message)

            qualified_names.add(register_name)

            for field in register.fields:
                field_name = self.qualified_field_name(
                    register=register, register_array=register_array, field=field
                )

                if field_name in qualified_names:
                    field_description = f"{register_description}.{field.name}"
                    message = (
                        f'Error in register list "{self.name}": '
                        f'Qualified name of field "{field_description}" '
                        f'("{field_name}") clashes with another item.'
                    )
                    raise ValueError(message)

                qualified_names.add(field_name)
