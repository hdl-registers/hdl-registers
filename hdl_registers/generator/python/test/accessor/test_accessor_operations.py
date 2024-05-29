# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import contextlib
import io
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from unittest.mock import Mock

# Third party libraries
import pytest

# First party libraries
from hdl_registers.generator.python.register_accessor_interface import (
    PythonRegisterAccessorInterface,
)

# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


@pytest.fixture
def default_accessor(generate_default_accessor):
    """
    Set up mocks and an object to perform common operations.
    Needs to be function-scoped since we want to check mock calls for each test.
    """
    tmp_path_session, python_module = generate_default_accessor

    register_accessor = Mock(spec=PythonRegisterAccessorInterface)
    test_accessor = python_module.get_accessor(register_accessor=register_accessor)

    class DefaultAccessor:
        def __init__(self):
            self.tmp_path_session = tmp_path_session
            self.python_module = python_module
            self.register_accessor = register_accessor
            self.test_accessor = test_accessor

        def set_read_value(self, value: int):
            self.register_accessor.read_register.return_value = value

        def assert_call(
            self,
            read_index: Optional[int] = None,
            write_index: Optional[int] = None,
            write_value: Optional[int] = None,
        ):
            if read_index is None:
                self.register_accessor.read_register.assert_not_called()
            else:
                self.register_accessor.read_register.assert_called_once_with(
                    register_list_name="test", register_address=4 * read_index
                )

            if write_index is None:
                self.register_accessor.write_register.assert_not_called()
            else:
                self.register_accessor.write_register.assert_called_once_with(
                    register_list_name="test",
                    register_address=4 * write_index,
                    register_value=write_value,
                )

    return DefaultAccessor()


SAMPLE_U32_0 = 0b10101010101010101010101010101010
SAMPLE_U32_1 = 0b01010101010101010101010101010101


# ==================================================================================================
# Test values for the 'test_register' with the 'a' fields.
# ==================================================================================================


def get_a_value_int(  # pylint: disable=too-many-arguments
    bit_aa0=0b0,
    bit_aa1=0b1,
    unsigned_aa=0b0101,
    signed_aa=0b1010,
    ufixed_aa=0b0110,
    sfixed_aa=0b1001,
    enumeration_aa=0b01,
    uint_aa=0b0101,
    sint_aa=0b00010,
):
    """
    Default argument values correspond to the default values in the register.
    """
    return (
        (bit_aa0 << 0)
        + (bit_aa1 << 1)
        + (unsigned_aa << 2)
        + (signed_aa << 6)
        + (ufixed_aa << 10)
        + (sfixed_aa << 14)
        + (enumeration_aa << 18)
        + (uint_aa << 20)
        + (sint_aa << 24)
    )


def a_value0_int(  # pylint: disable=too-many-arguments
    bit_aa0=0b0,
    bit_aa1=0b1,
    unsigned_aa=0b0110,
    signed_aa=0b1001,
    ufixed_aa=0b1100,
    sfixed_aa=0b1101,
    enumeration_aa=0b10,
    uint_aa=0b1010,
    sint_aa=0b11011,
):
    return get_a_value_int(
        bit_aa0=bit_aa0,
        bit_aa1=bit_aa1,
        unsigned_aa=unsigned_aa,
        signed_aa=signed_aa,
        ufixed_aa=ufixed_aa,
        sfixed_aa=sfixed_aa,
        enumeration_aa=enumeration_aa,
        uint_aa=uint_aa,
        sint_aa=sint_aa,
    )


def a_value0_class(value_class, uint_aa=10):
    return value_class(
        bit_aa0=0,
        bit_aa1=1,
        unsigned_aa=6,
        signed_aa=-7,
        ufixed_aa=3.0,
        sfixed_aa=-0.375,
        enumeration_aa=value_class.EnumerationAa.ELEMENT_AA2,
        uint_aa=uint_aa,
        sint_aa=-5,
    )


