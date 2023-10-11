# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import copy
from pathlib import Path
from typing import TYPE_CHECKING

# Third party libraries
import tomli
from tsfpga.system_utils import read_file

# Local folder libraries
from .constant.bit_vector_constant import UnsignedVector
from .register_list import RegisterList

if TYPE_CHECKING:
    # Local folder libraries
    from .register import Register


def load_toml_file(toml_file: Path) -> str:
    if not toml_file.exists():
        raise FileNotFoundError(f"Requested TOML file does not exist: {toml_file}")

    raw_toml = read_file(toml_file)
    try:
        return tomli.loads(raw_toml)
    except Exception as exception_info:
        message = f"Error while parsing TOML file {toml_file}:\n{exception_info}"
        raise ValueError(message) from exception_info


def from_toml(
    module_name: str, toml_file: Path, default_registers: list["Register"] = None
) -> RegisterList:
    """
    Parse a register TOML file.

    Arguments:
        module_name: The name of the module that these registers belong to.
        toml_file: The TOML file path.
        default_registers: List of default registers.

    Returns:
        The resulting register list.
    """
    parser = RegisterParser(
        module_name=module_name,
        source_definition_file=toml_file,
        default_registers=default_registers,
    )
    toml_data = load_toml_file(toml_file)

    return parser.parse(toml_data)


