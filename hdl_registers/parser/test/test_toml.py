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
from hdl_registers.register import Register


def test_load_nonexistent_toml_file_should_raise_exception(tmp_path):
    toml_path = tmp_path / "apa.toml"
    with pytest.raises(FileNotFoundError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value) == f"Requested TOML file does not exist: {toml_path}"


def test_load_dirty_toml_file_should_raise_exception(tmp_path):
    toml = """
a = 1
b = "c"
"""
    toml_path = create_file(tmp_path / "apa.toml", toml)
    from_toml(name="", toml_file=toml_path)

    toml_path = create_file(tmp_path / "hest.toml", toml + "garbage")
    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    assert str(exception_info.value).startswith(
        f"Error while parsing TOML file {toml_path}:\n"
        "expected an equals, found eof at line 4 column 8"
    )


def test_default_registers(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[register.apa]

mode = "w"

[register.hest]

mode = "w"
""",
    )
    register_list = from_toml(
        name="",
        toml_file=toml_path,
        default_registers=[
            Register(name="config", index=0, mode="r_w", description=""),
            Register(name="status", index=1, mode="r", description=""),
        ],
    )

    # Default registers.
    assert register_list.get_register("config").index == 0
    assert register_list.get_register("status").index == 1
    # TOML registers.
    assert register_list.get_register("apa").index == 2
    assert register_list.get_register("hest").index == 3


def test_two_registers_with_same_name_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[register.status]

mode = "w"

[register.status]

mode = "w"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    expected = (
        f"Error while parsing TOML file {toml_path}:\n"
        "redefinition of table `register.status` for key `register.status` at line 6 column 1"
    )
    assert str(exception_info.value).startswith(expected)


def test_two_bit_fields_with_same_name_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[register.test_reg]

mode = "w"

[register.test_reg.bit.test_bit]

description = "Declaration 1"

[register.test_reg.bit.test_bit]

description = "Declaration 2"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(name="", toml_file=toml_path)
    expected = (
        f"Error while parsing TOML file {toml_path}:\n"
        "redefinition of table `register.test_reg.bit.test_bit` for key "
        "`register.test_reg.bit.test_bit` at line 10 column 1"
    )
    assert str(exception_info.value).startswith(expected)