def a_value1_int(  # pylint: disable=too-many-arguments
    bit_aa0=0b1,
    bit_aa1=0b0,
    unsigned_aa=0b1111,
    signed_aa=0b1101,
    ufixed_aa=0b1011,
    sfixed_aa=0b1110,
    enumeration_aa=0b00,
    uint_aa=0b0101,
    sint_aa=0b00011,
):
    return get_a_value_int(
        bit_aa0=bit_aa0,
        bit_aa1=bit_aa1,
        unsigned_aa=unsigned_aa,
        signed_aa=signed_aa,
        ufixed_aa=ufixed_aa,
        sfixed_aa=sfixed_aa,
        enumeration_aa=enumeration_aa,
        uint_aa=uint_aa,
        sint_aa=sint_aa,
    )


def a_value1_class(value_class):
    return value_class(
        bit_aa0=1,
        bit_aa1=0,
        unsigned_aa=15,
        signed_aa=-3,
        ufixed_aa=2.75,
        sfixed_aa=-0.25,
        enumeration_aa=value_class.EnumerationAa.ELEMENT_AA0,
        uint_aa=5,
        sint_aa=3,
    )


def a_value2_int(  # pylint: disable=too-many-arguments
    bit_aa0=0b0,
    bit_aa1=0b1,
    unsigned_aa=0b0010,
    signed_aa=0b1101,
    ufixed_aa=0b1100,
    sfixed_aa=0b1000,
    enumeration_aa=0b10,
    uint_aa=0b0111,
    sint_aa=0b01010,
):
    return get_a_value_int(
        bit_aa0=bit_aa0,
        bit_aa1=bit_aa1,
        unsigned_aa=unsigned_aa,
        signed_aa=signed_aa,
        ufixed_aa=ufixed_aa,
        sfixed_aa=sfixed_aa,
        enumeration_aa=enumeration_aa,
        uint_aa=uint_aa,
        sint_aa=sint_aa,
    )


def a_value2_class(value_class):
    return value_class(
        bit_aa0=0,
        bit_aa1=1,
        unsigned_aa=2,
        signed_aa=-3,
        ufixed_aa=3.0,
        sfixed_aa=-1.0,
        enumeration_aa=value_class.EnumerationAa.ELEMENT_AA2,
        uint_aa=7,
        sint_aa=10,
    )


# ==================================================================================================


# ==================================================================================================
# Read empty registers.
# Methods should take integer value.
#
# Variants:
# * Array registers, plain registers.
# * Mode: r, r_w, r_wpulse
#
# 6 tests in total.
# ==================================================================================================


def test_read_empty_r_register_plain(default_accessor):
    default_accessor.set_read_value(SAMPLE_U32_0)
    assert default_accessor.test_accessor.read_empty_r() == SAMPLE_U32_0

    default_accessor.assert_call(read_index=5)


def test_read_empty_r_w_register_plain(default_accessor):
    default_accessor.set_read_value(SAMPLE_U32_1)
    assert default_accessor.test_accessor.read_empty_r_w() == SAMPLE_U32_1

    default_accessor.assert_call(read_index=7)


def test_read_empty_r_wpulse_register_plain(default_accessor):
    default_accessor.set_read_value(SAMPLE_U32_0)
    assert default_accessor.test_accessor.read_empty_r_wpulse() == SAMPLE_U32_0

    default_accessor.assert_call(read_index=9)


def test_read_empty_r_register_in_array(default_accessor):
    default_accessor.set_read_value(SAMPLE_U32_0)
    assert default_accessor.test_accessor.read_reg_array_a_empty_r(array_index=2) == SAMPLE_U32_0

    default_accessor.assert_call(read_index=15 + 2 * 15 + 5)


def test_read_empty_r_w_register_in_array(default_accessor):
    default_accessor.set_read_value(SAMPLE_U32_1)
    assert default_accessor.test_accessor.read_reg_array_a_empty_r_w(array_index=2) == SAMPLE_U32_1

    default_accessor.assert_call(read_index=15 + 2 * 15 + 7)


