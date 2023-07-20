# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import math

# Local folder libraries
from .register_field import RegisterField


class Integer(RegisterField):

    """
    Used to represent an integer field in a register.
    """

    def __init__(
        self,
        name: str,
        base_index: int,
        description: str,
        min_value: int,
        max_value: int,
        default_value: int,
    ):  # pylint: disable=too-many-arguments
        """
        Arguments:
            name: The name of the field.
            base_index: The zero-based index within the register for the lowest bit of this field.
            description: Textual field description.
            min_value: The minimum value that this field shall be able to represent.
            min_value: The maximum value that this field shall be able to represent.
            default_value: Default value. Must be within the specified range.
        """
        self.name = name
        self._base_index = base_index
        self.description = description

        # These affect the width of the field, and hence the base index of the next fields.
        # Hence the user is not allowed to change them, nor the base index of this field,
        # after initialization.
        self._check_range(min_value=min_value, max_value=max_value)
        self._min_value = min_value
        self._max_value = max_value

        self._default_value = None
        # Assign self._default_value via setter
        self.default_value = default_value

    @property
    def width(self):
        # Calculate the width based on the supplied numerical limits.
        # The number of bits needed to represent unsigned numbers [0, max_value].
        return int(math.ceil(math.log2(self.max_value + 1)))

    @property
    def base_index(self):
        return self._base_index

    def _check_range(self, min_value, max_value):
        """
        Perform some sanity checks on user_supplied values.
        """
        if not isinstance(min_value, int):
            message = (
                f'Integer field "{self.name}" should have integer value for "min_value". '
                f'Got: "{min_value}".'
            )
            raise ValueError(message)

        if not isinstance(max_value, int):
            message = (
                f'Integer field "{self.name}" should have integer value for "max_value". '
                f'Got: "{max_value}".'
            )
            raise ValueError(message)

        if min_value > max_value:
            message = (
                f'Integer field "{self.name}" should have ascending range. '
                f"Got: [{min_value}, {max_value}]."
            )
            raise ValueError(message)

        if min_value < 0:
            message = (
                f'Integer field "{self.name}" should have a non-negative range. '
                f"Got: [{min_value}, {max_value}]."
            )
            raise ValueError(message)

    @property
    def min_value(self):
        """
        Getter for private member.
        """
        return self._min_value

    @property
    def max_value(self):
        """
        Getter for private member.
        """
        return self._max_value

    @property
    def default_value(self):
        """
        Getter for private member.
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value: int):
        """
        Setter for default_value that performs sanity checks.
        """
        if not isinstance(value, int):
            message = (
                f'Integer field "{self.name}" should have integer value for "default_value". '
                f'Got: "{value}".'
            )
            raise ValueError(message)

        if value < self.min_value or value > self.max_value:
            message = (
                f'Integer field "{self.name}" should have "default_value" within range '
                f'[{self.min_value}, {self.max_value}]. Got: "{value}".'
            )
            raise ValueError(message)

        self._default_value = value

    @property
    def default_value_str(self):
        return str(self.default_value)

    @property
    def default_value_uint(self):
        return self.default_value

    def __repr__(self):
        return f"""{self.__class__.__name__}(\
name={self.name},\
base_index={self.base_index},\
description={self.description},
min_value={self.min_value},\
max_value={self.max_value},\
default_value={self.default_value},\
)"""
