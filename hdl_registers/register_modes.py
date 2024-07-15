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
        is_software_readable=True,
        is_software_writeable=False,
        has_hardware_up=True,
    ),
    w=RegisterMode(
        shorthand="w",
        name="Write",
        description="Software can write a value that is available for hardware usage.",
        is_software_readable=False,
        is_software_writeable=True,
        has_hardware_up=False,
    ),
    r_w=RegisterMode(
        shorthand="r_w",
        name="Read, Write",
        description=(
            "Software can write a value and read it back. "
            "The written value is available for hardware usage."
        ),
        is_software_readable=True,
        is_software_writeable=True,
        has_hardware_up=False,
    ),
    wpulse=RegisterMode(
        shorthand="wpulse",
        name="Write-pulse",
        description="Software can write a value that is asserted for one clock cycle in hardware.",
        is_software_readable=False,
        is_software_writeable=True,
        has_hardware_up=False,
    ),
    r_wpulse=RegisterMode(
        shorthand="r_wpulse",
        name="Read, Write-pulse",
        description=(
            "Software can read a value that hardware provides. "
            "Software can write a value that is asserted for one clock cycle in hardware."
        ),
        is_software_readable=True,
        is_software_writeable=True,
        has_hardware_up=True,
    ),
)
