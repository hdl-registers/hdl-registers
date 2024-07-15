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

    READ = _SoftwareAccessDirection(name_past="read", name_adjective="readable")
    WRITE = _SoftwareAccessDirection(name_past="written", name_adjective="writeable")


class HardwareAccessDirection(Enum):
    """
    The possible directions hardware can provide/read register values.
    """

    UP = auto()
    DOWN = auto()


class RegisterMode:
    def __init__(
        self,
        shorthand: str,
        name: str,
        description: str,
        is_software_readable: bool,
        is_software_writeable: bool,
        has_hardware_up: bool,
    ):  # pylint: disable=too-many-arguments
        """
        Arguments:
            shorthand: A short string that can be used to refer to this mode.
                E.g. "r".
            name: A short but human-readable readable representation of this mode.
                E.g. "Read".
            description: Textual description of mode.
            is_software_readable: True if registers of this mode are readable by software over the
                register bus.
                I.e. if software accessors shall have a 'read' method for registers of this mode.
                False otherwise.

                Analogous the ``reg_file.reg_file_pkg.is_read_type`` VHDL function.
            is_software_writeable: True if registers of this mode are writeable by software over the
                register bus.
                I.e. if software accessors shall have a 'write' method for registers of this mode.
                False otherwise.

                Analogous the ``reg_file.reg_file_pkg.is_write_type`` VHDL function.
            has_hardware_up: True if registers of this mode get their software read value
                from hardware.
                I.e. if hardware register files shall have a 'up' input port for registers of
                this mode.

                False otherwise, which can be due to either

                * mode is not software-readable, or
                * mode loopbacks a software-written value to the software read value.
        """
        assert is_software_readable or not has_hardware_up, (
            f'Register mode "{shorthand}"" has hardware "up", but is not software readable. '
            "This does not make sense."
        )

        self.shorthand = shorthand
        self.name = name
        self.description = description
        self.is_software_readable = is_software_readable
        self.is_software_writeable = is_software_writeable
        self.has_hardware_up = has_hardware_up

    @property
    def has_hardware_down(self) -> bool:
        """
        True if registers of this mode provide a value from software to hardware.
        I.e. if hardware register files shall have a 'down' output port for registers of
        this mode.

        False otherwise, which is most likely due to the register being read-only.
        """
        # At the moment this is the same being software-writeable.
        # Might change in the future if we implement some exotic mode.
        return self.is_software_writeable

    def is_software_accessible(self, direction: SoftwareAccessDirection) -> bool:
        """
        Test if this mode is software-accessible in the given ``direction``.
        """
        if direction == SoftwareAccessDirection.READ:
            return self.is_software_readable

        return self.is_software_writeable

    def is_hardware_accessible(self, direction: HardwareAccessDirection) -> bool:
        """
        Test if this mode is hardware-accessible in the given ``direction``.
        """
        if direction == HardwareAccessDirection.UP:
            return self.has_hardware_up

        return self.has_hardware_down

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

        return self.shorthand == other.shorthand
