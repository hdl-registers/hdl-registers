# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import Optional, Union

# Local folder libraries
from .numerical_interpretation import NumericalInterpretation, Unsigned
from .register_field import RegisterField


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
        numerical_interpretation: Optional[NumericalInterpretation] = None,
    ):  # pylint: disable=too-many-arguments
        """
        Arguments:
            name: The name of the bit vector.
            base_index: The zero-based index within the register for the lowest bit of this
                bit vector.
            description: Textual field description.
            width: The width of the bit vector field.
            default_value: Default value as a string.
                Must be of length ``width`` and contain only "1" and "0".
            numerical_interpretation: The mode used when interpreting the bits of this field as
                a numeric value.
                Default is unsigned with no fractional bits.
        """
        self.name = name
        self._base_index = base_index
        self.description = description

        self._numerical_interpretation = (
            Unsigned(bit_width=width)
            if numerical_interpretation is None
            else numerical_interpretation
        )

        self._check_width(width=width)
        self._width = width

        self._default_value = ""
        # Assign self._default_value via setter
        self.default_value = default_value

    @property
    def numerical_interpretation(self) -> NumericalInterpretation:
        """
        The mode used when interpreting the bits of this field as a numeric value
        (E.g. signed, unsigned fixed-point, etc.).
        Is used by :meth:`get_value` and :meth:`set_value`.

        Getter for private member.
        """
        return self._numerical_interpretation

    def _check_width(self, width: int) -> None:
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

        if width != self.numerical_interpretation.bit_width:
            raise ValueError(
                f'Inconsistent width for bit vector "{self.name}". '
                f'Field is "{width}" bits, numerical interpretation specification is '
                f'"{self.numerical_interpretation.bit_width}".'
            )

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

    def get_value(self, register_value: int) -> Union[int, float]:  # type: ignore[override]
        """
        See super method for details.
        This subclass method uses the native numeric representation of the field value
        (not the raw value of the bits).
        If the field has a non-zero number of fractional bits, the type of the result
        will be a ``float``.
        Otherwise it will be an ``int``.
        """
        value_unsigned = super().get_value(register_value=register_value)
        return self.numerical_interpretation.convert_from_unsigned_binary(
            unsigned_binary=value_unsigned
        )

    def set_value(self, field_value: Union[int, float]) -> int:
        """
        See super method for details.
        This subclass method uses the native numeric representation of the field value
        (not the raw value of the bits).
        If the field has a non-zero number of fractional bits, the type of the argument
        should be a ``float``.
        Otherwise it should be an ``int``.
        """
        unsigned_value = self.numerical_interpretation.convert_to_unsigned_binary(value=field_value)
        return super().set_value(field_value=unsigned_value)

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
_numerical_interpretation={self._numerical_interpretation},\
)"""
