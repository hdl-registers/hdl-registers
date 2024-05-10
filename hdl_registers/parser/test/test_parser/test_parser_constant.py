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
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.parser.toml import from_toml


def test_constants_in_toml(tmp_path):
    # Test all supported data types
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[data_width]

type = "constant"
value = 0xf
description = "the width"

[apa]

type = "constant"
value = 3.14

[hest]

type = "constant"
value = true

[zebra]

type = "constant"
value = "foo"

[base_address_hex]

type = "constant"
value = "0xFF01_2345"
data_type = "unsigned"

[base_address_bin]

type = "constant"
value = "0b1000_0011"
data_type = "unsigned"
""",
    )

    register_list = from_toml(name="", toml_file=toml_path)
    assert len(register_list.constants) == 6

    assert register_list.constants[0].name == "data_width"
    assert register_list.constants[0].value == 15
    assert register_list.constants[0].description == "the width"

    assert register_list.constants[1].name == "apa"
    assert register_list.constants[1].value == 3.14
    assert register_list.constants[1].description == ""

    assert register_list.constants[2].name == "hest"
    assert register_list.constants[2].value is True

    assert isinstance(register_list.constants[3], StringConstant)
    assert register_list.constants[3].name == "zebra"
    assert register_list.constants[3].value == "foo"

    assert isinstance(register_list.constants[4], UnsignedVectorConstant)
    assert register_list.constants[4].name == "base_address_hex"
    assert register_list.constants[4].value == "FF01_2345"

    assert isinstance(register_list.constants[5], UnsignedVectorConstant)
    assert register_list.constants[5].name == "base_address_bin"
    assert register_list.constants[5].value == "1000_0011"


def test_constant_without_value_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[data_width]

type = "constant"
description = "the width"
""",
    )
    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing constant "data_width" in {toml_path}: '
        'Missing required property "value".'
    )


def test_unknown_constant_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[data_width]

type = "constant"
value = 0xf
default_value = 0xf
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing constant "data_width" in {toml_path}: '
        'Got unknown property "default_value".'
    )


def test_unknown_constant_sub_item_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[data_width]

type = "constant"
value = 0xf

default_value.value = 0x3
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing constant "data_width" in {toml_path}: '
        'Got unknown property "default_value".'
    )


def test_data_type_on_non_string_constant_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[data_width]

type = "constant"
value = 0xf
data_type = "unsigned"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing constant "data_width" in {toml_path}: '
        'May not set "data_type" for non-string constant.'
    )


def test_invalid_string_constant_data_type_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[data_width]

type = "constant"
value = "0xff"
data_type = "signed"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing constant "data_width" in {toml_path}: Invalid data type "signed".'
    )
