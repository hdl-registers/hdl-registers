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


def test_register_can_be_specified_with_and_without_type(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

mode = "w"

[hest]

type = "register"
mode = "r"
description = "zebra"
""",
    )
    register_list = from_toml(name="", toml_file=toml_path)

    assert register_list.get_register("apa").index == 0
    assert register_list.get_register("apa").mode == REGISTER_MODES["w"]
    assert register_list.get_register("apa").description == ""
    assert register_list.get_register("hest").index == 1
    assert register_list.get_register("hest").mode == REGISTER_MODES["r"]
    assert register_list.get_register("hest").description == "zebra"


def test_register_with_no_mode_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

description = "w"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert (
        str(exception_info.value)
        == f'Error while parsing register "apa" in {toml_path}: Missing required property "mode".'
    )


def test_unknown_register_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]

mode = "w"
dummy = 3
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register "test_reg" in {toml_path}: Got unknown property "dummy".'
    )


def test_array_register_can_be_specified_with_and_without_type(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.hest]

mode = "r"

[apa.zebra]

type = "register"
mode = "w"
description = "stuff"
""",
    )

    register_list = from_toml(name="", toml_file=toml_path)
    assert register_list.get_register(register_name="hest", register_array_name="apa").index == 0
    assert (
        register_list.get_register(register_name="hest", register_array_name="apa").mode
        == REGISTER_MODES["r"]
    )
    assert (
        register_list.get_register(register_name="hest", register_array_name="apa").description
        == ""
    )
    assert register_list.get_register(register_name="zebra", register_array_name="apa").index == 1
    assert (
        register_list.get_register(register_name="zebra", register_array_name="apa").mode
        == REGISTER_MODES["w"]
    )
    assert (
        register_list.get_register(register_name="zebra", register_array_name="apa").description
        == "stuff"
    )


def test_array_register_with_bad_type_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.hest]

type = "constant"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register "hest" within array "apa" in {toml_path}: '
        'Got unknown type "constant". Expected "register".'
    )


def test_array_register_with_no_mode_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"
array_length = 2

[apa.hest]

description = "nothing"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register "hest" within array "apa" in {toml_path}: '
        'Missing required property "mode".'
    )


def test_unknown_array_register_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_array]

type = "register_array"
array_length = 2

[test_array.hest]

mode = "r"
dummy = 3
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert (
        str(exception_info.value)
        == f'Error while parsing register "hest" within array "test_array" in {toml_path}: '
        'Got unknown property "dummy".'
    )


def test_plain_register_with_array_length_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

mode = "r_w"
array_length = 4
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register "apa" in {toml_path}: Got unknown property "array_length".'
    )


def test_unknown_register_mode_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_reg]

mode = "rw"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register "test_reg" in {toml_path}: '
        'Got unknown mode "rw". Expected one of "r", "w", "r_w", "wpulse", "r_wpulse".'
    )


def test_unknown_array_register_mode_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_array]

type = "register_array"
array_length = 2

[test_array.hest]

mode = "r_pulse"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert (
        str(exception_info.value) == f'Error while parsing register "hest" in {toml_path}: '
        'Got unknown mode "r_pulse". Expected one of "r", "w", "r_w", "wpulse", "r_wpulse".'
    )
