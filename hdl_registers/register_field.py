# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod


class RegisterField(ABC):

    """
    Meta class for all register fields (bits, bit vectors, integers, ...).
    Lists a few methods that must be implemented.
    """

    @property
    def max_binary_value(self) -> int:
        """
        Get the maximum value, represented as a positive integer, that this field can hold given
        its width.

        Returns:
            int: The maximum value.
        """
        return 2 ** self.width - 1

    @property
    @abstractmethod
    def width(self):
        """
        Return the width, in number of bits, that this field occupies.

        Returns:
            int: The width.
        """
        raise NotImplementedError("Must be implemented in child class")

    @property
    @abstractmethod
    def base_index(self):
        """
        The index within the register for the lowest bit of this Field.

        Returns:
            int: The index.
        """
        raise NotImplementedError("Must be implemented in child class")

    @property
    @abstractmethod
    def range(self):
        """
        Return the bits that this field occupies in a readable format.
        The way it shall appear in documentation.

        Returns:
            str: The bit range.
        """
        raise NotImplementedError("Must be implemented in child class")

    @property
    @abstractmethod
    def default_value_str(self):
        """
        Return a formatted string of the default value. The way it shall appear in documentation.

        Returns:
            str: The default value.
        """
        raise NotImplementedError("Must be implemented in child class")

    @property
    @abstractmethod
    def default_value_uint(self):
        """
        Return a the default value as an unsigned int.

        Returns:
            int: The default value.
        """
        raise NotImplementedError("Must be implemented in child class")

    @abstractmethod
    def get_value(self, register_value):
        """
        Get the value of this field, given the supplied register value.
        Child classes might implement sanity checks on the value.

        Arguments:
            register_value (int): Value of the register that this field belongs to.

        Returns:
            int: The value.
        """
        raise NotImplementedError("Must be implemented in child class")

    def set_value(self, field_value: int) -> int:
        """
        Convert the supplied value into the bit-shifted unsigned integer ready
        to be written to the register. The bits of the other fields in the
        register are masked out and will be set to zero.

        Arguments:
            field_value (int) : Desired value to set the field to.

        Returns:
            int: the register value
        """
        max_ = self.max_binary_value
        if not 0 <= field_value <= max_:
            raise ValueError(f"Value: {field_value} is invalid for unsigned of width {max_}")
        mask = max_ << self.base_index
        value_shifted = field_value << self.base_index
        return value_shifted & mask
