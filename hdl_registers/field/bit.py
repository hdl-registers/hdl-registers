# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register_field import RegisterField


class Bit(RegisterField):
    """
    Used to represent a bit field in a register.
    """

    width = 1

    def __init__(self, name: str, index: int, description: str, default_value: str):
        """
        Arguments:
            name: The name of the bit.
            index: The zero-based index of this bit within the register.
            description: Textual bit description.
            default_value: Default value. Either "1" or "0".
        """
        self.name = name
        self._base_index = index
        self.description = description

        self._default_value = ""
        # Assign self._default_value via setter
        self.default_value = default_value

    @property
    def base_index(self) -> int:
        return self._base_index

    @property  # type: ignore[override]
    def default_value(self) -> str:
        """
        Getter for private member.
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value: str) -> None:
        """
        Setter for ``default_value`` that performs sanity checks.
        """
        if not isinstance(value, str):
            message = (
                f'Bit "{self.name}" should have string value for "default_value". Got "{value}".'
            )
            raise ValueError(message)

        if value not in ["0", "1"]:
            message = f'Bit "{self.name}" invalid binary value for "default_value". Got: "{value}".'
            raise ValueError(message)

        self._default_value = value

    @property
    def default_value_str(self) -> str:
        return f"0b{self.default_value}"

    @property
    def default_value_uint(self) -> int:
        return int(self.default_value, base=2)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
base_index={self.base_index},\
description={self.description},\
default_value={self.default_value},\
)"""
