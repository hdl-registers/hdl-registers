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
from typing import Optional, Union


def from_unsigned_binary(
    num_bits: int,
    value: int,
    num_integer_bits: Optional[int] = None,
    num_fractional_bits: int = 0,
    is_signed: bool = False,
) -> Union[int, float]:
    """
    Convert from a fixed-point unsigned binary value to one of

    * unsigned integer (Python ``int``)
    * signed integer (Python ``int``)
    * unsigned floating-point (Python ``float``)
    * signed floating-point (Python ``float``)

    Signed types use two's complement representation for the binary value.
    Sources:

    * https://en.wikibooks.org/wiki/Floating_Point/Fixed-Point_Numbers
    * https://vhdlguru.blogspot.com/2010/03/fixed-point-operations-in-vhdl-tutorial.html

    Arguments:
        num_bits: Width of the field.
        value: Unsigned binary integer representation of the value.
        num_integer_bits: The number of integer bits in the fixed-point ``value``.
            Might be negative if this is a fixed-point word with only fractional bits.
        num_fractional_bits: The number of fractional bits in the fixed-point ``value``.
            Might be negative if this is a fixed-point word with only integer bits.
        is_signed: If ``True``, the MSB of the ``value`` will be treated as a sign bit.
            Enables the handling of negative result values.

    Return:
        Native Python representation of the ``value``.
        Will be a ``float`` if ``num_fractional_bits`` is non-zero, otherwise it will be an ``int``.
    """
    num_integer_bits = num_bits if num_integer_bits is None else num_integer_bits

    if num_integer_bits + num_fractional_bits != num_bits:
        raise ValueError("Inconsistent bit width")

    result: Union[int, float] = value * 2**-num_fractional_bits

    if is_signed:
        sign_bit = value & (1 << (num_bits - 1))
        if sign_bit != 0:
            # If sign bit is set, compute negative value.
            result -= 2**num_integer_bits

    return result


def to_unsigned_binary(
    num_bits: int,
    value: Union[int, float],
    num_integer_bits: Optional[int] = None,
    num_fractional_bits: int = 0,
    is_signed: bool = False,
) -> int:
    """
    Convert from one of

    * unsigned integer (Python ``int``)
    * signed integer (Python ``int``)
    * unsigned floating-point (Python ``float``)
    * signed floating-point (Python ``float``)

    into an unsigned binary.
    Signed types use two's complement representation for the binary value.
    Sources:

    * https://en.wikibooks.org/wiki/Floating_Point/Fixed-Point_Numbers
    * https://vhdlguru.blogspot.com/2010/03/fixed-point-operations-in-vhdl-tutorial.html

    Arguments:
        num_bits: Width of the field.
        value: Native numeric Python representation of the value.
            If ``num_fractional_bits`` is non-zero the value is expected to be a ``float``,
            otherwise an ``int`` is expected.
        num_integer_bits: The number of integer bits in the target fixed-point word.
            Might be negative if this is a fixed-point word with only fractional bits.
        num_fractional_bits: The number of fractional bits in the target fixed-point word.
            Might be negative if this is a fixed-point word with only integer bits.
        is_signed: Enables the handling of negative input ``value``.
            If ``True``, the MSB of the result word will be treated as a sign bit.

    Return:
        Unsigned binary integer representation of the value.
        Potentially rounded, if the input ``value`` is a floating-point number.
    """
    num_integer_bits = num_bits if num_integer_bits is None else num_integer_bits

    if num_integer_bits + num_fractional_bits != num_bits:
        raise ValueError("Inconsistent bit width")

    binary_value: int = round(value * 2**num_fractional_bits)
    if value < 0:
        if is_signed:
            binary_value += 1 << num_bits
        else:
            raise ValueError("Attempting to convert negative value to unsigned")

    return binary_value