def test_read_empty_r_wpulse_register_in_array(default_accessor):
    default_accessor.set_read_value(SAMPLE_U32_0)
    assert (
        default_accessor.test_accessor.read_reg_array_a_empty_r_wpulse(array_index=2)
        == SAMPLE_U32_0
    )

    default_accessor.assert_call(read_index=15 + 2 * 15 + 9)


# ==================================================================================================


# ==================================================================================================
# Write empty registers.
# Methods should take integer argument values.
#
# Variants:
# * Array registers, plain registers.
# * Mode: w, r_w, wpulse, r_wpulse
#
# 8 tests in total.
# ==================================================================================================


def test_write_empty_w_register_plain(default_accessor):
    default_accessor.test_accessor.write_empty_w(register_value=SAMPLE_U32_1)

    default_accessor.assert_call(write_index=6, write_value=SAMPLE_U32_1)


def test_write_empty_r_w_register_plain(default_accessor):
    default_accessor.test_accessor.write_empty_r_w(register_value=SAMPLE_U32_0)

    default_accessor.assert_call(write_index=7, write_value=SAMPLE_U32_0)


def test_write_empty_wpulse_register_plain(default_accessor):
    default_accessor.test_accessor.write_empty_wpulse(register_value=SAMPLE_U32_1)

    default_accessor.assert_call(write_index=8, write_value=SAMPLE_U32_1)


def test_write_empty_r_wpulse_register_plain(default_accessor):
    default_accessor.test_accessor.write_empty_r_wpulse(register_value=SAMPLE_U32_0)

    default_accessor.assert_call(write_index=9, write_value=SAMPLE_U32_0)


def test_write_empty_w_register_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_empty_w(
        register_value=SAMPLE_U32_1, array_index=2
    )

    default_accessor.assert_call(write_index=15 + 2 * 15 + 6, write_value=SAMPLE_U32_1)


def test_write_empty_r_w_register_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_empty_r_w(
        register_value=SAMPLE_U32_0, array_index=2
    )

    default_accessor.assert_call(write_index=15 + 2 * 15 + 7, write_value=SAMPLE_U32_0)


def test_write_empty_wpulse_register_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_empty_wpulse(
        register_value=SAMPLE_U32_1, array_index=2
    )

    default_accessor.assert_call(write_index=15 + 2 * 15 + 8, write_value=SAMPLE_U32_1)


def test_write_empty_r_wpulse_register_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_empty_r_wpulse(
        register_value=SAMPLE_U32_0, array_index=2
    )

    default_accessor.assert_call(write_index=15 + 2 * 15 + 9, write_value=SAMPLE_U32_0)


# ==================================================================================================


# ==================================================================================================
# Read registers with value converted to value class.
# Methods should return class object.
#
# Variants:
# * Array registers, plain registers.
# * Mode: r, r_w, r_wpulse
#
# 6 tests in total.
# ==================================================================================================


def test_read_class_r_plain(default_accessor):
    default_accessor.set_read_value(a_value0_int())
    assert default_accessor.test_accessor.read_reg_r() == a_value0_class(
        default_accessor.python_module.TestRegRValue
    )

    default_accessor.assert_call(read_index=0)


def test_read_class_r_w_plain(default_accessor):
    default_accessor.set_read_value(a_value1_int())
    assert default_accessor.test_accessor.read_reg_r_w() == a_value1_class(
        default_accessor.python_module.TestRegRWValue
    )

    default_accessor.assert_call(read_index=2)


def test_read_class_r_wpulse_plain(default_accessor):
    default_accessor.set_read_value(a_value2_int())
    assert default_accessor.test_accessor.read_reg_r_wpulse() == a_value2_class(
        default_accessor.python_module.TestRegRWpulseValue
    )

    default_accessor.assert_call(read_index=4)


def test_read_class_r_in_array(default_accessor):
    default_accessor.set_read_value(a_value2_int())
    assert default_accessor.test_accessor.read_reg_array_a_reg_r(array_index=2) == a_value2_class(
        default_accessor.python_module.TestRegArrayARegRValue
    )

    default_accessor.assert_call(read_index=15 + 2 * 15 + 0)


