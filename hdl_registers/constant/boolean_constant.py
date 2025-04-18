# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------


from .constant import Constant


class BooleanConstant(Constant):
    """
    Represent a boolean constant.
    See :ref:`constant_boolean` for details.
    """

    def __init__(self, name: str, value: bool, description: str = "") -> None:
        """
        Arguments:
            name: The name of the constant.
            value: The constant value.
            description: Textual description for the constant.
        """
        self.name = name
        self.description = description

        self._value = False
        # Assign self._value via setter
        self.value = value

    @property
    def value(self) -> bool:
        """
        Getter for value.
        """
        return self._value

    @value.setter
    def value(self, value: bool) -> None:
        """
        Setter for value that performs sanity checks.
        """
        if not isinstance(value, bool):
            raise TypeError(
                f'Constant "{self.name}" has invalid data type "{type(value)}". Value: "{value}".'
            )

        self._value = value

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
value={self.value},\
description={self.description},\
)"""
