# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from abc import ABC, abstractmethod


def _from_unsigned_binary(
    bit_width: int,
    unsigned_binary: int,
    integer_bit_width: int = None,
    fraction_bit_width: int = 0,
    is_signed: bool = False,
) -> float:
    """
    Convert from an unsigned binary to one of:
        - unsigned integer
        - signed integer
        - unsigned fixed point
        - signed fixed point

    Signed uses two's complement representation.

    Sources:
        https://en.wikibooks.org/wiki/Floating_Point/Fixed-Point_Numbers
        https://vhdlguru.blogspot.com/2010/03/fixed-point-operations-in-vhdl-tutorial.html

    Arguments:
        bit_width (int) : Width of the field.
        unsigned_binary (int): Unsigned binary integer representation of the field.
        integer_bit_width (int): If fixed point, the number of bits assigned to the
            integer part of the field value.
        fraction_bit_width (int): If fixed point, the number of bits assigned to the
            fractional part of the field value.
        is_signed (bool): Is the field signed (Two's compliment)?

    Returns:
        float: Native Python representation of the field value.
    """
    integer_bit_width = bit_width if integer_bit_width is None else integer_bit_width

    if integer_bit_width + fraction_bit_width != bit_width:
        raise ValueError("Inconsistent bit width")

    value = unsigned_binary * 2**-fraction_bit_width
    if is_signed:
        sign_bit = unsigned_binary & (1 << (bit_width - 1))
        if sign_bit != 0:
            # If sign bit is set, compute negative value.
            value -= 2**integer_bit_width

    return value


def _to_unsigned_binary(
    bit_width: int,
    value: float,
    integer_bit_width: int = None,
    fraction_bit_width: int = 0,
    is_signed: bool = False,
) -> int:
    """
    Convert from one of:
        - unsigned integer
        - signed integer
        - unsigned fixed point
        - signed fixed point
    into an unsigned binary.

    Signed uses two's complement representation.

    Sources:
        https://en.wikibooks.org/wiki/Floating_Point/Fixed-Point_Numbers
        https://vhdlguru.blogspot.com/2010/03/fixed-point-operations-in-vhdl-tutorial.html

    Arguments:
        bit_width (int) : Width of the field.
        value (float): Native Python representation of the field value.
        integer_bit_width (int): If fixed point, the number of bits assigned to the
            integer part of the field value.
        fraction_bit_width (int): If fixed point, the number of bits assigned to the
            fractional part of the field value.
        is_signed (bool): Is the field signed (Two's compliment)?

    Returns:
        int: Unsigned binary integer representation of the field.
    """
    integer_bit_width = bit_width if integer_bit_width is None else integer_bit_width

    if integer_bit_width + fraction_bit_width != bit_width:
        raise ValueError("Inconsistent bit width")

    binary_value = round(value * 2**fraction_bit_width)
    if value < 0:
        if is_signed:
            binary_value += 1 << bit_width
        else:
            raise ValueError("Attempting to convert negative value to unsigned")

    return binary_value


class FieldType(ABC):
    @abstractmethod
    def min_value(self, bit_width: int):
        """
        Minimum representable value for this field type.
        """

    @abstractmethod
    def max_value(self, bit_width: int):
        """
        Maximum representable value for this field type.
        """

    @abstractmethod
    def convert_from_unsigned_binary(self, bit_width: int, unsigned_binary: int):
        """
        Convert from the unsigned binary integer representation of a field,
        into the native Python value of the field.

        Arguments:
            bit_width (int) : Width of the field.
            unsigned_binary (int): Unsigned binary integer representation of the field.
        """

    @abstractmethod
    def convert_to_unsigned_binary(self, bit_width: int, value) -> int:
        """
        Convert from the native Python value of the field, into the
        unsigned binary integer representation which can be written to a register.

        Arguments:
            bit_width (int) : Width of the field.
            value : Native Python representation of the field value.

        Returns:
            int: Unsigned binary integer representation of the field.
        """

    @abstractmethod
    def vhdl_typedef(self, bit_width: int) -> str:
        """
        VHDL representation of the field type for the VHDL generation.

        Arguments:
            bit_width (int) : Width of the field.

        Returns:
            str
        """

    @abstractmethod
    def __repr__(self):
        pass

    def _check_value_in_range(self, bit_width: int, value):
        """
        Check that a given field value is valid within the allowed range.

        Arguments:
            bit_width (int) : Width of the field.
            value : Native Python representation of the field value.
        """
        min_ = self.min_value(bit_width)
        max_ = self.max_value(bit_width)
        if not min_ <= value <= max_:
            raise ValueError(f"Value: {value} out of range of {bit_width}-bit ({min_}, {max_}).")


class Unsigned(FieldType):
    """
    Unsigned integer.
    """

    def min_value(self, bit_width: int) -> int:
        return 0

    def max_value(self, bit_width: int) -> int:
        return 2**bit_width - 1

    def convert_from_unsigned_binary(self, bit_width: int, unsigned_binary: int) -> int:
        return unsigned_binary

    def convert_to_unsigned_binary(self, bit_width: int, value: float) -> int:
        self._check_value_in_range(bit_width, value)
        return round(value)

    def vhdl_typedef(self, bit_width: int) -> str:
        return f"u_unsigned({bit_width-1} downto 0)"

    def __repr__(self):
        return self.__class__.__name__


