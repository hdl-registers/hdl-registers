# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
import pytest
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_modes import REGISTER_MODES


def test_unknown_top_level_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
mode = "w"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing {toml_path}: Got unknown top-level property "mode".'
    )


def test_unknown_top_level_item_type_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
hest.type = "register_constant"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing "hest" in {toml_path}: Got unknown type "register_constant". '
        'Expected one of "constant", "register", "register_array".'
    )


def test_order_of_registers_and_fields(tmp_path):  # pylint: disable=too-many-statements
    toml_data = """
################################################################################
[data]

type = "register"
mode = "w"


################################################################################
[status]

type = "register"
mode = "r_w"
description = "Status register"

direction.type = "enumeration"
direction.description = "The direction mode"
direction.default_value = "input"
direction.element.passthrough = ""
direction.element.input = ""
direction.element.output = "use in output mode"

bad.type = "bit"
bad.description = "Bad things happen"

interrupts.type = "bit_vector"
interrupts.width = 4
interrupts.description = "Many interrupts"
interrupts.default_value = "0110"

not_good.type = "bit"
not_good.description = ""
not_good.default_value = "1"

count.type = "integer"
count.description = "The number of things"
count.min_value = -5
count.max_value = 15


################################################################################
[config]

type = "register_array"
array_length = 3
description = "A register array"


# ------------------------------------------------------------------------------
[config.input_settings]

type = "register"
description = "Input configuration"
mode = "r_w"

[config.input_settings.enable]

type = "bit"
description = "Enable things"
default_value = "1"

[config.input_settings.disable]

type = "bit"
description = ""
default_value = "0"

[config.input_settings.number]

type = "integer"
description = "Configure number"
max_value = 3
default_value = 1

[config.input_settings.size]

type = "enumeration"
default_value = "large"
element.small = ""
element.medium = ""
element.large = ""


# ------------------------------------------------------------------------------
[config.output_settings]

type = "register"
mode = "w"

[config.output_settings.data]

type = "bit_vector"
width = 16
description = "Some data"
default_value = "0000000000000011"
"""
    toml_file = create_file(file=tmp_path / "sensor_regs.toml", contents=toml_data)

    registers = from_toml(name="sensor", toml_file=toml_file).register_objects

    assert registers[0].name == "data"
    assert registers[0].mode == REGISTER_MODES["w"]
    assert registers[0].index == 0
    assert registers[0].description == ""
    assert registers[0].default_value == 0
    assert registers[0].fields == []

    assert registers[1].name == "status"
    assert registers[1].mode == REGISTER_MODES["r_w"]
    assert registers[1].index == 1
    assert registers[1].description == "Status register"

    # Enumeration field
    assert registers[1].fields[0].name == "direction"
    assert registers[1].fields[0].description == "The direction mode"
    assert registers[1].fields[0].width == 2
    assert registers[1].fields[0].default_value.name == "input"
    assert registers[1].fields[0].elements[0].name == "passthrough"
    assert registers[1].fields[0].elements[2].name == "output"
    assert registers[1].fields[0].elements[2].description == "use in output mode"

    # Bit field
    assert registers[1].fields[1].name == "bad"
    assert registers[1].fields[1].description == "Bad things happen"
    assert registers[1].fields[1].default_value == "0"

    # Bit vector field
    assert registers[1].fields[2].name == "interrupts"
    assert registers[1].fields[2].description == "Many interrupts"
    assert registers[1].fields[2].width == 4
    assert registers[1].fields[2].default_value == "0110"

    # Bit field
    assert registers[1].fields[3].name == "not_good"
    assert registers[1].fields[3].description == ""
    assert registers[1].fields[3].default_value == "1"

    # Integer field
    assert registers[1].fields[4].name == "count"
    assert registers[1].fields[4].description == "The number of things"
    assert registers[1].fields[4].width == 5
    assert registers[1].fields[4].min_value == -5
    assert registers[1].fields[4].max_value == 15
    assert registers[1].fields[4].default_value == -5

    assert registers[1].default_value == (
        # Enum
        1 * 2**0
        # Bit
        + 0 * 2**2
        # Bit vector
        + 6 * 2**3
        # Bit
        + 1 * 2**7
        # Integer, negative value converted to positive
        + 0b11011 * 2**8
    )

    assert registers[2].name == "config"
    assert registers[2].length == 3
    assert registers[2].description == "A register array"
    assert registers[2].index == 2 + 2 * 3 - 1
    assert len(registers[2].registers) == 2

    assert registers[2].registers[0].name == "input_settings"
    assert registers[2].registers[0].mode == REGISTER_MODES["r_w"]
    assert registers[2].registers[0].index == 0
    assert registers[2].registers[0].description == "Input configuration"
    assert registers[2].registers[0].fields[0].name == "enable"
    assert registers[2].registers[0].fields[0].description == "Enable things"
    assert registers[2].registers[0].fields[0].default_value == "1"
    assert registers[2].registers[0].fields[1].name == "disable"
    assert registers[2].registers[0].fields[1].description == ""
    assert registers[2].registers[0].fields[1].default_value == "0"
    assert registers[2].registers[0].fields[2].name == "number"
    assert registers[2].registers[0].fields[2].description == "Configure number"
    assert registers[2].registers[0].fields[2].default_value == 1
    assert registers[2].registers[0].fields[3].name == "size"
    assert registers[2].registers[0].fields[3].default_value.name == "large"
    assert registers[2].registers[0].default_value == (
        # First bit
        1 * 2**0
        # Integer
        + 1 * 2**2
        # Enumeration
        + 2 * 2**4
    )

    assert registers[2].registers[1].name == "output_settings"
    assert registers[2].registers[1].mode == REGISTER_MODES["w"]
    assert registers[2].registers[1].index == 1
    assert registers[2].registers[1].description == ""
    assert registers[2].registers[1].default_value == 3
    assert registers[2].registers[1].fields[0].name == "data"
    assert registers[2].registers[1].fields[0].description == "Some data"
    assert registers[2].registers[1].fields[0].width == 16
    assert registers[2].registers[1].fields[0].default_value == "0000000000000011"
