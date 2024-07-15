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
from hdl_registers.register_modes import REGISTER_MODES


def test_overriding_default_register(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[config]

type = "register"
description = "apa"
""",
    )
    register_list = from_toml(
        name="",
        toml_file=toml_path,
        default_registers=[
            Register(name="config", index=0, mode=REGISTER_MODES["r_w"], description="")
        ],
    )

    assert register_list.get_register("config").description == "apa"


def test_changing_mode_of_default_register_should_raise_exception(tmp_path):
    toml_path = create_file(
        file=tmp_path / "regs.toml",
        contents="""
[config]

mode = "w"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(
            name="",
            toml_file=toml_path,
            default_registers=[
                Register(name="config", index=0, mode=REGISTER_MODES["r_w"], description="")
            ],
        )
    assert str(exception_info.value) == (
        f'Error while parsing register "config" in {toml_path}: '
        'A "mode" may not be specified for a default register.'
    )
