# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries

# Third party libraries
import pytest
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers.parser.json import _load_json_file, from_json
from hdl_registers.parser.toml import _load_toml_file, from_toml
from hdl_registers.parser.yaml import _load_yaml_file, from_yaml


def test_convert_big_toml_file(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
################################################################################
[register.data]

mode = "w"


################################################################################
[register.status]

mode = "r_w"
description = "Status register"

[register.status.bit.bad]

description = "Bad things happen"

[register.status.enumeration.direction]

description = "The direction mode"
default_value = "input"

element.passthrough = ""
element.input = ""
element.output = "use in output mode"

[register.status.bit.not_good]

description = ""
default_value = "1"

[register.status.bit_vector.interrupts]

width = 4
description = "Many interrupts"
default_value = "0110"

[register.status.integer.count]

description = "The number of things"
min_value = -5
max_value = 15


################################################################################
[register_array.config]

array_length = 3
description = "A register array"

# ------------------------------------------------------------------------------
[register_array.config.register.input_settings]

description = "Input configuration"
mode = "r_w"

[register_array.config.register.input_settings.bit.enable]

description = "Enable things"
default_value = "1"

[register_array.config.register.input_settings.integer.number]

description = "Configure number"
max_value = 3
default_value = 1

[register_array.config.register.input_settings.bit.disable]

description = ""
default_value = "0"

[register_array.config.register.input_settings.enumeration.size]

element.small = ""
element.large = ""


# ------------------------------------------------------------------------------
[register_array.config.register.output_settings]

mode = "w"

[register_array.config.register.output_settings.bit_vector.data]

width=16
description = "Some data"
default_value="0000000000000011"


################################################################################
[constant.burst_length_beats]

value = 256


################################################################################
[constant.data_mask]

value = "0b1100_1111"
data_type = "unsigned"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == ("Found register data in old format. See message above.")

    new_toml_path = tmp_path / "regs_version_6_format.toml"

    # Parsing of fixed file should pass without error.
    from_toml(name="", toml_file=new_toml_path)

    got = _load_toml_file(file_path=new_toml_path)

    # Expected data in the new format.
    # Note that the bit fields have been grouped together, and not in the order they appeared
    # in the original TOML.
    expected = {
        "data": {"mode": "w"},
        "status": {
            "mode": "r_w",
            "description": "Status register",
            "bad": {"type": "bit", "description": "Bad things happen"},
            "not_good": {"type": "bit", "description": "", "default_value": "1"},
            "direction": {
                "type": "enumeration",
                "description": "The direction mode",
                "default_value": "input",
                "element": {"passthrough": "", "input": "", "output": "use in output mode"},
            },
            "interrupts": {
                "type": "bit_vector",
                "width": 4,
                "description": "Many interrupts",
                "default_value": "0110",
            },
            "count": {
                "type": "integer",
                "description": "The number of things",
                "min_value": -5,
                "max_value": 15,
            },
        },
        "config": {
            "type": "register_array",
            "array_length": 3,
            "description": "A register array",
            "input_settings": {
                "description": "Input configuration",
                "mode": "r_w",
                "enable": {"type": "bit", "description": "Enable things", "default_value": "1"},
                "disable": {"type": "bit", "description": "", "default_value": "0"},
                "number": {
                    "type": "integer",
                    "description": "Configure number",
                    "max_value": 3,
                    "default_value": 1,
                },
                "size": {"type": "enumeration", "element": {"small": "", "large": ""}},
            },
            "output_settings": {
                "mode": "w",
                "data": {
                    "type": "bit_vector",
                    "width": 16,
                    "description": "Some data",
                    "default_value": "0000000000000011",
                },
            },
        },
        "burst_length_beats": {"type": "constant", "value": 256},
        "data_mask": {"type": "constant", "value": "0b1100_1111", "data_type": "unsigned"},
    }

    assert got == expected


def test_convert_small_json_file(tmp_path):
    json_path = create_file(
        file=tmp_path / "regs.json",
        contents="""
{
    "register": {
        "apa": {
            "mode": "r_w",
            "description": "Apa.",
            "bit": {
                "enable": {
                    "description": "Enable.",
                    "default_value": "1"
                }
            }
        },
        "hest": {
            "mode": "r",
            "description": "Hest.",
            "bit": {
                "disable": {
                    "description": "Disable."
                }
            }
        }
    }
}
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_json(name="", json_file=json_path)
    assert str(exception_info.value) == ("Found register data in old format. See message above.")

    new_json_path = tmp_path / "regs_version_6_format.json"

    # Parsing of fixed file should pass without error.
    from_json(name="", json_file=new_json_path)

    got = _load_json_file(file_path=new_json_path)
    expected = {
        "apa": {
            "mode": "r_w",
            "description": "Apa.",
            "enable": {"type": "bit", "description": "Enable.", "default_value": "1"},
        },
        "hest": {
            "mode": "r",
            "description": "Hest.",
            "disable": {"type": "bit", "description": "Disable."},
        },
    }

    assert got == expected


def test_convert_small_yaml_file(tmp_path):
    yaml_path = create_file(
        file=tmp_path / "regs.yaml",
        contents="""
register:
  apa:
    mode: r_w
    description: Apa.
    bit:
      enable:
        default_value: '1'
        description: Enable.

  hest:
    mode: r
    description: Hest.
    bit:
      disable:
        description: Disable.
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_yaml(name="", yaml_file=yaml_path)
    assert str(exception_info.value) == ("Found register data in old format. See message above.")

    new_yaml_path = tmp_path / "regs_version_6_format.yaml"

    # Parsing of fixed file should pass without error.
    from_yaml(name="", yaml_file=new_yaml_path)

    got = _load_yaml_file(file_path=new_yaml_path)
    expected = {
        "apa": {
            "mode": "r_w",
            "description": "Apa.",
            "enable": {"type": "bit", "description": "Enable.", "default_value": "1"},
        },
        "hest": {
            "mode": "r",
            "description": "Hest.",
            "disable": {"type": "bit", "description": "Disable."},
        },
    }

    assert got == expected