class Signed(FieldType):
    """
    Two's complement signed integer format.
    """

    def min_value(self, bit_width: int) -> int:
        return -(2 ** (bit_width - 1))

    def max_value(self, bit_width: int) -> int:
        return 2 ** (bit_width - 1) - 1

    def convert_from_unsigned_binary(self, bit_width: int, unsigned_binary: int) -> int:
        return int(_from_unsigned_binary(bit_width, unsigned_binary, is_signed=True))

    def convert_to_unsigned_binary(self, bit_width: int, value: float) -> int:
        self._check_value_in_range(bit_width, value)
        return _to_unsigned_binary(bit_width, value, is_signed=True)

    def vhdl_typedef(self, bit_width: int) -> str:
        return f"u_signed({bit_width-1} downto 0)"

    def __repr__(self):
        return self.__class__.__name__


class Fixed(FieldType, ABC):
    def __init__(self, is_signed: bool, max_bit_index: int, min_bit_index: int):
        """
        Abstract baseclass for Fixed field types.

        The bit_index arguments indicates the position of the decimal point in
        relation to the number expressed by the field. The decimal point is
        between the "0" and "-1" bit index. If the bit_index argument is
        negative, then the number represented by the field will include a
        fractional portion.

        Arguments:
            is_signed (bool): Is the field signed (Two's compliment)?
            max_bit_index (int): Position of the upper bit relative to the decimal point.
            min_bit_index (int): Position of the lower bit relative to the decimal point.
        """
        self.is_signed = is_signed
        self._integer = Signed() if is_signed else Unsigned()
        self.max_bit_index = max_bit_index
        self.min_bit_index = min_bit_index
        if not self.max_bit_index >= self.min_bit_index:
            raise ValueError("max_bit_index must be >= min_bit_index")

        self.integer_bit_width = self.max_bit_index + 1
        self.fraction_bit_width = -self.min_bit_index
        self.expected_bit_width = self.integer_bit_width + self.fraction_bit_width

    def min_value(self, bit_width: int) -> float:
        min_integer_value = self._integer.min_value(bit_width)
        min_integer_binary = self._integer.convert_to_unsigned_binary(bit_width, min_integer_value)
        return self.convert_from_unsigned_binary(bit_width, min_integer_binary)

    def max_value(self, bit_width: int) -> float:
        max_integer_value = self._integer.max_value(bit_width)
        max_integer_binary = self._integer.convert_to_unsigned_binary(bit_width, max_integer_value)
        return self.convert_from_unsigned_binary(bit_width, max_integer_binary)

    def convert_from_unsigned_binary(self, bit_width: int, unsigned_binary: int) -> float:
        return _from_unsigned_binary(
            bit_width=bit_width,
            unsigned_binary=unsigned_binary,
            integer_bit_width=self.integer_bit_width,
            fraction_bit_width=self.fraction_bit_width,
            is_signed=self.is_signed,
        )

    def convert_to_unsigned_binary(self, bit_width: int, value: float) -> int:
        self._check_value_in_range(bit_width, value)
        return _to_unsigned_binary(
            bit_width=bit_width,
            value=value,
            integer_bit_width=self.integer_bit_width,
            fraction_bit_width=self.fraction_bit_width,
            is_signed=self.is_signed,
        )

    @abstractmethod
    def vhdl_typedef(self, bit_width: int) -> str:
        pass

    def __repr__(self):
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
            max_bit_index (int): Position of the upper bit relative to the decimal point.
            min_bit_index (int): Position of the lower bit relative to the decimal point.
        """
        super().__init__(is_signed=False, max_bit_index=max_bit_index, min_bit_index=min_bit_index)

    def vhdl_typedef(self, bit_width: int) -> str:
        if bit_width != self.expected_bit_width:
            raise ValueError("Inconsistent bit width")
        return f"ufixed({self.max_bit_index} downto {self.min_bit_index})"

    @classmethod
    def from_bit_widths(
        cls, integer_bit_width: int, fraction_bit_width: int
    ) -> "UnsignedFixedPoint":
        """
        Create instance via the respective fixed point bit widths.

        Arguments:
            integer_bit_width (int): The number of bits assigned to the
                integer part of the field value.
            fraction_bit_width (int): The number of bits assigned to the
                fractional part of the field value.
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
            max_bit_index (int): Position of the upper bit relative to the decimal point.
            min_bit_index (int): Position of the lower bit relative to the decimal point.
        """
        super().__init__(is_signed=True, max_bit_index=max_bit_index, min_bit_index=min_bit_index)

    def vhdl_typedef(self, bit_width: int) -> str:
        if bit_width != self.expected_bit_width:
            raise ValueError("Inconsistent bit width")
        return f"sfixed({self.max_bit_index} downto {self.min_bit_index})"

    @classmethod
    def from_bit_widths(cls, integer_bit_width: int, fraction_bit_width: int) -> "SignedFixedPoint":
        """
        Create instance via the respective fixed point bit widths.

        Arguments:
            integer_bit_width (int): The number of bits assigned to the
                integer part of the field value.
            fraction_bit_width (int): The number of bits assigned to the
                fractional part of the field value.
        """
        return cls(max_bit_index=integer_bit_width - 1, min_bit_index=-fraction_bit_width)
