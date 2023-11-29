# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import Optional

# Local folder libraries
from .constant import Constant


class BitVectorConstant(Constant):
    separator_character = "_"
    allowed_binary_characters = "01" + separator_character
    allowed_hexadecimal_characters = "0123456789abcdefABCDEF" + separator_character

    def __init__(self, name: str, value: str, description: Optional[str] = None):
        """
        Arguments:
            name: The name of the constant.
            value: The constant value. Must start with "0b" or "0x". Must only contain legal binary
                or hexadecimal characters. Underscore may be used as a separator.
            description: Textual description for the constant.
        """
        self.name = name
        self.description = "" if description is None else description

        # Assigned in 'value' setter.
        self._is_hexadecimal_not_binary = False
        self._prefix = ""

        self._value = ""
        # Assign self._value via setter
        self.value = value

    @property
    def prefix(self) -> str:
        """
        Getter for ``prefix``.
        """
        return self._prefix

    @property
    def value(self) -> str:
        """
        Getter for ``value``.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """
        Setter for ``value`` that performs sanity checks.
        """
        if not isinstance(value, str):
            raise TypeError(
                f'Constant "{self.name}" has invalid data type "{type(value)}". Value: "{value}".'
            )

        self._prefix = value[0:2]

        if len(value) < 3 or self._prefix not in ["0b", "0x"]:
            raise ValueError(
                f'Constant "{self.name}" value must start with a correct prefix. '
                f'Value: "{value}".'
            )

        self._is_hexadecimal_not_binary = self._prefix == "0x"

        # Assign only the numeric characters
        self._value = value[2:]

        allowed_characters = (
            self.allowed_hexadecimal_characters
            if self._is_hexadecimal_not_binary
            else self.allowed_binary_characters
        )
        for character in self._value:
            if character not in allowed_characters:
                raise ValueError(
                    f'Constant "{self.name}" contains illegal character "{character}". '
                    f'Value: "{value}".'
                )

    @property
    def value_without_separator(self) -> str:
        """
        Getter for ``value``, without any separator characters.
        """
        return self._value.replace(self.separator_character, "")

    @property
    def is_hexadecimal_not_binary(self) -> bool:
        """
        Getter for ``is_hexadecimal_not_binary``.
        """
        return self._is_hexadecimal_not_binary

    @property
    def width(self) -> int:
        """
        The number of bits this vector constant occupies.
        """
        bits_per_character = 4 if self._is_hexadecimal_not_binary else 1

        return len(self.value_without_separator) * bits_per_character

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
prefix={self.prefix},\
value={self.value},\
description={self.description},\
)"""


class UnsignedVector(str):
    """
    Represent a value that is of type unsigned vector
    (as opposed to a **register constant** of the same type, which would use the
    :class:`.UnsignedVectorConstant` class).
    """


class UnsignedVectorConstant(BitVectorConstant):
    """
    Represent a register constant that is of type unsigned vector
    (as opposed to a **plain value** of the same type in Python, which would use the
    :class:`.UnsignedVector` class).
    """
