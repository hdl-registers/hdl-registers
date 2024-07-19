# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register_mode import RegisterMode

# The official register modes in hdl-registers.
# This dictionary maps the official shorthand name of the mode to the object that describes
# the mode.
REGISTER_MODES = dict(
    r=RegisterMode(
        shorthand="r",
        name="Read",
        description="Software can read a value that hardware provides.",
        software_can_read=True,
        software_can_write=False,
        hardware_has_up=True,
    ),
    w=RegisterMode(
        shorthand="w",
        name="Write",
        description="Software can write a value that is available for hardware usage.",
        software_can_read=False,
        software_can_write=True,
        hardware_has_up=False,
    ),
    r_w=RegisterMode(
        shorthand="r_w",
        name="Read, Write",
        description=(
            "Software can write a value and read it back. "
            "The written value is available for hardware usage."
        ),
        software_can_read=True,
        software_can_write=True,
        hardware_has_up=False,
    ),
    wpulse=RegisterMode(
        shorthand="wpulse",
        name="Write-pulse",
        description="Software can write a value that is asserted for one clock cycle in hardware.",
        software_can_read=False,
        software_can_write=True,
        hardware_has_up=False,
    ),
    r_wpulse=RegisterMode(
        shorthand="r_wpulse",
        name="Read, Write-pulse",
        description=(
            "Software can read a value that hardware provides. "
            "Software can write a value that is asserted for one clock cycle in hardware."
        ),
        software_can_read=True,
        software_can_write=True,
        hardware_has_up=True,
    ),
)
