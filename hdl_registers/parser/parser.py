# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import copy
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Third party libraries
import tomli_w
import yaml
from tsfpga import DEFAULT_FILE_ENCODING

# First party libraries
from hdl_registers.about import WEBSITE_URL
from hdl_registers.constant.bit_vector_constant import UnsignedVector
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register import Register
    from hdl_registers.register_mode import RegisterMode


class RegisterParser:
    # Attributes of the constant.
    recognized_constant_items = {"type", "value", "description", "data_type"}
    # Note that "type" being present is implied. We would not be parsing a constant unless we
    # know it to be a "constant" type.
    # So we save some CPU cycles by not checking for it.
    required_constant_items = ["value"]

    # Attributes of the register.
    # Anything apart from these are names of fields.
    default_register_items = {
        "type",
        "mode",
        "description",
    }
    # While a 'mode' is required for a register, it may NOT be specified/changed in the data file
    # for a default register.
    # Hence this property is handled separately.
    # And hence, registers have no required items.

    # Attributes of the register array.
    # Anything apart from these are names of registers.
    default_register_array_items = {"type", "array_length", "description"}
    # Note that "type" being present is implied.
    # We would not be parsing a register array unless we know it to be a "register_array" type.
    # So we save some CPU cycles by not checking for it.
    required_register_array_items = ["array_length"]

    # Attributes of the "bit" register field.
    recognized_bit_items = {"type", "description", "default_value"}
    # Note that "type" being present is implied.
    # We would not be parsing a bit unless we know it to be a "bit" type.
    # So we save some CPU cycles by not checking for it.
    required_bit_items: list[str] = []

    # Attributes of the "bit_vector" register field.
    recognized_bit_vector_items = {"type", "description", "width", "default_value"}
    # Note that "type" being present is implied.
    # We would not be parsing a bit_vector unless we know it to be a "bit_vector" type.
    # So we save some CPU cycles by not checking for it.
    required_bit_vector_items = ["width"]

    # Attributes of the "enumeration" register field.
    recognized_enumeration_items = {"type", "description", "default_value", "element"}
    # Note that "type" being present is implied.
    # We would not be parsing a enumeration unless we know it to be a "enumeration" type.
    # So we save some CPU cycles by not checking for it.
    required_enumeration_items = ["element"]

    # Attributes of the "integer" register field.
    recognized_integer_items = {"type", "description", "min_value", "max_value", "default_value"}
    # Note that "type" being present is implied.
    # We would not be parsing a integer unless we know it to be a "integer" type.
    # So we save some CPU cycles by not checking for it.
    required_integer_items = ["max_value"]

    def __init__(
        self,
        name: str,
        source_definition_file: Path,
        default_registers: Optional[list["Register"]] = None,
    ):
        """
        Arguments:
            name: The name of the register list.
            source_definition_file: The source file that defined this register list.
                Will be displayed in generated source code and documentation
                for traceability.
            default_registers: List of default registers.
                Note that this list with :class:`.Register` objects will be deep copied, so you can
                use the same list many times without worrying about mutability.
        """
        self._register_list = RegisterList(name=name, source_definition_file=source_definition_file)
        self._source_definition_file = source_definition_file

        self._default_register_names = []
        if default_registers:
            # Perform deep copy of the mutable register objects.
            # Ignore a mypy error that seems buggy.
            # We are assigning list[Register] to list[Register | RegisterArray]
            # which should be absolutely fine, but mypy warns.
            self._register_list.register_objects = copy.deepcopy(
                default_registers  # type: ignore[arg-type]
            )
            for register in default_registers:
                self._default_register_names.append(register.name)

    def parse(self, register_data: dict[str, Any]) -> RegisterList:
        """
        Parse the register data.

        Arguments:
            register_data: Register data as a dictionary.

        Return:
            The resulting register list.
        """
        for old_top_level_key_name in ["constant", "register", "register_array"]:
            if old_top_level_key_name in register_data:
                source_file = self._source_definition_file
                output_file = (
                    source_file.parent.resolve()
                    / f"{source_file.stem}_version_6_format{source_file.suffix}"
                )

                print(
                    f"""
ERROR: Parsing register data that appears to be in the old pre-6.0.0 format.
ERROR: For more information, see: {WEBSITE_URL}/rst/basic_feature/basic_feature_register_modes.html
ERROR: Your data will be automatically converted to the new format and saved to: {output_file}
ERROR: Please inspect that file and update your data file to the new format.
"""
                )
                _save_to_new_format(old_data=register_data, output_file=output_file)
                raise ValueError("Found register data in old format. See message above.")

        parser_methods = {
            "constant": self._parse_constant,
            "register": self._parse_plain_register,
            "register_array": self._parse_register_array,
        }

        for top_level_name, top_level_items in register_data.items():
            if not isinstance(top_level_items, dict):
                message = (
                    f"Error while parsing {self._source_definition_file}: "
                    f'Got unknown top-level property "{top_level_name}".'
                )
                raise ValueError(message)

            top_level_type = top_level_items.get("type", "register")

            if top_level_type not in parser_methods:
                valid_types_str = ", ".join(f'"{parser_key}"' for parser_key in parser_methods)
                message = (
                    f'Error while parsing "{top_level_name}" in {self._source_definition_file}: '
                    f'Got unknown type "{top_level_type}". Expected one of {valid_types_str}.'
                )
                raise ValueError(message)

            parser_methods[top_level_type](name=top_level_name, items=top_level_items)

        return self._register_list

    def _parse_constant(self, name: str, items: dict[str, Any]) -> None:
        for item_name in self.required_constant_items:
            if item_name not in items:
                message = (
                    f'Error while parsing constant "{name}" in {self._source_definition_file}: '
                    f'Missing required property "{item_name}".'
                )
                raise ValueError(message)

        for item_name in items.keys():
            if item_name not in self.recognized_constant_items:
                message = (
                    f'Error while parsing constant "{name}" in {self._source_definition_file}: '
                    f'Got unknown property "{item_name}".'
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

    def _parse_plain_register(self, name: str, items: dict[str, Any]) -> None:
        description = items.get("description", "")

        if name in self._default_register_names:
            # Default registers can be "updated" in the sense that the user can set a custom
            # 'description' and add whatever fields they want in the current register list.
            # They may not, however, change the 'mode' which is part of the default definition.
            if "mode" in items:
                message = (
                    f'Error while parsing register "{name}" in {self._source_definition_file}: '
                    'A "mode" may not be specified for a default register.'
                )
                raise ValueError(message)

            register = self._register_list.get_register(register_name=name)
            register.description = description

        else:
            # If it is a new register however, the 'mode' has to be specified.
            if "mode" not in items:
                message = (
                    f'Error while parsing register "{name}" in {self._source_definition_file}: '
                    f'Missing required property "mode".'
                )
                raise ValueError(message)

            mode = self._get_mode(mode_name=items["mode"], register_name=name)

            register = self._register_list.append_register(
                name=name, mode=mode, description=description
            )

        self._parse_register_fields(register=register, register_items=items, register_array_note="")

    def _get_mode(self, mode_name: str, register_name: str) -> "RegisterMode":
        if mode_name in REGISTER_MODES:
            return REGISTER_MODES[mode_name]

        valid_modes_str = ", ".join(f'"{mode_key}"' for mode_key in REGISTER_MODES)
        message = (
            f'Error while parsing register "{register_name}" in {self._source_definition_file}: '
            f'Got unknown mode "{mode_name}". Expected one of {valid_modes_str}.'
        )
        raise ValueError(message)

    def _parse_register_fields(
        self,
        register_items: dict[str, Any],
        register: "Register",
        register_array_note: str,
    ) -> None:
        # Add any fields that are specified.
        for item_name, item_value in register_items.items():
            # Skip default items so we only get the fields.
            if item_name in self.default_register_items:
                continue

            if not isinstance(item_value, dict):
                message = (
                    f'Error while parsing register "{register.name}"{register_array_note} '
                    f"in {self._source_definition_file}: "
                    f'Got unknown property "{item_name}".'
                )
                raise ValueError(message)

            if "type" not in item_value:
                message = (
                    f'Error while parsing field "{item_name}" in register '
                    f'"{register.name}"{register_array_note} in {self._source_definition_file}: '
                    'Missing required property "type".'
                )
                raise ValueError(message)

            field_type = item_value["type"]

            parser_methods = {
                "bit": self._parse_bit,
                "bit_vector": self._parse_bit_vector,
                "enumeration": self._parse_enumeration,
                "integer": self._parse_integer,
            }

            if field_type not in parser_methods:
                valid_types_str = ", ".join(f'"{parser_key}"' for parser_key in parser_methods)
                message = (
                    f'Error while parsing field "{item_name}" in register '
                    f'"{register.name}"{register_array_note} in {self._source_definition_file}: '
                    f'Unknown field type "{field_type}". Expected one of {valid_types_str}.'
                )
                raise ValueError(message)

            parser_methods[field_type](
                register=register, field_name=item_name, field_items=item_value
            )

    def _parse_register_array(self, name: str, items: dict[str, Any]) -> None:
        for required_property in self.required_register_array_items:
            if required_property not in items:
                message = (
                    f'Error while parsing register array "{name}" in '
                    f"{self._source_definition_file}: "
                    f'Missing required property "{required_property}".'
                )
                raise ValueError(message)

        register_array_length = items["array_length"]
        register_array_description = items.get("description", "")
        register_array = self._register_list.append_register_array(
            name=name, length=register_array_length, description=register_array_description
        )

        # Add all registers that are specified.
        found_at_least_one_register = False
        for item_name, item_value in items.items():
            # Skip default items so we only get the registers.
            if item_name in self.default_register_array_items:
                continue

            found_at_least_one_register = True

            if not isinstance(item_value, dict):
                message = (
                    f'Error while parsing register array "{name}" in '
                    f"{self._source_definition_file}: "
                    f'Got unknown property "{item_name}".'
                )
                raise ValueError(message)

            item_type = item_value.get("type", "register")
            if item_type != "register":
                message = (
                    f'Error while parsing register "{item_name}" within array "{name}" in '
                    f"{self._source_definition_file}: "
                    f'Got unknown type "{item_type}". Expected "register".'
                )
                raise ValueError(message)

            # A 'mode' is semi-required for plain registers, but always required for
            # array registers.
            if "mode" not in item_value:
                raise ValueError(
                    f'Error while parsing register "{item_name}" within array "{name}" in '
                    f"{self._source_definition_file}: "
                    f'Missing required property "mode".'
                )
            register_mode = self._get_mode(mode_name=item_value["mode"], register_name=item_name)

            register_description = item_value.get("description", "")

            register = register_array.append_register(
                name=item_name, mode=register_mode, description=register_description
            )

            self._parse_register_fields(
                register_items=item_value,
                register=register,
                register_array_note=f' within array "{name}"',
            )

        if not found_at_least_one_register:
            message = (
                f'Error while parsing register array "{name}" in {self._source_definition_file}: '
                "Array must contain at least one register."
            )
            raise ValueError(message)

    def _check_field_items(
        self,
        register_name: str,
        field_name: str,
        field_items: dict[str, Any],
        recognized_items: set[str],
        required_items: list[str],
    ) -> None:
        """
        Will raise exception if anything is wrong.
        """
        for item_name in required_items:
            if item_name not in field_items:
                message = (
                    f'Error while parsing field "{field_name}" in register "{register_name}" in '
                    f"{self._source_definition_file}: "
                    f'Missing required property "{item_name}".'
                )
                raise ValueError(message)

        for item_name in field_items.keys():
            if item_name not in recognized_items:
                message = (
                    f'Error while parsing field "{field_name}" in register '
                    f'"{register_name}" in {self._source_definition_file}: '
                    f'Unknown property "{item_name}".'
                )
                raise ValueError(message)

    def _parse_bit(
        self, register: "Register", field_name: str, field_items: dict[str, Any]
    ) -> None:
        self._check_field_items(
            register_name=register.name,
            field_name=field_name,
            field_items=field_items,
            recognized_items=self.recognized_bit_items,
            required_items=self.required_bit_items,
        )

        description = field_items.get("description", "")
        default_value = field_items.get("default_value", "0")

        register.append_bit(name=field_name, description=description, default_value=default_value)

    def _parse_bit_vector(
        self, register: "Register", field_name: str, field_items: dict[str, Any]
    ) -> None:
        self._check_field_items(
            register_name=register.name,
            field_name=field_name,
            field_items=field_items,
            recognized_items=self.recognized_bit_vector_items,
            required_items=self.required_bit_vector_items,
        )

        width = field_items["width"]

        description = field_items.get("description", "")
        default_value = field_items.get("default_value", "0" * width)

        register.append_bit_vector(
            name=field_name, description=description, width=width, default_value=default_value
        )

    def _parse_enumeration(
        self, register: "Register", field_name: str, field_items: dict[str, Any]
    ) -> None:
        self._check_field_items(
            register_name=register.name,
            field_name=field_name,
            field_items=field_items,
            recognized_items=self.recognized_enumeration_items,
            # Check that we have at least one element.
            # This is checked also in the Enumeration class, which is needed if the user
            # is working directly with the Python API.
            # That is where we usually sanity check, to avoid duplication.
            # However, this particular check is needed here also since the logic for default
            # value below does not work if there are no elements.
            required_items=self.required_enumeration_items,
        )

        description = field_items.get("description", "")
        # We assert above that the enumeration has at least one element.
        # Meaning that the result of this get can not be None, as mypy thinks.
        elements: dict[str, str] = field_items.get("element")  # type: ignore[assignment]

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

    def _parse_integer(
        self, register: "Register", field_name: str, field_items: dict[str, Any]
    ) -> None:
        self._check_field_items(
            register_name=register.name,
            field_name=field_name,
            field_items=field_items,
            recognized_items=self.recognized_integer_items,
            required_items=self.required_integer_items,
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


def _convert_to_new_format(  # pylint: disable=too-many-locals
    old_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Convert pre-6.0.0 format to the new format.
    """

    def _get_register_dict(register_items: dict[str, Any]) -> dict[str, Any]:
        register_dict = dict()

        for register_item_name, register_item_value in register_items.items():
            if register_item_name in RegisterParser.default_register_items:
                register_dict[register_item_name] = register_item_value

            elif register_item_name in ["bit", "bit_vector", "enumeration", "integer"]:
                for field_name, field_items in register_item_value.items():
                    field_dict = dict(type=register_item_name)

                    for field_item_name, field_item_value in field_items.items():
                        field_dict[field_item_name] = field_item_value

                    register_dict[field_name] = field_dict

            else:
                raise ValueError(
                    f"Unknown item {register_item_name}. "
                    "Looks like an error in the user data file."
                )

        return register_dict

    result = dict()

    def _add_item(name: str, items: dict[str, Any]) -> None:
        if name in result:
            raise ValueError(f"Duplicate item {name}")

        result[name] = items

    if "register" in old_data:
        for register_name, register_items in old_data["register"].items():
            register_dict = _get_register_dict(register_items=register_items)
            _add_item(name=register_name, items=register_dict)

    if "register_array" in old_data:
        for register_array_name, register_array_items in old_data["register_array"].items():
            register_array_dict: dict[str, Any] = dict(type="register_array")

            for register_array_item_name, register_array_item_value in register_array_items.items():
                if register_array_item_name in RegisterParser.default_register_array_items:
                    register_array_dict[register_array_item_name] = register_array_item_value

                elif register_array_item_name == "register":
                    for register_name, register_items in register_array_item_value.items():
                        register_array_dict[register_name] = _get_register_dict(
                            register_items=register_items
                        )

                else:
                    raise ValueError(
                        f"Unknown item {register_array_item_name}. "
                        "Looks like an error in the user data file."
                    )

            _add_item(name=register_array_name, items=register_array_dict)

    if "constant" in old_data:
        for constant_name, constant_items in old_data["constant"].items():
            constant_dict = dict(type="constant")

            for constant_item_name, constant_item_value in constant_items.items():
                constant_dict[constant_item_name] = constant_item_value

            _add_item(name=constant_name, items=constant_dict)

    return result


def _save_to_new_format(old_data: dict[str, Any], output_file: Path) -> None:
    """
    Save the old data to the new format.
    """
    new_data = _convert_to_new_format(old_data=old_data)

    if output_file.suffix == ".toml":
        with open(output_file, "wb") as file_handle:
            tomli_w.dump(new_data, file_handle, multiline_strings=True)

        return

    if output_file.suffix == ".json":
        with open(output_file, "w", encoding=DEFAULT_FILE_ENCODING) as file_handle:
            json.dump(new_data, file_handle, indent=4)

        return

    if output_file.suffix == ".yaml":
        with open(output_file, "w", encoding=DEFAULT_FILE_ENCODING) as file_handle:
            yaml.dump(new_data, file_handle)

        return

    raise ValueError(f"Unknown file format {output_file}")
