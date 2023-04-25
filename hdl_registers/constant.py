# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------


class Constant:  # pylint: disable=too-many-instance-attributes
    is_boolean = False
    is_integer = False
    is_float = False
    is_string = False

    def __init__(self, name, value, description=None):
        """
        Arguments:
            name (str): The name of the constant.
            value (bool, int, str): The constant value.
            description (str): Textual description for the constant.
        """
        self.name = name
        self.description = "" if description is None else description

        self._value = None
        # Assign self._value via setter
        self.value = value

    @property
    def value(self):
        """
        Getter for value.
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Setter for value that performs sanity checks.
        """
        self._value = value

        if isinstance(value, int):
            self.is_boolean = isinstance(value, bool)
            self.is_integer = not self.is_boolean

        elif isinstance(value, float):
            self.is_float = True

        elif isinstance(value, str):
            self.is_string = True

        if sum([self.is_boolean, self.is_integer, self.is_float, self.is_string]) != 1:
            raise ValueError(
                f'Constant "{self.name}" has invalid data type "{type(value)}". Value: "{value}"'
            )

    def __repr__(self):
        return f"""{self.__class__.__name__}(\
name={self.name},\
value={self.value},\
description={self.description},
)"""
