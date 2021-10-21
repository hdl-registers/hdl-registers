# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import copy
import tomlkit

from tsfpga.system_utils import read_file
from .register_list import RegisterList
from .constant import Constant


def load_toml_file(toml_file):
    if not toml_file.exists():
        raise FileNotFoundError(f"Requested TOML file does not exist: {toml_file}")

    raw_toml = read_file(toml_file)
    try:
        return tomlkit.loads(raw_toml)
    except Exception as exception_info:
        message = f"Error while parsing TOML file {toml_file}:\n{exception_info}"
        raise ValueError(message) from exception_info


def from_toml(module_name, toml_file, default_registers=None):
    """
    Parse a register TOML file.

    Arguments:
        module_name (str): The name of the module that these registers belong to.
        toml_file (`pathlib.Path`): The TOML file path.
        default_registers (list(:class:`.Register`)): List of default registers.

    Returns:
        :class:`.RegisterList`: The resulting register list.
    """
    parser = RegisterParser(
        module_name=module_name,
        source_definition_file=toml_file,
        default_registers=default_registers,
    )
    toml_data = load_toml_file(toml_file)

    return parser.parse(toml_data)


class RegisterParser:

    recognized_constant_items = {"value", "description"}
    recognized_register_items = {"mode", "description", "bit", "bit_vector"}
    recognized_register_array_items = {"array_length", "description", "register"}
    recognized_bit_items = {"description", "default_value"}
    recognized_bit_vector_items = {"description", "width", "default_value"}

    def __init__(self, module_name, source_definition_file, default_registers):
        self._register_list = RegisterList(
            name=module_name, source_definition_file=source_definition_file
        )
        self._source_definition_file = source_definition_file

        self._default_register_names = []
        if default_registers is not None:
            # Perform deep copy of the mutable register objects
            self._register_list.register_objects = copy.deepcopy(default_registers)
            for register in default_registers:
                self._default_register_names.append(register.name)

        self._names_taken = set()

    def parse(self, register_data):
        """
        Parse the TOML data.

        Arguments:
            register_data (str): TOML register data.

        Returns:
            :class:`.RegisterList`: The resulting register list.
        """
        if "constant" in register_data:
            for name, items in register_data["constant"].items():
                self._parse_constant(name, items)

        if "register" in register_data:
            for name, items in register_data["register"].items():
                self._parse_plain_register(name, items)

        if "register_array" in register_data:
            for name, items in register_data["register_array"].items():
                self._parse_register_array(name, items)

        return self._register_list

    def _parse_constant(self, name, items):
        constant = Constant(name=name, value=items["value"])

        for item_name, item_value in items.items():
            if item_name not in self.recognized_constant_items:
                message = (
                    f'Error while parsing constant "{name}" in {self._source_definition_file}: '
                    f'Unknown key "{item_name}"'
                )
                raise ValueError(message)

            if item_name == "description":
                constant.description = item_value

        self._register_list.constants.append(constant)

    def _parse_plain_register(self, name, items):
        for item_name in items.keys():
            if item_name not in self.recognized_register_items:
                message = (
                    f'Error while parsing register "{name}" in {self._source_definition_file}: '
                    f'Unknown key "{item_name}"'
                )
                raise ValueError(message)

        description = items.get("description", "")

        if name in self._default_register_names:
            # Default registers can be "updated" in the sense that the user can use a custom
            # description and add whatever bits they use in the current module. They can not however
            # change the mode.
            if "mode" in items:
                message = (
                    f'Overloading register "{name}" in {self._source_definition_file}, '
                    'one can not change "mode" from default'
                )
                raise ValueError(message)

            register = self._register_list.get_register(name)
            register.description = description

        else:
            # If it is a new register however the mode has to be specified.
            if "mode" not in items:
                raise ValueError(
                    f'Register "{name}" in {self._source_definition_file} does not have '
                    '"mode" field'
                )
            mode = items["mode"]
            register = self._register_list.append_register(
                name=name, mode=mode, description=description
            )

        self._names_taken.add(name)

        if "bit" in items:
            self._parse_bits(register, items["bit"])

        if "bit_vector" in items:
            self._parse_bit_vectors(register, items["bit_vector"])

    def _parse_register_array(self, name, items):
        if name in self._names_taken:
            message = f'Duplicate name "{name}" in {self._source_definition_file}'
            raise ValueError(message)
        if "array_length" not in items:
            message = (
                f'Register array "{name}" in {self._source_definition_file} does not have '
                '"array_length" attribute'
            )
            raise ValueError(message)

        for item_name in items:
            if item_name not in self.recognized_register_array_items:
                message = (
                    f'Error while parsing register array "{name}" in '
                    f'{self._source_definition_file}: Unknown key "{item_name}"'
                )
                raise ValueError(message)

        length = items["array_length"]
        description = items.get("description", "")
        register_array = self._register_list.append_register_array(
            name=name, length=length, description=description
        )

        for register_name, register_items in items["register"].items():
            # The only required field
            if "mode" not in register_items:
                message = (
                    f'Register "{register_name}" within array "{name}" in '
                    f'{self._source_definition_file} does not have "mode" field'
                )
                raise ValueError(message)

            for register_item_name in register_items.keys():
                if register_item_name not in self.recognized_register_items:
                    message = (
                        f'Error while parsing register "{register_name}" in array "{name}" in '
                        f'{self._source_definition_file}: Unknown key "{register_item_name}"'
                    )
                    raise ValueError(message)

            mode = register_items["mode"]
            description = register_items.get("description", "")

            register = register_array.append_register(
                name=register_name, mode=mode, description=description
            )

            if "bit" in register_items:
                self._parse_bits(register, register_items["bit"])

            if "bit_vector" in register_items:
                self._parse_bit_vectors(register, register_items["bit_vector"])

    def _parse_bits(self, register, bit_configurations):
        for bit_name, bit_configuration in bit_configurations.items():
            for item_name in bit_configuration.keys():
                if item_name not in self.recognized_bit_items:
                    message = (
                        f'Error while parsing bit "{bit_name}" in register "{register.name}" in '
                        f'{self._source_definition_file}: Unknown key "{item_name}"'
                    )
                    raise ValueError(message)

            description = bit_configuration.get("description", "")
            default_value = bit_configuration.get("default_value", "0")

            register.append_bit(name=bit_name, description=description, default_value=default_value)

    def _parse_bit_vectors(self, register, bit_vector_configurations):
        for vector_name, vector_configuration in bit_vector_configurations.items():
            # The only required field
            if "width" not in vector_configuration:
                message = (
                    f'Bit vector "{vector_name}" in register "{register.name}" in file '
                    f'{self._source_definition_file} does not have a "width" property'
                )
                raise ValueError(message)

            for item_name in vector_configuration.keys():
                if item_name not in self.recognized_bit_vector_items:
                    message = (
                        f'Error while parsing bit vector "{vector_name}" in register '
                        f'"{register.name}" in {self._source_definition_file}: '
                        f'Unknown key "{item_name}"'
                    )
                    raise ValueError(message)

            width = vector_configuration["width"]

            description = vector_configuration.get("description", "")
            default_value = vector_configuration.get("default_value", "0" * width)

            register.append_bit_vector(vector_name, description, width, default_value)
