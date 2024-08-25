# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


@dataclass
class _SoftwareAccessDirection:
    name_past: str
    name_adjective: str


class SoftwareAccessDirection(Enum):
    """
    The possible directions software can access registers.
    """

    # The type of the enum values might change in the future.
    # Should not make a difference for any user since the values are unique either way.
    READ = _SoftwareAccessDirection(name_past="read", name_adjective="readable")
    WRITE = _SoftwareAccessDirection(name_past="written", name_adjective="writeable")


class HardwareAccessDirection(Enum):
    """
    The possible directions hardware can provide/read register values.
    """

    # The type of the enum values might change in the future.
    # Should not make a difference for any user since the values are unique either way.
    UP = auto()
    DOWN = auto()


class RegisterMode:
    """
    Represents a mode of a register, which defines how the register can be accessed.
    The terms "software"/"hardware", along with "register bus", "register file", "read", "write",
    "up" and "down" are used in this class.
    These terms are explained by the following diagram:

    .. code-block:: none

       ______________________
      |      "Software"      |
      | E.g. CPU, PCIe, etc. |
      |______________________|
                 ||
                 ||         "Register bus"
                 ||         E.g. AXI-Lite.
                 || "read" or "write" transactions.
                 ||
       _______________________      "down"      ______________________________
      |    "Register file"    |--------------->|          "Hardware"          |
      | E.g. generic AXI-Lite |                |  Meaning, your application.  |
      |     register file.    |      "up"      | In e.g. FPGA fabric or ASIC. |
      |_______________________|<---------------|______________________________|
    """

    def __init__(
        self,
        shorthand: str,
        name: str,
        description: str,
        software_can_read: bool,
        software_can_write: bool,
        hardware_has_up: bool,
    ):  # pylint: disable=too-many-arguments
        """
        Arguments:
            shorthand: A short string that can be used to refer to this mode.
                E.g. "r".
            name: A short but human-readable readable representation of this mode.
                E.g. "Read".
            description: Textual description and explanation of this mode.
            software_can_read: True if register is readable by software on the register bus.
                I.e. if software accessors shall have a 'read' method for registers of this mode.
                False otherwise.

                Analogous the ``reg_file.reg_file_pkg.is_read_type`` VHDL function.
            software_can_write: True if register is writeable by software on the register bus.
                I.e. if software accessors shall have a 'write' method for registers of this mode.
                False otherwise.

                Analogous the ``reg_file.reg_file_pkg.is_write_type`` VHDL function.
            hardware_has_up: True if register gets its software-read value from hardware.
                I.e. if register file shall have an 'up' input port for registers of this mode.

                False otherwise, which can be due to either

                * mode is not software-readable, or
                * mode loopbacks a software-written value to the software read value.
        """
        assert software_can_read or not hardware_has_up, (
            f'Register mode "{shorthand}"" has hardware "up", but is not software readable. '
            "This does not make sense."
        )

        self.shorthand = shorthand
        self.name = name
        self.description = description
        self.software_can_read = software_can_read
        self.software_can_write = software_can_write
        self.hardware_has_up = hardware_has_up

    @property
    def hardware_has_down(self) -> bool:
        """
        True if register provides a value from software to hardware.
        I.e. if register file shall have a 'down' output port for registers of this mode.

        False otherwise, which is most likely due to the register being read-only.
        """
        # At the moment this is the same being software-writeable.
        # Might change in the future if we implement some exotic cool mode.
        return self.software_can_write

    def is_software_accessible(self, direction: SoftwareAccessDirection) -> bool:
        """
        Test if this mode is software-accessible in the given ``direction``.
        Method is just a simple wrapper around the already-existing attributes.
        """
        if direction == SoftwareAccessDirection.READ:
            return self.software_can_read

        return self.software_can_write

    def is_hardware_accessible(self, direction: HardwareAccessDirection) -> bool:
        """
        Test if this mode is hardware-accessible in the given ``direction``.
        Method is just a simple wrapper around the already-existing attributes.
        """
        if direction == HardwareAccessDirection.UP:
            return self.hardware_has_up

        return self.hardware_has_down

    def __repr__(self) -> str:
        """
        There should never be different modes with the same shorthand.
        Hence, in order to make a unique representation, it is enough to use the shorthand.
        None of the other attributes are needed.
        """
        return f"{self.__class__.__name__}(shorthand={self.shorthand})"

    def __str__(self) -> str:
        return repr(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        # Same logic as in __repr__.
        return self.shorthand == other.shorthand
