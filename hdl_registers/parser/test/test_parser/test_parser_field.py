# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import pytest
from tsfpga.system_utils import create_file

from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
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


def test_unknown_bit_property_should_raise_exception(tmp_path):
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


def test_unknown_bit_vector_property_should_raise_exception(tmp_path):
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


def test_bit_vector_without_width_should_raise_exception(tmp_path):
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


def test_numerical_interpretation_properties_on_anything_but_bit_vector_should_raise_exception(
    tmp_path,
):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]
mode = "w"

my_field.type = "integer"
my_field.max_value = 255
my_field.numerical_interpretation = "unsigned"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "my_field" in register "test_reg" in {toml_path}: '
        'Unknown property "numerical_interpretation".'
    )


def test_bit_vector_different_numerical_interpretations(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]
mode = "w"

unsigned_implied.type = "bit_vector"
unsigned_implied.width = 1

unsigned_explicit.type = "bit_vector"
unsigned_explicit.width = 2
unsigned_explicit.numerical_interpretation = "unsigned"

signed.type = "bit_vector"
signed.width = 3
signed.numerical_interpretation = "signed"

ufixed_implied.type = "bit_vector"
ufixed_implied.width = 4
ufixed_implied.numerical_interpretation = "unsigned_fixed_point"

ufixed_explicit.type = "bit_vector"
ufixed_explicit.width = 5
ufixed_explicit.numerical_interpretation = "unsigned_fixed_point"
ufixed_explicit.min_bit_index = -2

sfixed_implied.type = "bit_vector"
sfixed_implied.width = 6
sfixed_implied.numerical_interpretation = "signed_fixed_point"

sfixed_explicit.type = "bit_vector"
sfixed_explicit.width = 7
sfixed_explicit.numerical_interpretation = "signed_fixed_point"
sfixed_explicit.min_bit_index = 2
""",
    )
    register = from_toml(name="", toml_file=toml_path).get_register("test_reg")

    unsigned_implied = register.get_field("unsigned_implied").numerical_interpretation
    assert isinstance(unsigned_implied, Unsigned)
    assert unsigned_implied.bit_width == 1

    unsigned_explicit = register.get_field("unsigned_explicit").numerical_interpretation
    assert isinstance(unsigned_explicit, Unsigned)
    assert unsigned_explicit.bit_width == 2

    signed = register.get_field("signed").numerical_interpretation
    assert isinstance(signed, Signed)
    assert signed.bit_width == 3

    ufixed_implied = register.get_field("ufixed_implied").numerical_interpretation
    assert isinstance(ufixed_implied, UnsignedFixedPoint)
    assert ufixed_implied.max_bit_index == 3
    assert ufixed_implied.min_bit_index == 0

    ufixed_explicit = register.get_field("ufixed_explicit").numerical_interpretation
    assert isinstance(ufixed_explicit, UnsignedFixedPoint)
    assert ufixed_explicit.max_bit_index == 2
    assert ufixed_explicit.min_bit_index == -2

    sfixed_implied = register.get_field("sfixed_implied").numerical_interpretation
    assert isinstance(sfixed_implied, SignedFixedPoint)
    assert sfixed_implied.max_bit_index == 5
    assert sfixed_implied.min_bit_index == 0

    sfixed_explicit = register.get_field("sfixed_explicit").numerical_interpretation
    assert isinstance(sfixed_explicit, SignedFixedPoint)
    assert sfixed_explicit.max_bit_index == 8
    assert sfixed_explicit.min_bit_index == 2


def test_bit_vector_unknown_numerical_interpretation_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]
mode = "w"

my_field.type = "bit_vector"
my_field.width = 2
my_field.numerical_interpretation = "apa"
""",
    )
    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing field "my_field" in register "test_reg" in {toml_path}: '
        'Unknown value "apa" for property "numerical_interpretation". '
        'Expected one of "unsigned", "signed", "unsigned_fixed_point", "signed_fixed_point".'
    )


def test_enumeration_without_elements_should_raise_exception(tmp_path):
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


def test_integer_without_max_value_should_raise_exception(tmp_path):
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
