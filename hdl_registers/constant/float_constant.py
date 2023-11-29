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


class FloatConstant(Constant):
    """
    Represent a floating-point constant.

    .. note::

      The ``value`` is stored with its native representation, which is a Python ``float``
      if a decimal value is provided.
      The Python ``float`` type is a double-precision value, so the precision in Python matches
      the precision in C/C++/VHDL generators.
    """

    def __init__(self, name: str, value: float, description: Optional[str] = None):
        """
        Arguments:
            name: The name of the constant.
            value: The constant value.
            description: Textual description for the constant.
        """
        self.name = name
        self.description = "" if description is None else description

        self._value = 0.0
        # Assign self._value via setter
        self.value = value

    @property
    def value(self) -> float:
        """
        Getter for value.
        """
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """
        Setter for value that performs sanity checks.
        """
        if not isinstance(value, float):
            raise ValueError(
                f'Constant "{self.name}" has invalid data type "{type(value)}". Value: "{value}".'
            )

        self._value = value

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
value={self.value},\
description={self.description},\
)"""
