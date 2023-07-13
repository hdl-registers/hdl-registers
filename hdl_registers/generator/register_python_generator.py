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

# Third party libraries
from tsfpga.system_utils import create_file

# Local folder libraries
from .register_code_generator import RegisterCodeGenerator


class RegisterPythonGenerator(RegisterCodeGenerator):
    """
    Generate a Python class with register definitions.
    """

    def __init__(self, module_name, generated_info):
        """
        Arguments:
            module_name (str): The name of the register map.
            generated_info (list(str)): Will be placed in the file headers.
        """
        self.module_name = module_name
        self.generated_info = generated_info
        self._class_name = self._to_pascal_case(module_name)

    def create_class(self, register_list, output_folder):
        """
        Save register list object to binary file (pickle) and create a python class
        that recreates it.

        Arguments:
            register_list (RegisterList): This register list object will be saved.
            output_folder (pathlib.Path): The pickle and python files will be saved here.
        """
        pickle_file = output_folder / f"{self.module_name}.pickle"
        py_file = output_folder / f"{self.module_name}.py"

        py_code = f'''\
{self._file_header}
import pickle
from pathlib import Path

THIS_DIR = Path(__file__).parent


class {self._class_name}:

    """
    Instantiate this class to get the RegisterList object for the '{self.module_name}' module.
    """

    def __new__(cls):
        """
        Recreate the RegisterList object from binary pickle.
        """
        with (THIS_DIR / "{pickle_file.name}").open("rb") as file_handle:
            return pickle.load(file_handle)


def get_register_list():
    """
    Return a RegisterList object with the registers/constants from the '{self.module_name}' module.
    Recreated from a python pickle file.
    """
    return {self._class_name}()
'''
        create_file(py_file, py_code)

        with pickle_file.open("wb") as file_handle:
            pickle.dump(register_list, file_handle)

    @property
    def _file_header(self):
        return "".join([self._comment(header_line) for header_line in self.generated_info])

    @staticmethod
    def _comment(comment, indentation=0):
        indent = " " * indentation
        return f"{indent}# {comment}\n"