class NumericalInterpretation(ABC):
    """
    This class represents different modes used when interpreting a field of bits as a numeric value.
    Contains metadata, helper methods, etc.
    """

    # Width of the field in number of bits.
    bit_width: int

    @property
    @abstractmethod
    def is_signed(self) -> bool:
        """
        Is the field signed (two's complement)?
        """

    @property
    @abstractmethod
    def min_value(self) -> Union[int, float]:
        """
        Minimum representable value for this field, in its native numeric representation.

        Return type is the native Python representation of the value, which depends on the subclass.
        If the subclass has a non-zero number of fractional bits, the value will be a ``float``.
        If not, it will be an ``int``.
        """

    @property
    @abstractmethod
    def max_value(self) -> Union[int, float]:
        """
        Maximum representable value for this field, in its native numeric representation.

        Return type is the native Python representation of the value, which depends on the subclass.
        If the subclass has a non-zero number of fractional bits, the value will be a ``float``.
        If not, it will be an ``int``.
        """

    @abstractmethod
    def convert_from_unsigned_binary(self, unsigned_binary: int) -> Union[int, float]:
        """
        Convert from the unsigned binary integer representation of a field,
        into the native value of the field.

        Arguments:
            unsigned_binary: Unsigned binary integer representation of the field.
        """

    @abstractmethod
    def convert_to_unsigned_binary(self, value: Union[int, float]) -> int:
        """
        Convert from the native value of the field, into the
        unsigned binary integer representation which can be written to a register.

        Arguments:
            value: Native Python representation of the field value.

        Return:
            Unsigned binary integer representation of the field.
        """

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def _check_native_value_in_range(self, value: Union[int, float]) -> None:
        """
        Raise an exception if the given field value is not within the allowed range.
        Note that this is the native field value, not the raw binary value.

        Arguments:
            value: Native Python representation of the field value.
        """
        min_ = self.min_value
        max_ = self.max_value
        if not min_ <= value <= max_:
            raise ValueError(
                f"Value: {value} out of range of {self.bit_width}-bit ({min_}, {max_})."
            )

    def _check_unsigned_binary_value_in_range(self, value: Union[int, float]) -> None:
        """
        Raise an exception if the given unsigned binary value does not fit in the field.

        Arguments:
            value: Unsigned binary representation of the field value.
        """
        max_ = 2**self.bit_width - 1
        if not 0 <= value <= max_:
            raise ValueError(f"Value: {value} out of range of {self.bit_width}-bit (0, {max_}).")


class Unsigned(NumericalInterpretation):
    """
    Unsigned integer.
    """

    is_signed: bool = False

    def __init__(self, bit_width: int):
        self.bit_width = bit_width

    @property
    def min_value(self) -> int:
        return 0

    @property
    def max_value(self) -> int:
        result: int = 2**self.bit_width - 1
        return result

    def convert_from_unsigned_binary(self, unsigned_binary: int) -> int:
        self._check_unsigned_binary_value_in_range(unsigned_binary)
        return unsigned_binary

    def convert_to_unsigned_binary(self, value: float) -> int:
        self._check_native_value_in_range(value)
        return round(value)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
bit_width={self.bit_width},\
)"""


class Signed(NumericalInterpretation):
    """
    Two's complement signed integer format.
    """

    is_signed: bool = True

    def __init__(self, bit_width: int):
        self.bit_width = bit_width

    @property
    def min_value(self) -> int:
        result: int = -(2 ** (self.bit_width - 1))
        return result

    @property
    def max_value(self) -> int:
        result: int = 2 ** (self.bit_width - 1) - 1
        return result

    def convert_from_unsigned_binary(self, unsigned_binary: int) -> int:
        self._check_unsigned_binary_value_in_range(unsigned_binary)
        return int(
            from_unsigned_binary(
                num_bits=self.bit_width, value=unsigned_binary, is_signed=self.is_signed
            )
        )

    def convert_to_unsigned_binary(self, value: float) -> int:
        self._check_native_value_in_range(value)
        return to_unsigned_binary(num_bits=self.bit_width, value=value, is_signed=self.is_signed)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
bit_width={self.bit_width},\
)"""


