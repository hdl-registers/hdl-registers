# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from abc import ABC, abstractmethod
from typing import Union


class RegisterField(ABC):
    """
    Meta class for all register fields (bits, bit vectors, integers, ...).
    Lists a few methods that must be implemented.
    """

    # Must set as class members in subclasses.
    name: str
    _base_index: int
    _width: int
    description: str
    default_value: Union[str, int]

    @property
    def base_index(self) -> int:
        """
        The index within the register for the lowest bit of this field.
        Note that this (along with :attr:`.width`) decides the base index of upcoming fields, and
        thus it may not be changed.
        Hence this read-only property which is a getter for a private member.
        """
        return self._base_index

    @property
    def width(self) -> int:
        """
        The width, in number of bits, that this field occupies.
        Note that this (along with :attr:`.base_index`) decides the base index of upcoming fields,
        and thus it may not be changed.
        Hence this read-only property which is a getter for a private member.
        """
        return self._width

    @property
    @abstractmethod
    def default_value_uint(self) -> int:
        """
        Return a the default value of this field as an unsigned integer.
        """

    def get_value(self, register_value: int) -> int:
        """
        Get the value of this field, given the supplied register value.

        Arguments:
            register_value: Value of the register that this field belongs to,
                as an unsigned integer.

        Return:
            The value of the field as an unsigned integer.

            Note that a subclass might have a different type for the resulting value.
            Subclasses should call this super method, and then convert the numeric value to whatever
            type is applicable for that field.
            Subclasses might also implement sanity checks of the value given the constraints
            of that field.
        """
        shift_count = self.base_index

        mask_at_base = (1 << self.width) - 1
        mask_shifted = mask_at_base << shift_count

        value = (register_value & mask_shifted) >> shift_count

        return value

    def set_value(self, field_value: int) -> int:
        """
        Convert the supplied value into the bit-shifted unsigned integer ready
        to be written to the register.
        The bits of the other fields in the register are masked out and will be set to zero.

        Arguments:
            field_value: Desired unsigned integer value to set the field to.

                Note that a subclass might have a different type for this argument.
                Subclasses should convert their argument value to an integer and call
                this super method.

        Return:
            The register value as an unsigned integer.
        """
        max_value = 2**self.width - 1
        if not 0 <= field_value <= max_value:
            raise ValueError(f"Value: {field_value} is invalid for unsigned of width {self.width}")

        return field_value << self.base_index

    @abstractmethod
    def __repr__(self) -> str:
        pass