def test_read_class_r_w_in_array(default_accessor):
    default_accessor.set_read_value(a_value1_int())
    assert default_accessor.test_accessor.read_reg_array_a_reg_r_w(array_index=2) == a_value1_class(
        default_accessor.python_module.TestRegArrayARegRWValue
    )

    default_accessor.assert_call(read_index=15 + 2 * 15 + 2)


def test_read_class_r_wpulse_in_array(default_accessor):
    default_accessor.set_read_value(a_value0_int())
    assert default_accessor.test_accessor.read_reg_array_a_reg_r_wpulse(
        array_index=1
    ) == a_value0_class(default_accessor.python_module.TestRegArrayARegRWpulseValue)

    default_accessor.assert_call(read_index=15 + 1 * 15 + 4)


# ==================================================================================================


# ==================================================================================================
# Write registers with value class.
# Methods should take class objects.
#
# Variants:
# * Array registers, plain registers.
# * Mode: w, r_w, wpulse, r_wpulse
#
# 8 tests in total.
# ==================================================================================================


def test_write_class_w_plain(default_accessor):
    default_accessor.test_accessor.write_reg_w(
        register_value=a_value0_class(default_accessor.python_module.TestRegWValue),
    )

    default_accessor.assert_call(write_index=1, write_value=a_value0_int())


def test_write_class_r_w_plain(default_accessor):
    default_accessor.test_accessor.write_reg_r_w(
        register_value=a_value1_class(default_accessor.python_module.TestRegRWValue),
    )

    default_accessor.assert_call(write_index=2, write_value=a_value1_int())


def test_write_class_wpulse_plain(default_accessor):
    default_accessor.test_accessor.write_reg_wpulse(
        register_value=a_value2_class(default_accessor.python_module.TestRegWpulseValue),
    )

    default_accessor.assert_call(write_index=3, write_value=a_value2_int())


def test_write_class_r_wpulse_plain(default_accessor):
    default_accessor.test_accessor.write_reg_r_wpulse(
        register_value=a_value0_class(default_accessor.python_module.TestRegRWpulseValue),
    )

    default_accessor.assert_call(write_index=4, write_value=a_value0_int())


def test_write_class_w_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_w(
        register_value=a_value1_class(default_accessor.python_module.TestRegArrayARegWValue),
        array_index=2,
    )

    default_accessor.assert_call(write_index=15 + 2 * 15 + 1, write_value=a_value1_int())


def test_write_class_r_w_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_r_w(
        register_value=a_value2_class(default_accessor.python_module.TestRegArrayARegRWValue),
        array_index=1,
    )

    default_accessor.assert_call(write_index=15 + 1 * 15 + 2, write_value=a_value2_int())


def test_write_class_wpulse_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_wpulse(
        register_value=a_value0_class(default_accessor.python_module.TestRegArrayARegRWpulseValue),
        array_index=2,
    )

    default_accessor.assert_call(write_index=15 + 2 * 15 + 3, write_value=a_value0_int())


