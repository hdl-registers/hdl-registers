# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.register_mode import (
    HardwareAccessDirection,
    RegisterMode,
    SoftwareAccessDirection,
)


def test_repr():
    assert (
        repr(
            RegisterMode(
                shorthand="a",
                name="b",
                description="c",
                software_can_read=False,
                software_can_write=False,
                hardware_has_up=False,
            )
        )
        == "RegisterMode(shorthand=a)"
    )


def test_software_access_direction():
    register_mode = RegisterMode(
        shorthand="a",
        name="b",
        description="c",
        software_can_read=True,
        software_can_write=False,
        hardware_has_up=False,
    )

    assert register_mode.is_software_accessible(SoftwareAccessDirection.READ)
    assert not register_mode.is_software_accessible(SoftwareAccessDirection.WRITE)


def test_hardware_access_direction():
    register_mode = RegisterMode(
        shorthand="a",
        name="b",
        description="c",
        software_can_read=True,
        software_can_write=False,
        hardware_has_up=True,
    )

    assert register_mode.is_hardware_accessible(HardwareAccessDirection.UP)
    assert not register_mode.is_software_accessible(HardwareAccessDirection.DOWN)

    register_mode = RegisterMode(
        shorthand="a",
        name="b",
        description="c",
        software_can_read=True,
        software_can_write=True,
        hardware_has_up=False,
    )

    assert not register_mode.is_hardware_accessible(HardwareAccessDirection.UP)
    assert register_mode.is_software_accessible(HardwareAccessDirection.DOWN)
