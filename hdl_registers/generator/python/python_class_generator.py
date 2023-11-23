# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import pickle
from pathlib import Path
from typing import Any

# First party libraries
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers
from hdl_registers.register_list import RegisterList


class PythonClassGenerator(RegisterCodeGenerator, RegisterCodeGeneratorHelpers):
    """
    Generate a Python class with register definitions.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "Python class"

    COMMENT_START = "#"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}.py"

    def __init__(self, register_list: RegisterList, output_folder: Path):
        super().__init__(register_list=register_list, output_folder=output_folder)

        self.pickle_file = self.output_folder / f"{self.name}.pickle"

    def create(self, **kwargs: Any) -> None:
        """
        Create the binary pickle also, apart from the class file.

        Note that this is a little bit hacky, preferably each generator should produce only
        one file.
        """
        super().create(**kwargs)

        with self.pickle_file.open("wb") as file_handle:
            pickle.dump(self.register_list, file_handle)

    def get_code(self, **kwargs: Any) -> str:
        """
        Save register list object to binary file (pickle) and create a python class
        that recreates it.

        Arguments:
            register_list (RegisterList): This register list object will be saved.
            output_folder (pathlib.Path): The pickle and python files will be saved here.
        """
        class_name = self.to_pascal_case(self.name)

        return f'''\
{self.header}
# Standard libraries
import pickle
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third party libraries
    from hdl_registers.register_list import RegisterList

THIS_DIR = Path(__file__).parent


class {class_name}:

    """
    Instantiate this class to get the RegisterList object for the '{self.name}' module.
    """

    def __new__(cls):
        """
        Recreate the RegisterList object from binary pickle.
        """
        with (THIS_DIR / "{self.pickle_file.name}").open("rb") as file_handle:
            return pickle.load(file_handle)


def get_register_list() -> "RegisterList":
    """
    Return a RegisterList object with the registers/constants from the '{self.name}' module.
    Recreated from a Python pickle file.
    """
    return {class_name}()
'''

    @property
    def should_create(self) -> bool:
        """
        Since this generator creates two files, where on is binary, it is impossible to do the
        version/hash check.
        Hence, set it to "always create".
        The mechanism "create if needed" should not be used for this generator anyway, since
        this generator is not designed to run in real-time like e.g. the VHDL generator.
        """
        return True
