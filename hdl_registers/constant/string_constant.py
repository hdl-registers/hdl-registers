# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------


from .constant import Constant


class StringConstant(Constant):
    """
    Represent a string constant.
    See :ref:`constant_string` for details.
    """

    def __init__(self, name: str, value: str, description: str = "") -> None:
        """
        Arguments:
            name: The name of the constant.
            value: The constant value.
            description: Textual description for the constant.
        """
        self.name = name
        self.description = description

        self._value = ""
        # Assign self._value via setter
        self.value = value

    @property
    def value(self) -> str:
        """
        Getter for value.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """
        Setter for value that performs sanity checks.
        """
        if not isinstance(value, str):
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
