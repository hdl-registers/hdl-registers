# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register_field import DEFAULT_FIELD_TYPE, RegisterField
from .register_field_type import FieldType, Fixed


class BitVector(RegisterField):
    """
    Used to represent a bit vector field in a register.
    """

    def __init__(
        self,
        name: str,
        base_index: int,
        description: str,
        width: int,
        default_value: str,
        field_type: FieldType = DEFAULT_FIELD_TYPE,
    ):  # pylint: disable=too-many-arguments
        """
        Arguments:
            name: The name of the bit vector.
            base_index: The zero-based index within the register for the lowest bit of this
                bit vector.
            description: Textual bit vector description.
            width: The width of the bit vector field.
            default_value: Default value as a string. Must be of length ``width`` and contain
                only "1" and "0".
            field_type: The field type used to interpret the bits of the field.
        """
        self.name = name
        self._base_index = base_index
        self.description = description

        # The width of the field affects the base index of the next fields.
        # Hence the user is not allowed to change it, nor the base index of this field,
        # after initialization.
        self._check_width(width=width, field_type=field_type)
        self._width = width

        self._default_value = ""
        # Assign self._default_value via setter
        self.default_value = default_value

        self._field_type = field_type

    @property
    def field_type(self) -> FieldType:
        return self._field_type

    @property
    def width(self) -> int:
        return self._width

    def _check_width(self, width: int, field_type: FieldType) -> None:
        """
        Sanity checks for the provided width
        Will raise exception if something is wrong.
        """
        if not isinstance(width, int):
            message = (
                f'Bit vector "{self.name}" should have integer value for "width". Got: "{width}".'
            )
            raise ValueError(message)

        if width < 1 or width > 32:
            raise ValueError(f'Invalid width for bit vector "{self.name}". Got: "{width}".')

        # A fixed-point field type specifies its integer width and fractional width,
        # which together form a total width.
        # Check that this does not clash with the width specified for the field.
        if isinstance(field_type, Fixed):
            if width != field_type.expected_bit_width:
                raise ValueError(
                    f'Inconsistent width for bit vector "{self.name}". '
                    f'Field is "{width}" bits, type is "{field_type.expected_bit_width}".'
                )

    @property
    def base_index(self) -> int:
        return self._base_index

    @property  # type: ignore[override]
    def default_value(self) -> str:
        """
        Getter for private member.
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value: str) -> None:
        """
        Setter for ``default_value`` that performs sanity checks.
        """
        if not isinstance(value, str):
            message = (
                f'Bit vector "{self.name}" should have string value for "default_value". '
                f'Got: "{value}"'
            )
            raise ValueError(message)

        if len(value) != self.width:
            message = (
                f'Bit vector "{self.name}" should have "default_value" of length {self.width}. '
                f'Got: "{value}".'
            )
            raise ValueError(message)

        for character in value:
            if character not in ["0", "1"]:
                message = (
                    f'Bit vector "{self.name}" invalid binary value for "default_value". '
                    f'Got: "{value}".'
                )
                raise ValueError(message)

        self._default_value = value

    @property
    def default_value_str(self) -> str:
        return f"0b{self.default_value}"

    @property
    def default_value_uint(self) -> int:
        return int(self.default_value, base=2)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
_base_index={self._base_index},\
description={self.description},
_width={self._width},\
_default_value={self._default_value},\
_field_type={self._field_type},\
)"""
