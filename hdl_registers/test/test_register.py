# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
import pytest

# First party libraries
from hdl_registers.register import Register
from hdl_registers.register_modes import REGISTER_MODES


def test_repr_basic():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(Register(name="apa", index=0, mode=REGISTER_MODES["r"], description=""))

    # Different name
    assert repr(Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")) != repr(
        Register(name="hest", index=0, mode=REGISTER_MODES["r"], description="")
    )

    # Different index
    assert repr(Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")) != repr(
        Register(name="apa", index=1, mode=REGISTER_MODES["r"], description="")
    )

    # Different mode
    assert repr(Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")) != repr(
        Register(name="apa", index=0, mode=REGISTER_MODES["w"], description="")
    )

    # Different description
    assert repr(
        Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="Blah")
    ) != repr(Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="Gah"))


def test_repr_with_bits_appended():
    """
    Shows that the ``fields`` impact the repr. Do not need to test with other fields than bits.
    """
    register_a = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register_a.append_bit(name="hest", description="", default_value="0")

    register_b = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register_b.append_bit(name="hest", description="", default_value="0")

    assert repr(register_a) == repr(register_b)

    register_a.append_bit(name="zebra", description="", default_value="0")
    register_b.append_bit(name="foo", description="", default_value="0")

    assert repr(register_a) != repr(register_b)


def test_bits_are_appended_properly_and_can_be_edited_in_place():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")

    bit_hest = register.append_bit(name="hest", description="abc", default_value="0")
    assert bit_hest.base_index == 0

    bit_zebra = register.append_bit(name="zebra", description="def", default_value="0")
    assert bit_zebra.base_index == 1

    bit_hest.description = "new desc"
    assert register.fields[0].description == "new desc"


def test_bit_vectors_are_appended_properly_and_can_be_edited_in_place():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")

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


def test_integers_are_appended_properly_and_can_be_edited_in_place():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")

    integer_hest = register.append_integer(
        name="hest",
        description="",
        min_value=0,
        max_value=10,
        default_value=0,
    )
    assert integer_hest.base_index == 0

    integer_zebra = register.append_integer(
        name="zebra",
        description="",
        min_value=0,
        max_value=20,
        default_value=0,
    )
    assert integer_zebra.base_index == 4

    integer_hest.description = "new desc"
    assert register.fields[0].description == "new desc"


def test_appending_bit_to_full_register():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit_vector(name="foo", width=32, description="", default_value="0" * 32)

    with pytest.raises(ValueError) as exception_info:
        register.append_bit(name="bar", description="", default_value="0")
    assert str(exception_info.value) == 'Maximum width exceeded for register "apa".'


def test_appending_bit_vector_to_full_register():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit_vector(name="foo", width=30, description="", default_value="0" * 30)

    with pytest.raises(ValueError) as exception_info:
        register.append_bit_vector(name="bar", description="", width=3, default_value="000")
    assert str(exception_info.value) == 'Maximum width exceeded for register "apa".'


def test_appending_integer_to_full_register():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit_vector(name="foo", width=30, description="", default_value="0" * 30)

    with pytest.raises(ValueError) as exception_info:
        register.append_integer(
            name="zebra",
            description="",
            min_value=0,
            max_value=4,
            default_value=0,
        )
    assert str(exception_info.value) == 'Maximum width exceeded for register "apa".'


def test_default_value():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit(name="foo", description="", default_value="1")
    register.append_bit(name="foo", description="", default_value="0")
    register.append_bit(name="foo", description="", default_value="1")
    register.append_bit_vector(name="foo", description="", width=4, default_value="0110")
    register.append_bit_vector(name="foo", description="", width=4, default_value="0101")

    assert register.default_value == 1 * 2**0 + 1 * 2**2 + 6 * 2**3 + 5 * 2**7


def test_default_value_can_be_updated():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    register.append_bit(name="foo", description="", default_value="1")

    assert register.default_value == 1

    register.fields[0].default_value = "0"
    assert register.default_value == 0


def test_get_field():
    register = Register(name="apa", index=0, mode=REGISTER_MODES["r"], description="")
    hest = register.append_bit(name="hest", description="", default_value="1")
    zebra = register.append_bit(name="zebra", description="", default_value="1")

    assert register.get_field("hest") is hest
    assert register.get_field("zebra") is zebra

    with pytest.raises(ValueError) as exception_info:
        assert register.get_field("non existing") is None
    assert str(exception_info.value) == 'Could not find field "non existing" within register "apa"'
