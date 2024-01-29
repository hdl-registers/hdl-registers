# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register_field import RegisterField
from .register_field_type import FieldType, Signed, Unsigned


class Integer(RegisterField):  # pylint: disable=too-many-instance-attributes
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

        self._default_value = 0
        # Assign self._default_value via setter
        self.default_value = default_value

        # Determines how bits are to be interpreted in 'set_value' and 'get_value'.
        self._field_type = Signed() if self.is_signed else Unsigned()

    @property
    def field_type(self) -> FieldType:
        """
        Getter for private member.
        """
        return self._field_type

    @property
    def is_signed(self) -> bool:
        """
        Returns True if the field can hold negative numbers.
        """
        return self._min_value < 0

    @property
    def width(self) -> int:
        # Calculate the width based on the supplied numerical limits.
        error_message = (
            f"Supplied integer range [{self._min_value}, {self._max_value}] does not fit "
            "in a register."
        )

        if not self.is_signed:
            # The number of bits needed to represent UNSIGNED numbers [0, max_value].
            num_bits = self._max_value.bit_length()

            if num_bits > 32:
                raise ValueError(error_message)

            return num_bits

        for num_bits in range(1, 33):
            # Two's complement range for signed numbers.
            min_range = -(2 ** (num_bits - 1))
            max_range = 2 ** (num_bits - 1) - 1

            if self._min_value >= min_range and self._max_value <= max_range:
                return num_bits

        raise ValueError(error_message)

    @property
    def base_index(self) -> int:
        return self._base_index

    def _check_range(self, min_value: int, max_value: int) -> None:
        """
        Perform some sanity checks on user-supplied values.
        Will raise exception if something is wrong,.
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

    @property
    def min_value(self) -> int:
        """
        Getter for private member.
        """
        return self._min_value

    @property
    def max_value(self) -> int:
        """
        Getter for private member.
        """
        return self._max_value

    @property  # type: ignore[override]
    def default_value(self) -> int:
        """
        Getter for private member.
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value: int) -> None:
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
    def default_value_str(self) -> str:
        return str(self.default_value)

    @property
    def default_value_uint(self) -> int:
        if self.default_value >= 0:
            return self.default_value

        assert self.is_signed, "Should not end up here unless signed."

        # Offset the sign bit.
        result: int = self.default_value + 2**self.width

        return result

    def get_value(self, register_value: int) -> int:
        """
        See super method for details.
        Adds sanity checks of the value.
        """
        # We know that the return value is an integer and not a float, since this field uses
        # a field_type with no fractional bits.
        result: int = super().get_value(register_value=register_value)  # type: ignore

        if self.min_value <= result <= self.max_value:
            return result

        raise ValueError(
            f'Register field value "{result}" not inside "{self.name}" field\'s '
            f"legal range: ({self.min_value}, {self.max_value})."
        )

    def set_value(self, field_value: int) -> int:  # type: ignore
        """
        See super method for details.
        Adds sanity checks of the value.
        """
        if not self.min_value <= field_value <= self.max_value:
            raise ValueError(
                f'Value "{field_value}" not inside "{self.name}" field\'s '
                f"legal range: ({self.min_value}, {self.max_value})."
            )

        return super().set_value(field_value=field_value)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
_base_index={self._base_index},\
description={self.description},
_min_value={self._min_value},\
_max_value={self._max_value},\
_default_value={self._default_value},\
)"""
