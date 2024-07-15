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
from hdl_registers.parser.json import from_json
from hdl_registers.register import Register
from hdl_registers.register_modes import REGISTER_MODES


def test_load_nonexistent_json_file_should_raise_exception(tmp_path):
    json_path = tmp_path / "apa.json"
    with pytest.raises(FileNotFoundError) as exception_info:
        from_json(name="", json_file=json_path)
    assert str(exception_info.value) == f"Requested JSON file does not exist: {json_path}"


def test_load_dirty_json_file_should_raise_exception(tmp_path):
    json = """
{
    "config": {
        "mode": "r_w"
    }
}
"""
    json_path = create_file(tmp_path / "apa.json", json)
    from_json(name="", json_file=json_path)

    json_path = create_file(tmp_path / "hest.json", json + "garbage")
    with pytest.raises(ValueError) as exception_info:
        from_json(name="", json_file=json_path)
    assert str(exception_info.value).startswith(
        f"Error while parsing JSON file {json_path}:\nExtra data: "
    )


def test_default_registers(tmp_path):
    json_path = create_file(
        file=tmp_path / "regs.json",
        contents="""
{
    "apa": {
        "mode": "r_w",
        "description": "Apa.",
        "enable": {
            "type": "bit",
            "description": "Enable.",
            "default_value": "1"
        }
    },
    "hest": {
        "mode": "r",
        "description": "Hest.",
        "disable": {
            "type": "bit",
            "description": "Disable."
        }
    }
}
""",
    )
    register_list = from_json(
        name="",
        json_file=json_path,
        default_registers=[
            Register(name="config", index=0, mode=REGISTER_MODES["r_w"], description=""),
            Register(name="status", index=1, mode=REGISTER_MODES["r"], description=""),
        ],
    )

    # Default registers.
    assert register_list.get_register("config").index == 0
    assert register_list.get_register("status").index == 1

    # json registers.
    assert register_list.get_register("apa").index == 2
    assert register_list.get_register("apa").mode == REGISTER_MODES["r_w"]
    assert register_list.get_register("apa").description == "Apa."
    assert len(register_list.get_register("apa").fields) == 1
    assert register_list.get_register("apa").fields[0].name == "enable"
    assert register_list.get_register("apa").fields[0].description == "Enable."
    assert register_list.get_register("apa").fields[0].default_value == "1"

    assert register_list.get_register("hest").index == 3
    assert register_list.get_register("hest").mode == REGISTER_MODES["r"]
    assert register_list.get_register("hest").description == "Hest."
    assert len(register_list.get_register("hest").fields) == 1
    assert register_list.get_register("hest").fields[0].name == "disable"
    assert register_list.get_register("hest").fields[0].description == "Disable."
    assert register_list.get_register("hest").fields[0].default_value == "0"


def test_two_registers_with_same_name_does_not_raise_exception(tmp_path):
    # Limitation in the JSON file format, unlike TOML.
    # We would highly prefer if this raised exception.
    json_path = create_file(
        file=tmp_path / "regs.json",
        contents="""
{
    "apa": {
        "mode": "r"
    },
    "apa": {
        "mode": "r_w"
    }
}
""",
    )

    register_list = from_json(name="", json_file=json_path)
    assert len(register_list.register_objects) == 1
    assert register_list.register_objects[0].mode == REGISTER_MODES["r_w"]
