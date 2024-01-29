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

# Local folder libraries
from .register_field_type import FieldType, Unsigned

DEFAULT_FIELD_TYPE = Unsigned()


class RegisterField(ABC):
    """
    Meta class for all register fields (bits, bit vectors, integers, ...).
    Lists a few methods that must be implemented.
    """

    # Must set these two as class members in subclasses.
    name: str
    description: str
    default_value: Union[str, int]

    @property
    def max_binary_value(self) -> int:
        """
        Get the maximum value, represented as a positive integer, that this
        field can hold given its width.
        """
        result: int = 2**self.width - 1
        return result

    @property
    def range_str(self) -> str:
        """
        Return the bits that this field occupies in a readable format.
        The way it shall appear in documentation.
        """
        if self.width == 1:
            return f"{self.base_index}"

        return f"{self.base_index + self.width - 1}:{self.base_index}"

    @property
    def field_type(self) -> FieldType:
        """
        The field type (Unsigned, Signed, UnsignedFixedPoint, SignedFixedPoint, ...)
        used to interpret the bits of the field.
        """
        # Default for all RegisterFields
        return DEFAULT_FIELD_TYPE

    @property
    @abstractmethod
    def width(self) -> int:
        """
        Return the width, in number of bits, that this field occupies.
        """

    @property
    @abstractmethod
    def base_index(self) -> int:
        """
        The index within the register for the lowest bit of this field.
        """

    @property
    @abstractmethod
    def default_value_str(self) -> str:
        """
        Return a formatted string of the default value. The way it shall appear
        in documentation.
        """

    @property
    @abstractmethod
    def default_value_uint(self) -> int:
        """
        Return a the default value as an unsigned int.
        """

    def get_value(self, register_value: int) -> Union[int, float]:
        """
        Get the value of this field, given the supplied register value.
        Subclasses might implement sanity checks on the value.

        Arguments:
            register_value: Value of the register that this field belongs to.

        Return:
            The value of the field.
            If the field has a non-zero number of fractional bits, the type of the result
            will be a ``float``.
            Otherwise it will be an ``int``.

            Note that a subclass might have a different type for the resulting value.
            Subclasses should call this super method and convert the numeric value to whatever
            type is applicable for that field.
        """
        shift = self.base_index

        mask_at_base = (1 << self.width) - 1
        mask = mask_at_base << shift

        value_unsigned = (register_value & mask) >> shift
        field_value = self.field_type.convert_from_unsigned_binary(self.width, value_unsigned)

        return field_value

    def set_value(self, field_value: Union[int, float]) -> int:
        """
        Convert the supplied value into the bit-shifted unsigned integer ready
        to be written to the register. The bits of the other fields in the
        register are masked out and will be set to zero.

        Arguments:
            field_value: Desired value to set the field to.
                If the field has a non-zero number of fractional bits, the type of the value is
                expected to be a ``float``.
                Otherwise it should be an ``int``.

                Note that a subclass might have a different type for this argument.
                Subclasses should convert their argument value to an integer/float and call
                this super method.

        Return:
            The register value as an unsigned integer.
        """
        value_unsigned = self.field_type.convert_to_unsigned_binary(self.width, field_value)
        max_value = self.max_binary_value
        if not 0 <= value_unsigned <= max_value:
            raise ValueError(
                f"Value: {value_unsigned} is invalid for unsigned of width {self.width}"
            )

        mask = max_value << self.base_index
        value_shifted = value_unsigned << self.base_index

        return value_shifted & mask

    @abstractmethod
    def __repr__(self) -> str:
        pass
