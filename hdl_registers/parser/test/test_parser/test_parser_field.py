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


def test_register_field_without_type_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

mode = "r_w"

hest.width = 4
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "hest" in register "apa" in {toml_path}: '
        'Missing required property "type".'
    )


def test_array_register_field_without_type_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.hest]

mode = "r_w"

zebra.width = 4
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "zebra" in register "hest" within array "apa" in {toml_path}: '
        'Missing required property "type".'
    )


def test_register_field_with_unknown_type_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

mode = "r_w"

hest.type = "bits"
hest.width = 4
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "hest" in register "apa" in {toml_path}: '
        'Unknown field type "bits". Expected one of "bit", "bit_vector", "enumeration", "integer".'
    )


def test_array_register_field_with_unknown_type_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.hest]

mode = "r_w"

zebra.type = "bits"
zebra.width = 4
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "zebra" in register "hest" within array "apa" in {toml_path}: '
        'Unknown field type "bits". Expected one of "bit", "bit_vector", "enumeration", "integer".'
    )


def test_unknown_bit_field_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[dummy_reg]

mode = "w"

dummy_bit.type = "bit"
dummy_bit.description = "Stuff"

dummy_bit.dummy_integer.max_value = 3
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "dummy_bit" in register "dummy_reg" in {toml_path}: '
        'Unknown property "dummy_integer".'
    )


def test_unknown_bit_vector_field_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.dummy_reg]

mode = "w"

[apa.dummy_reg.dummy_bit_vector]

type = "bit_vector"
description = "Stuff"
width = 3
height = 4

""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "dummy_bit_vector" in register "dummy_reg" in '
        f'{toml_path}: Unknown property "height".'
    )


def test_bit_vector_field_without_width_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]
mode = "w"

test_bit_vector.type = "bit_vector"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "test_bit_vector" in register "test_reg" in {toml_path}: '
        'Missing required property "width".'
    )


def test_enumeration_field_without_elements_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.test_reg]

mode = "w"

test.type = "enumeration"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "test" in register "test_reg" in {toml_path}: '
        'Missing required property "element".'
    )


def test_integer_field_without_max_value_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]
mode = "w"

test_integer.type = "integer"
test_integer.min_value = 3
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "test_integer" in register "test_reg" in {toml_path}: '
        'Missing required property "max_value".'
    )