def test_write_class_r_wpulse_in_array(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_r_wpulse(
        register_value=a_value1_class(default_accessor.python_module.TestRegArrayARegRWpulseValue),
        array_index=0,
    )

    default_accessor.assert_call(write_index=15 + 0 * 15 + 4, write_value=a_value1_int())


# ==================================================================================================


# ==================================================================================================
# Write field to register that has only a single field.
# Methods should take native type.
#
# Variants:
# * Array registers, plain registers.
# * Mode: w, r_w, wpulse, r_wpulse
# * Type: bit, unsigned, signed, ufixed, sfixed, enumeration, uint, sint
#
# We test a subset of all possible combinations. Most important is to try the different types.
# ==================================================================================================


def test_write_field_w_plain_single_bit(default_accessor):
    default_accessor.test_accessor.write_single_w_bit_bit_bb(field_value=1)

    default_accessor.assert_call(write_index=10, write_value=0b1)


def test_write_field_w_plain_single_unsigned(default_accessor):
    default_accessor.test_accessor.write_single_w_unsigned_unsigned_bb(field_value=15)

    default_accessor.assert_call(write_index=11, write_value=0b1111)


def test_write_field_r_w_plain_single_sfixed(default_accessor):
    default_accessor.test_accessor.write_single_r_w_sfixed_sfixed_bb(field_value=-1.75)

    default_accessor.assert_call(write_index=12, write_value=0b1001)


def test_write_field_wpulse_plain_single_enumeration(default_accessor):
    field_value = (
        default_accessor.python_module.TestSingleWpulseEnumerationValue.EnumerationBb.ELEMENT_BB2
    )
    default_accessor.test_accessor.write_single_wpulse_enumeration_enumeration_bb(
        field_value=field_value
    )

    default_accessor.assert_call(write_index=13, write_value=0b10)


def test_write_field_r_wpulse_plain_single_uint(default_accessor):
    default_accessor.test_accessor.write_single_r_wpulse_uint_uint_bb(field_value=11)

    default_accessor.assert_call(write_index=14, write_value=0b1011)


def test_write_field_r_w_in_array_single_sfixed(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_single_r_w_sfixed_sfixed_bb(
        field_value=1.5, array_index=2
    )

    default_accessor.assert_call(write_index=15 + 15 * 2 + 12, write_value=0b0110)


def test_write_field_wpulse_in_array_single_enumeration(default_accessor):
    register_value_class = default_accessor.python_module.TestRegArrayASingleWpulseEnumerationValue
    field_value = register_value_class.EnumerationBb.ELEMENT_BB1
    default_accessor.test_accessor.write_reg_array_a_single_wpulse_enumeration_enumeration_bb(
        field_value=field_value, array_index=1
    )

    default_accessor.assert_call(write_index=15 + 15 * 1 + 13, write_value=0b01)


# ==================================================================================================


# ==================================================================================================
# Write field to register that has multiple fields.
# Methods should take native type.
#
# Variants:
# * Array registers, plain registers.
# * Mode: w, r_w, wpulse, r_wpulse
# * Type: bit, unsigned, signed, ufixed, sfixed, enumeration, uint, sint
#
# Mode 'r_w' should do a read-modify-write.
# Mode 'w', 'wpulse' and 'r_wpulse' should do a write with all other fields set to default.
#
# We test a subset of all possible combinations.
# ==================================================================================================


def test_write_field_w_plain_multiple_bit_aa0(default_accessor):
    default_accessor.test_accessor.write_reg_w_bit_aa0(field_value=1)

    default_accessor.assert_call(write_index=1, write_value=get_a_value_int(bit_aa0=0b1))


def test_write_field_w_plain_multiple_bit_aa1(default_accessor):
    default_accessor.test_accessor.write_reg_w_bit_aa1(field_value=0)

    default_accessor.assert_call(write_index=1, write_value=get_a_value_int(bit_aa1=0b0))


def test_write_field_w_plain_multiple_unsigned_aa(default_accessor):
    default_accessor.test_accessor.write_reg_w_unsigned_aa(field_value=9)

    default_accessor.assert_call(write_index=1, write_value=get_a_value_int(unsigned_aa=0b1001))


def test_write_field_wpulse_plain_multiple_signed_aa(default_accessor):
    default_accessor.test_accessor.write_reg_wpulse_signed_aa(field_value=-3)

    default_accessor.assert_call(write_index=3, write_value=get_a_value_int(signed_aa=0b1101))


def test_write_field_wpulse_plain_multiple_ufixed_aa(default_accessor):
    default_accessor.test_accessor.write_reg_wpulse_ufixed_aa(field_value=3.25)

    default_accessor.assert_call(write_index=3, write_value=get_a_value_int(ufixed_aa=0b1101))


def test_write_field_wpulse_plain_multiple_sfixed_aa(default_accessor):
    default_accessor.test_accessor.write_reg_wpulse_sfixed_aa(field_value=-0.75)

    default_accessor.assert_call(write_index=3, write_value=get_a_value_int(sfixed_aa=0b1010))


def test_write_field_r_wpulse_in_array_multiple_enumeration_aa(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_r_wpulse_enumeration_aa(
        field_value=default_accessor.python_module.TestRegRWpulseValue.EnumerationAa.ELEMENT_AA2,
        array_index=0,
    )

    default_accessor.assert_call(
        write_index=15 + 15 * 0 + 4, write_value=get_a_value_int(enumeration_aa=0b10)
    )


def test_write_field_r_wpulse_in_array_multiple_uint_aa(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_r_wpulse_uint_aa(
        field_value=10, array_index=1
    )

    default_accessor.assert_call(
        write_index=15 + 15 * 1 + 4, write_value=get_a_value_int(uint_aa=0b1010)
    )


def test_write_field_r_wpulse_in_array_multiple_sint_aa(default_accessor):
    default_accessor.test_accessor.write_reg_array_a_reg_r_wpulse_sint_aa(
        field_value=-3, array_index=2
    )

    default_accessor.assert_call(
        write_index=15 + 15 * 2 + 4, write_value=get_a_value_int(sint_aa=0b11101)
    )


def test_write_field_r_w_plain_multiple_bit_aa0(default_accessor):
    default_accessor.set_read_value(a_value0_int())
    default_accessor.test_accessor.write_reg_r_w_bit_aa0(field_value=1)

    default_accessor.assert_call(read_index=2, write_index=2, write_value=a_value0_int(bit_aa0=0b1))


def test_write_field_r_w_plain_multiple_bit_aa1(default_accessor):
    default_accessor.set_read_value(a_value0_int())
    default_accessor.test_accessor.write_reg_r_w_bit_aa1(field_value=0)

    default_accessor.assert_call(read_index=2, write_index=2, write_value=a_value0_int(bit_aa1=0b0))


def test_write_field_r_w_plain_multiple_unsigned_aa(default_accessor):
    default_accessor.set_read_value(a_value0_int())
    default_accessor.test_accessor.write_reg_r_w_unsigned_aa(field_value=9)

    default_accessor.assert_call(
        read_index=2, write_index=2, write_value=a_value0_int(unsigned_aa=0b1001)
    )


def test_write_field_r_w_plain_multiple_signed_aa(default_accessor):
    default_accessor.set_read_value(a_value1_int())
    default_accessor.test_accessor.write_reg_r_w_signed_aa(field_value=-3)

    default_accessor.assert_call(
        read_index=2, write_index=2, write_value=a_value1_int(signed_aa=0b1101)
    )


def test_write_field_r_w_plain_multiple_ufixed_aa(default_accessor):
    default_accessor.set_read_value(a_value1_int())
    default_accessor.test_accessor.write_reg_r_w_ufixed_aa(field_value=3.25)

    default_accessor.assert_call(
        read_index=2, write_index=2, write_value=a_value1_int(ufixed_aa=0b1101)
    )


def test_write_field_r_w_plain_multiple_sfixed_aa(default_accessor):
    default_accessor.set_read_value(a_value1_int())
    default_accessor.test_accessor.write_reg_r_w_sfixed_aa(field_value=-0.75)

    default_accessor.assert_call(
        read_index=2,
        write_index=2,
        write_value=a_value1_int(sfixed_aa=0b1010),
    )


def test_write_field_r_w_in_array_multiple_enumeration_aa(default_accessor):
    default_accessor.set_read_value(a_value2_int())
    default_accessor.test_accessor.write_reg_array_a_reg_r_w_enumeration_aa(
        field_value=default_accessor.python_module.TestRegRWValue.EnumerationAa.ELEMENT_AA2,
        array_index=0,
    )

    default_accessor.assert_call(
        read_index=15 + 15 * 0 + 2,
        write_index=15 + 15 * 0 + 2,
        write_value=a_value2_int(enumeration_aa=0b10),
    )


def test_write_field_r_w_in_array_multiple_uint_aa(default_accessor):
    default_accessor.set_read_value(a_value2_int())
    default_accessor.test_accessor.write_reg_array_a_reg_r_w_uint_aa(field_value=10, array_index=1)

    default_accessor.assert_call(
        read_index=15 + 15 * 1 + 2,
        write_index=15 + 15 * 1 + 2,
        write_value=a_value2_int(uint_aa=0b1010),
    )


def test_write_field_r_w_in_array_multiple_sint_aa(default_accessor):
    default_accessor.set_read_value(a_value2_int())
    default_accessor.test_accessor.write_reg_array_a_reg_r_w_sint_aa(field_value=-3, array_index=2)

    default_accessor.assert_call(
        read_index=15 + 15 * 2 + 2,
        write_index=15 + 15 * 2 + 2,
        write_value=a_value2_int(sint_aa=0b11101),
    )


# ==================================================================================================


# ==================================================================================================
# Basic tests
# ==================================================================================================


def test_read_with_array_index_out_of_bound_should_raise_exception(default_accessor):
    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.read_reg_array_a_empty_r(array_index=3)
    assert (
        str(exception_info.value)
        == 'Index 3 out of range for register array "reg_array_a" of length 3.'
    )


def test_read_with_array_index_negative_should_raise_exception(default_accessor):
    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.read_reg_array_a_empty_r(array_index=-1)
    assert (
        str(exception_info.value)
        == 'Index -1 out of range for register array "reg_array_a" of length 3.'
    )


def test_read_integer_out_of_range_should_raise_exception(default_accessor):
    default_accessor.set_read_value(a_value0_int(uint_aa=0b1111))

    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.read_reg_r_w()
    assert (
        str(exception_info.value)
        == 'Register field value "15" not inside "uint_aa" field\'s legal range: (0, 10).'
    )


def test_read_enumeration_out_of_range_should_raise_exception(default_accessor):
    default_accessor.set_read_value(a_value0_int(enumeration_aa=0b11))

    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.read_reg_r_w()
    assert (
        str(exception_info.value)
        == 'Enumeration "enumeration_aa", requested element value does not exist. Got: "3".'
    )


def test_write_integer_out_of_range_should_raise_exception(default_accessor):
    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.write_reg_r_w(
            a_value0_class(value_class=default_accessor.python_module.TestRegRWValue, uint_aa=15)
        )
    assert (
        str(exception_info.value)
        == 'Value "15" not inside "uint_aa" field\'s legal range: (0, 10).'
    )


def test_write_enumeration_out_of_range_should_raise_exception(default_accessor):
    @dataclass
    class ValueClass:  # pylint: disable=too-many-instance-attributes
        class EnumerationAa(Enum):
            ELEMENT_AA0 = 1
            ELEMENT_AA1 = 2
            ELEMENT_AA2 = 3

        bit_aa0: int
        bit_aa1: int
        unsigned_aa: int
        signed_aa: int
        ufixed_aa: float
        sfixed_aa: float
        enumeration_aa: EnumerationAa
        uint_aa: int
        sint_aa: int

    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.write_reg_r_w(a_value0_class(value_class=ValueClass))
    assert (
        str(exception_info.value)
        == 'Enumeration "enumeration_aa", requested element name does not exist. Got: "3".'
    )


def test_register_accessor_read_value_out_of_range_should_raise_exception(default_accessor):
    default_accessor.set_read_value(2**32)
    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.read_reg_r_w()
    assert (
        str(exception_info.value)
        == 'Register read value "4294967296" from accessor is out of range.'
    )

    default_accessor.set_read_value(-1)
    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.read_reg_r_w()
    assert str(exception_info.value) == 'Register read value "-1" from accessor is out of range.'


def test_register_write_value_out_of_range_should_raise_exception(default_accessor):
    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.write_empty_w(register_value=2**32)
    assert str(exception_info.value) == 'Register write value "4294967296" is out of range.'

    with pytest.raises(ValueError) as exception_info:
        default_accessor.test_accessor.write_empty_w(register_value=-1)
    assert str(exception_info.value) == 'Register write value "-1" is out of range.'


# ==================================================================================================


# ==================================================================================================
# Test printing
# ==================================================================================================


def test_print_registers(default_accessor):
    default_accessor.set_read_value(a_value0_int())

    string_io = io.StringIO()
    with contextlib.redirect_stdout(string_io):
        default_accessor.test_accessor.print_registers()
        stdout = string_io.getvalue()

    # To inspect:
    # print(stdout)
    # assert False

    values = """\
  bit_aa0: 0
  bit_aa1: 1
  unsigned_aa: 6 (hexadecimal 6, binary 0110)
  signed_aa: -7 (unsigned decimal 9, hexadecimal 9, binary 1001)
  ufixed_aa: 3.0 (unsigned decimal 12, hexadecimal C, binary 1100)
  sfixed_aa: -0.375 (unsigned decimal 13, hexadecimal D, binary 1101)
  enumeration_aa: ELEMENT_AA2 (2)
  uint_aa: 10 (hexadecimal A, binary 1010)
  sint_aa: -5 (unsigned decimal 27, hexadecimal 1B, binary 1_1011)
"""

    assert (
        f"""\
Register 'reg_r' .............................................................. \
(index 0, address 0):
{values}
"""
        in stdout
    )

    assert (
        f"""
Register 'reg_array_a[2].reg_r_wpulse' ........................................ \
(index 49, address 196):
{values}
"""
        in stdout
    )
    assert (
        """
Register 'reg_array_a[2].reg_wpulse' .......................................... \
(index 48, address 192):
  Not readable.
"""
        in stdout
    )


def test_print_registers_value1(default_accessor):
    default_accessor.set_read_value(a_value1_int())

    string_io = io.StringIO()
    with contextlib.redirect_stdout(string_io):
        default_accessor.test_accessor.print_registers()
        stdout = string_io.getvalue()

    values = """\
  bit_aa0: 1
  bit_aa1: 0
  unsigned_aa: 15 (hexadecimal F, binary 1111)
  signed_aa: -3 (unsigned decimal 13, hexadecimal D, binary 1101)
  ufixed_aa: 2.75 (unsigned decimal 11, hexadecimal B, binary 1011)
  sfixed_aa: -0.25 (unsigned decimal 14, hexadecimal E, binary 1110)
  enumeration_aa: ELEMENT_AA0 (0)
  uint_aa: 5 (hexadecimal 5, binary 0101)
  sint_aa: 3 (unsigned decimal 3, hexadecimal 03, binary 0_0011)
"""

    assert (
        f"""\
Register 'reg_r' .............................................................. \
(index 0, address 0):
{values}
"""
        in stdout
    )


def test_print_registers_value2(default_accessor):
    default_accessor.set_read_value(a_value2_int())

    string_io = io.StringIO()
    with contextlib.redirect_stdout(string_io):
        default_accessor.test_accessor.print_registers()
        stdout = string_io.getvalue()

    values = """\
  bit_aa0: 0
  bit_aa1: 1
  unsigned_aa: 2 (hexadecimal 2, binary 0010)
  signed_aa: -3 (unsigned decimal 13, hexadecimal D, binary 1101)
  ufixed_aa: 3.0 (unsigned decimal 12, hexadecimal C, binary 1100)
  sfixed_aa: -1.0 (unsigned decimal 8, hexadecimal 8, binary 1000)
  enumeration_aa: ELEMENT_AA2 (2)
  uint_aa: 7 (hexadecimal 7, binary 0111)
  sint_aa: 10 (unsigned decimal 10, hexadecimal 0A, binary 0_1010)
"""

    assert (
        f"""\
Register 'reg_r' .............................................................. \
(index 0, address 0):
{values}
"""
        in stdout
    )


# ==================================================================================================
