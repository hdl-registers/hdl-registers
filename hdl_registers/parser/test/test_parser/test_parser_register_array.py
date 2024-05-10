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


def test_register_array_without_register_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[dummy_array]

type = "register_array"
array_length = 2
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register array "dummy_array" in {toml_path}: '
        "Array must contain at least one register."
    )


def test_register_array_without_array_length_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[apa]

type = "register_array"

[apa.hest]

mode = "r_w"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == (
        f'Error while parsing register array "apa" in {toml_path}: '
        'Missing required property "array_length".'
    )


def test_unknown_register_array_property_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[test_array]

type = "register_array"
array_length = 2
dummy = 3

[test_array.hest]

mode = "r"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert (
        str(exception_info.value)
        == f'Error while parsing register array "test_array" in {toml_path}: '
        'Got unknown property "dummy".'
    )