class Fixed(NumericalInterpretation, ABC):
    def __init__(self, is_signed: bool, max_bit_index: int, min_bit_index: int):
        """
        Abstract baseclass for fixed-point fields.

        The bit_index arguments indicates the position of the decimal point in
        relation to the number expressed by the field. The decimal point is
        between the "0" and "-1" bit index. If the bit_index argument is
        negative, then the number represented by the field will include a
        fractional portion.

        Arguments:
            is_signed: Is the field signed (two's complement)?
            max_bit_index: Position of the upper bit relative to the decimal point.
            min_bit_index: Position of the lower bit relative to the decimal point.
        """
        if max_bit_index < min_bit_index:
            raise ValueError("max_bit_index must be >= min_bit_index")

        self.max_bit_index = max_bit_index
        self.min_bit_index = min_bit_index

        self.integer_bit_width = self.max_bit_index + 1
        self.fraction_bit_width = -self.min_bit_index
        # The total width.
        # Note that this the same property name as the 'Unsigned' and 'Signed' classes.
        self.bit_width = self.integer_bit_width + self.fraction_bit_width

        self._is_signed = is_signed
        self._integer = (
            Signed(bit_width=self.bit_width) if is_signed else Unsigned(bit_width=self.bit_width)
        )

    @property
    def is_signed(self) -> bool:
        return self._is_signed

    @property
    def min_value(self) -> float:
        min_integer_value = self._integer.min_value
        min_integer_binary = self._integer.convert_to_unsigned_binary(min_integer_value)
        return self.convert_from_unsigned_binary(min_integer_binary)

    @property
    def max_value(self) -> float:
        max_integer_value = self._integer.max_value
        max_integer_binary = self._integer.convert_to_unsigned_binary(max_integer_value)
        return self.convert_from_unsigned_binary(max_integer_binary)

    def convert_from_unsigned_binary(self, unsigned_binary: int) -> float:
        self._check_unsigned_binary_value_in_range(unsigned_binary)
        return from_unsigned_binary(
            num_bits=self.bit_width,
            value=unsigned_binary,
            num_integer_bits=self.integer_bit_width,
            num_fractional_bits=self.fraction_bit_width,
            is_signed=self.is_signed,
        )

    def convert_to_unsigned_binary(self, value: float) -> int:
        self._check_native_value_in_range(value)
        return to_unsigned_binary(
            num_bits=self.bit_width,
            value=value,
            num_integer_bits=self.integer_bit_width,
            num_fractional_bits=self.fraction_bit_width,
            is_signed=self.is_signed,
        )

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
max_bit_index={self.max_bit_index},\
min_bit_index={self.min_bit_index},\
)"""


class UnsignedFixedPoint(Fixed):
    def __init__(self, max_bit_index: int, min_bit_index: int):
        """
        Unsigned fixed point format to represent fractional values.

        The bit_index arguments indicates the position of the decimal point in
        relation to the number expressed by the field. The decimal point is
        between the "0" and "-1" bit index. If the bit_index argument is
        negative, then the number represented by the field will include a
        fractional portion.

        e.g. ufixed (4 downto -5) specifies unsigned fixed point, 10 bits wide,
        with 5 bits of decimal. Consequently y = 6.5 = "00110.10000".

        Arguments:
            max_bit_index: Position of the upper bit relative to the decimal point.
            min_bit_index: Position of the lower bit relative to the decimal point.
        """
        super().__init__(is_signed=False, max_bit_index=max_bit_index, min_bit_index=min_bit_index)

    @classmethod
    def from_bit_widths(
        cls, integer_bit_width: int, fraction_bit_width: int
    ) -> "UnsignedFixedPoint":
        """
        Create instance via the respective fixed point bit widths.

        Arguments:
            integer_bit_width: The number of bits assigned to the integer part of the field value.
            fraction_bit_width: The number of bits assigned to the fractional part of the
                field value.
        """
        return cls(max_bit_index=integer_bit_width - 1, min_bit_index=-fraction_bit_width)


class SignedFixedPoint(Fixed):
    def __init__(self, max_bit_index: int, min_bit_index: int):
        """
        Signed fixed point format to represent fractional values.
        Signed integer uses two's complement representation.

        The bit_index arguments indicates the position of the decimal point in
        relation to the number expressed by the field. The decimal point is
        between the "0" and "-1" bit index. If the bit_index argument is
        negative, then the number represented by the field will include a
        fractional portion.

        e.g. sfixed (4 downto -5) specifies signed fixed point, 10 bits wide,
        with 5 bits of decimal. Consequently y = -6.5 = "11001.10000".

        Arguments:
            max_bit_index: Position of the upper bit relative to the decimal point.
            min_bit_index: Position of the lower bit relative to the decimal point.
        """
        super().__init__(is_signed=True, max_bit_index=max_bit_index, min_bit_index=min_bit_index)

    @classmethod
    def from_bit_widths(cls, integer_bit_width: int, fraction_bit_width: int) -> "SignedFixedPoint":
        """
        Create instance via the respective fixed point bit widths.

        Arguments:
            integer_bit_width: The number of bits assigned to the integer part of the field value.
            fraction_bit_width: The number of bits assigned to the fractional part of the
                field value.
        """
        return cls(max_bit_index=integer_bit_width - 1, min_bit_index=-fraction_bit_width)