class RegisterParser:
    recognized_constant_items = {"value", "description", "data_type"}

    recognized_register_items = {
        # Attributes of the register.
        "description",
        "mode",
        # Fields.
        "bit",
        "bit_vector",
        "enumeration",
        "integer",
    }

    recognized_register_array_items = {"array_length", "description", "register"}

    recognized_bit_items = {"description", "default_value"}
    recognized_bit_vector_items = {"description", "width", "default_value"}
    recognized_enumeration_items = {"description", "default_value", "element"}
    recognized_integer_items = {"description", "min_value", "max_value", "default_value"}

    def __init__(
        self,
        module_name: str,
        source_definition_file: Path,
        default_registers: list["Register"] = None,
    ):
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

    def parse(self, register_data: str) -> RegisterList:
        """
        Parse the TOML data.

        Arguments:
            register_data: TOML register data.

        Returns:
            The resulting register list.
        """
        if "constant" in register_data:
            for name, items in register_data["constant"].items():
                self._parse_constant(name=name, items=items)

        if "register" in register_data:
            for name, items in register_data["register"].items():
                self._parse_plain_register(name, items)

        if "register_array" in register_data:
            for name, items in register_data["register_array"].items():
                self._parse_register_array(name, items)

        return self._register_list

    def _parse_constant(self, name, items):
        if "value" not in items:
            message = (
                f'Constant "{name}" in {self._source_definition_file} does not have '
                'the required "value" property.'
            )
            raise ValueError(message)

        for item_name in items.keys():
            if item_name not in self.recognized_constant_items:
                message = (
                    f'Error while parsing constant "{name}" in {self._source_definition_file}: '
                    f'Unknown key "{item_name}".'
                )
                raise ValueError(message)

        value = items["value"]
        description = items.get("description", "")
        data_type_str = items.get("data_type")

        if data_type_str is not None:
            if not isinstance(value, str):
                raise ValueError(
                    f'Error while parsing constant "{name}" in '
                    f"{self._source_definition_file}: "
                    'May not set "data_type" for non-string constant.'
                )

            if data_type_str == "unsigned":
                value = UnsignedVector(value)
            else:
                raise ValueError(
                    f'Error while parsing constant "{name}" in '
                    f"{self._source_definition_file}: "
                    f'Invalid data type "{data_type_str}".'
                )

        self._register_list.add_constant(name=name, value=value, description=description)

    def _parse_plain_register(self, name, items):
        for item_name in items.keys():
            if item_name not in self.recognized_register_items:
                message = (
                    f'Error while parsing register "{name}" in {self._source_definition_file}: '
                    f'Unknown key "{item_name}".'
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
                    'the required "mode" property.'
                )
            mode = items["mode"]
            register = self._register_list.append_register(
                name=name, mode=mode, description=description
            )

        if "bit" in items:
            self._parse_bits(register=register, field_configurations=items["bit"])

        if "bit_vector" in items:
            self._parse_bit_vectors(register=register, field_configurations=items["bit_vector"])

        if "enumeration" in items:
            self._parse_enumerations(register=register, field_configurations=items["enumeration"])

        if "integer" in items:
            self._parse_integers(register=register, field_configurations=items["integer"])

    def _parse_register_array(self, name, items):
        for required_attribute in ["array_length", "register"]:
            if required_attribute not in items:
                message = (
                    f'Register array "{name}" in {self._source_definition_file} does not have '
                    f'the required "{required_attribute}" property.'
                )
                raise ValueError(message)

        for item_name in items:
            if item_name not in self.recognized_register_array_items:
                message = (
                    f'Error while parsing register array "{name}" in '
                    f'{self._source_definition_file}: Unknown key "{item_name}".'
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
                    f'{self._source_definition_file} does not have the required "mode" property.'
                )
                raise ValueError(message)

            for register_item_name in register_items.keys():
                if register_item_name not in self.recognized_register_items:
                    message = (
                        f'Error while parsing register "{register_name}" in array "{name}" in '
                        f'{self._source_definition_file}: Unknown key "{register_item_name}".'
                    )
                    raise ValueError(message)

            mode = register_items["mode"]
            description = register_items.get("description", "")

            register = register_array.append_register(
                name=register_name, mode=mode, description=description
            )

            if "bit" in register_items:
                self._parse_bits(register=register, field_configurations=register_items["bit"])

            if "bit_vector" in register_items:
                self._parse_bit_vectors(
                    register=register, field_configurations=register_items["bit_vector"]
                )

            if "enumeration" in register_items:
                self._parse_enumerations(
                    register=register, field_configurations=register_items["enumeration"]
                )

            if "integer" in register_items:
                self._parse_integers(
                    register=register, field_configurations=register_items["integer"]
                )

    def _check_field_items(
        self,
        register_name: str,
        field_name: str,
        field_items: dict,
        recognized_items: set,
        required_items: list,
    ):
        for item_name in required_items:
            if item_name not in field_items:
                message = (
                    f'Field "{field_name}" in register "{register_name}" in '
                    f"{self._source_definition_file} does not have the "
                    f'required "{item_name}" property.'
                )
                raise ValueError(message)

        for item_name in field_items.keys():
            if item_name not in recognized_items:
                message = (
                    f'Error while parsing field "{field_name}" in register '
                    f'"{register_name}" in {self._source_definition_file}: '
                    f'Unknown key "{item_name}".'
                )
                raise ValueError(message)

    def _parse_bits(self, register: "Register", field_configurations: dict):
        for field_name, field_items in field_configurations.items():
            self._check_field_items(
                register_name=register.name,
                field_name=field_name,
                field_items=field_items,
                recognized_items=self.recognized_bit_items,
                required_items=[],
            )

            description = field_items.get("description", "")
            default_value = field_items.get("default_value", "0")

            register.append_bit(
                name=field_name, description=description, default_value=default_value
            )

    def _parse_bit_vectors(self, register: "Register", field_configurations: dict):
        for field_name, field_items in field_configurations.items():
            self._check_field_items(
                register_name=register.name,
                field_name=field_name,
                field_items=field_items,
                recognized_items=self.recognized_bit_vector_items,
                required_items=["width"],
            )

            width = field_items["width"]

            description = field_items.get("description", "")
            default_value = field_items.get("default_value", "0" * width)

            register.append_bit_vector(
                name=field_name, description=description, width=width, default_value=default_value
            )

    def _parse_enumerations(self, register: "Register", field_configurations: dict):
        for field_name, field_items in field_configurations.items():
            self._check_field_items(
                register_name=register.name,
                field_name=field_name,
                field_items=field_items,
                recognized_items=self.recognized_enumeration_items,
                # This is checked also in the Enumeration class, which is needed if the user
                # is working directly with the Python API.
                # That is where we usually sanity check, to avoid duplication.
                # However, this particular check is needed here also since the logic for default
                # value below does not work if there are no elements.
                required_items=["element"],
            )

            description = field_items.get("description", "")
            elements = field_items.get("element")

            # The default "default value" is the first declared enumeration element.
            # Note that this works because dictionaries in Python are guaranteed ordered since
            # Python 3.7.
            default_value = field_items.get("default_value", list(elements)[0])

            register.append_enumeration(
                name=field_name,
                description=description,
                elements=elements,
                default_value=default_value,
            )

    def _parse_integers(self, register: "Register", field_configurations: dict):
        for field_name, field_items in field_configurations.items():
            self._check_field_items(
                register_name=register.name,
                field_name=field_name,
                field_items=field_items,
                recognized_items=self.recognized_integer_items,
                required_items=["max_value"],
            )

            max_value = field_items["max_value"]

            description = field_items.get("description", "")
            min_value = field_items.get("min_value", 0)
            default_value = field_items.get("default_value", min_value)

            register.append_integer(
                name=field_name,
                description=description,
                min_value=min_value,
                max_value=max_value,
                default_value=default_value,
            )
