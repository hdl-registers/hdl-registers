# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

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


def test_repr_str_eq_hash():
    def get_mode(shorthand: str) -> RegisterMode:
        return RegisterMode(
            shorthand=shorthand,
            name="b",
            description="c",
            software_can_read=True,
            software_can_write=False,
            hardware_has_up=False,
        )

    register_mode_a = get_mode("a")
    register_mode_b = get_mode("a")
    register_mode_c = get_mode("c")

    assert repr(register_mode_a) == "RegisterMode(shorthand=a)"
    assert repr(register_mode_a) == repr(register_mode_b)
    assert repr(register_mode_a) != repr(register_mode_c)

    assert str(register_mode_a) == repr(register_mode_a)

    assert register_mode_a == register_mode_b
    assert register_mode_a != register_mode_c

    assert hash(register_mode_a) == hash(register_mode_b)
    assert hash(register_mode_a) != hash(register_mode_c)
