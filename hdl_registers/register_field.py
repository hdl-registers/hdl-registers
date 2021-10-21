# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod


class RegisterField(ABC):

    """
    Meta class for all register fields (bits, bit vectors, integers, ...).
    Lists a few methods that must be implemented.
    """

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
