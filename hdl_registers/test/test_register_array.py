# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import pytest

from tsfpga.registers.register_array import RegisterArray


def test_registers_are_appended_properly_and_can_be_edited_in_place():
    register_array = RegisterArray(name="apa", base_index=0, length=4, description="")

    register_hest = register_array.append_register(name="hest", mode="r", description="")
    assert register_hest.index == 0

    register_zebra = register_array.append_register(name="zebra", mode="r", description="")
    assert register_zebra.index == 1

    register_hest.description = "new desc"
    assert register_array.registers[0].description == "new desc"


def test_get_register():
    register_array = RegisterArray(name="apa", base_index=0, length=3, description="")
    hest = register_array.append_register(name="hest", mode="w", description="")
    zebra = register_array.append_register(name="zebra", mode="r", description="")

    assert register_array.get_register("hest") is hest
    assert register_array.get_register("zebra") is zebra

    with pytest.raises(ValueError) as exception_info:
        assert register_array.get_register("non existing") is None
    assert (
        str(exception_info.value)
        == 'Could not find register "non existing" within register array "apa"'
    )


def test_repr_basic():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(RegisterArray(name="apa", base_index=0, length=4, description=""))

    # Different name
    assert repr(RegisterArray(name="apa", base_index=0, length=4, description="")) != repr(
        RegisterArray(name="hest", base_index=0, length=4, description="")
    )

    # Different base_index
    assert repr(RegisterArray(name="apa", base_index=0, length=4, description="")) != repr(
        RegisterArray(name="apa", base_index=8, length=4, description="")
    )

    # Different length
    assert repr(RegisterArray(name="apa", base_index=0, length=4, description="")) != repr(
        RegisterArray(name="apa", base_index=0, length=8, description="")
    )

    # Different description
    assert repr(RegisterArray(name="apa", base_index=0, length=4, description="hest")) != repr(
        RegisterArray(name="apa", base_index=0, length=4, description="zebra")
    )


def test_repr_with_registers_appended():
    register_array_a = RegisterArray(name="apa", base_index=0, length=4, description="")
    register_array_a.append_register(name="hest", mode="r", description="")

    register_array_b = RegisterArray(name="apa", base_index=0, length=4, description="")
    register_array_b.append_register(name="hest", mode="r", description="")

    assert repr(register_array_a) == repr(register_array_b)

    register_array_a.append_register(name="zebra", mode="w", description="")
    register_array_b.append_register(name="zebra", mode="r_w", description="")

    assert repr(register_array_a) != repr(register_array_b)


def test_index():
    register_array = RegisterArray(name="apa", base_index=0, length=4, description="")
    register_array.append_register(name="hest", mode="r", description="")
    assert register_array.index == 3

    register_array.length = 5
    assert register_array.index == 4

    register_array.append_register(name="zebra", mode="r", description="")
    assert register_array.index == 9


def test_start_index():
    register_array = RegisterArray(name="apa", base_index=10, length=4, description="")
    register_array.append_register(name="hest", mode="r", description="")
    assert register_array.get_start_index(0) == 10
    assert register_array.get_start_index(1) == 11
    assert register_array.get_start_index(2) == 12

    register_array.append_register(name="zebra", mode="r", description="")
    assert register_array.get_start_index(0) == 10
    assert register_array.get_start_index(1) == 12
    assert register_array.get_start_index(2) == 14


def test_start_index_with_argument_outside_of_length_should_raise_exception():
    register_array = RegisterArray(name="apa", base_index=0, length=4, description="")
    register_array.append_register(name="hest", mode="r", description="")

    with pytest.raises(ValueError) as exception_info:
        register_array.get_start_index(4)
    assert str(exception_info.value) == 'Index 4 out of range for register array "apa" of length 4.'
