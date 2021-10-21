# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import pytest
from tsfpga.registers.register import Register


def test_repr_basic():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(Register(name="apa", index=0, mode="r", description=""))

    # Different name
    assert repr(Register(name="apa", index=0, mode="r", description="")) != repr(
        Register(name="hest", index=0, mode="r", description="")
    )

    # Different index
    assert repr(Register(name="apa", index=0, mode="r", description="")) != repr(
        Register(name="apa", index=1, mode="r", description="")
    )

    # Different mode
    assert repr(Register(name="apa", index=0, mode="r", description="")) != repr(
        Register(name="apa", index=0, mode="w", description="")
    )

    # Different description
    assert repr(Register(name="apa", index=0, mode="r", description="Blaah")) != repr(
        Register(name="apa", index=0, mode="r", description="Gaah")
    )


def test_repr_with_bits_appended():
    """
    Shows that the ``fields`` impact the repr. Do not need to test with other fields than bits.
    """
    register_a = Register(name="apa", index=0, mode="r", description="")
    register_a.append_bit(name="hest", description="", default_value="0")

    register_b = Register(name="apa", index=0, mode="r", description="")
    register_b.append_bit(name="hest", description="", default_value="0")

    assert repr(register_a) == repr(register_b)

    register_a.append_bit(name="zebra", description="", default_value="0")
    register_b.append_bit(name="foo", description="", default_value="0")

    assert repr(register_a) != repr(register_b)


def test_bits_are_appended_properly_and_can_be_edited_in_place():
    register = Register(name="apa", index=0, mode="r", description="")

    bit_hest = register.append_bit(name="hest", description="abc", default_value="0")
    assert bit_hest.base_index == 0

    bit_zebra = register.append_bit(name="zebra", description="def", default_value="0")
    assert bit_zebra.base_index == 1

    bit_hest.description = "new desc"
    assert register.fields[0].description == "new desc"


def test_bit_vectors_are_appended_properly_and_can_be_edited_in_place():
    register = Register(name="apa", index=0, mode="r", description="")

    bit_vector_hest = register.append_bit_vector(
        name="hest", description="abc", width=3, default_value="000"
    )
    assert bit_vector_hest.base_index == 0

    bit_vector_zebra = register.append_bit_vector(
        name="zebra", description="def", width=5, default_value="00000"
    )
    assert bit_vector_zebra.base_index == 3

    bit_vector_hest.description = "new desc"
    assert register.fields[0].description == "new desc"


def test_appending_bit_to_full_register():
    register = Register(name="apa", index=0, mode="r", description="")
    register.append_bit_vector(name="foo", width=32, description="", default_value="0" * 32)

    with pytest.raises(ValueError) as exception_info:
        register.append_bit(name="bar", description="", default_value="0")
    assert str(exception_info.value).startswith('Maximum width exceeded for register "apa"')


def test_appending_bit_vector_to_full_register():
    register = Register(name="apa", index=0, mode="r", description="")
    register.append_bit_vector(name="foo", width=30, description="", default_value="0" * 30)

    with pytest.raises(ValueError) as exception_info:
        register.append_bit_vector(name="bar", description="", width=3, default_value="000")
    assert str(exception_info.value).startswith('Maximum width exceeded for register "apa"')


def test_default_value():
    register = Register(name="apa", index=0, mode="r", description="")
    register.append_bit(name="foo", description="", default_value="1")
    register.append_bit(name="foo", description="", default_value="0")
    register.append_bit(name="foo", description="", default_value="1")
    register.append_bit_vector(name="foo", description="", width=4, default_value="0110")
    register.append_bit_vector(name="foo", description="", width=4, default_value="0101")

    assert register.default_value == 1 * 2 ** 0 + 1 * 2 ** 2 + 6 * 2 ** 3 + 5 * 2 ** 7


def test_default_value_can_be_updated():
    register = Register(name="apa", index=0, mode="r", description="")
    register.append_bit(name="foo", description="", default_value="1")

    assert register.default_value == 1

    register.fields[0].default_value = "0"
    assert register.default_value == 0


def test_get_field():
    register = Register(name="apa", index=0, mode="r", description="")
    hest = register.append_bit(name="hest", description="", default_value="1")
    zebra = register.append_bit(name="zebra", description="", default_value="1")

    assert register.get_field("hest") is hest
    assert register.get_field("zebra") is zebra

    with pytest.raises(ValueError) as exception_info:
        assert register.get_field("non existing") is None
    assert str(exception_info.value) == 'Could not find field "non existing" within register "apa"'
