# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import copy
from pathlib import Path

# Third party libraries
import pytest

# First party libraries
from hdl_registers.register import Register
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


def test_from_default_registers():
    register_a = Register(name="a", index=0, mode=REGISTER_MODES["r"], description="AA")
    register_b = Register(name="b", index=1, mode=REGISTER_MODES["w"], description="BB")
    default_registers = [register_a, register_b]

    register_list = RegisterList.from_default_registers(
        name="apa", source_definition_file=None, default_registers=default_registers
    )

    # Change some things in the register objects to show that they are copied
    default_registers.append(
        Register(name="c", index=2, mode=REGISTER_MODES["r_w"], description="CC")
    )
    register_a.mode = REGISTER_MODES["w"]
    register_b.name = "x"

    print(register_list.get_register("a").mode)
    print(REGISTER_MODES["r"])

    assert len(register_list.register_objects) == 2
    assert register_list.get_register("a").mode == REGISTER_MODES["r"]
    assert register_list.get_register("b").name == "b"


def test_from_default_registers_with_bad_indexes_should_raise_exception():
    register_a = Register(name="a", index=0, mode=REGISTER_MODES["r"], description="")
    register_b = Register(name="b", index=0, mode=REGISTER_MODES["w"], description="")
    default_registers = [register_a, register_b]

    with pytest.raises(ValueError) as exception_info:
        RegisterList.from_default_registers(
            name="apa", source_definition_file=None, default_registers=default_registers
        )
    assert (
        str(exception_info.value)
        == 'Default register index mismatch for "b". Got "0", expected "1".'
    )


def test_header_constants():
    registers = RegisterList(name="apa", source_definition_file=None)
    hest = registers.add_constant("hest", 123, "")
    zebra = registers.add_constant("zebra", 456, "description")

    assert len(registers.constants) == 2

    assert registers.get_constant("hest") == hest
    assert registers.get_constant("zebra") == zebra

    with pytest.raises(ValueError) as exception_info:
        assert registers.get_constant("non existing") is None
    assert (
        str(exception_info.value)
        == 'Could not find constant "non existing" within register list "apa"'
    )

    zebra.value = -5
    assert registers.get_constant("zebra").value == -5


def test_registers_are_appended_properly_and_can_be_edited_in_place():
    register_array = RegisterList(name="apa", source_definition_file=Path("."))

    register_hest = register_array.append_register(
        name="hest", mode=REGISTER_MODES["r"], description=""
    )
    assert register_hest.index == 0

    register_zebra = register_array.append_register(
        name="zebra", mode=REGISTER_MODES["r"], description=""
    )
    assert register_zebra.index == 1

    register_hest.description = "new desc"
    assert register_array.register_objects[0].description == "new desc"


def test_register_arrays_are_appended_properly_and_can_be_edited_in_place():
    register_array = RegisterList(name="apa", source_definition_file=Path("."))

    register_array_hest = register_array.append_register_array(
        name="hest", length=4, description=""
    )
    assert register_array_hest.base_index == 0
    register_array_hest.append_register(name="foo", mode=REGISTER_MODES["r"], description="")
    register_array_hest.append_register(name="bar", mode=REGISTER_MODES["w"], description="")

    register_array_zebra = register_array.append_register_array(
        name="zebra", length=2, description=""
    )
    assert register_array_zebra.base_index == 8


def test_get_register():
    register_list = RegisterList(name="apa", source_definition_file=None)
    apa = register_list.append_register(name="apa", mode=REGISTER_MODES["r"], description="")
    hest = register_list.append_register(name="hest", mode=REGISTER_MODES["r"], description="")
    register_array = register_list.append_register_array(
        name="register_array", length=3, description=""
    )
    zebra = register_array.append_register(name="zebra", mode=REGISTER_MODES["r"], description="")

    assert register_list.get_register(register_name="apa") is apa
    assert register_list.get_register(register_name="hest") is hest

    with pytest.raises(ValueError) as exception_info:
        assert register_list.get_register(register_name="non existing") is None
    assert (
        str(exception_info.value)
        == 'Could not find register "non existing" within register list "apa"'
    )

    with pytest.raises(ValueError) as exception_info:
        register_list.get_register(register_name="register_array")
    assert (
        str(exception_info.value)
        == 'Could not find register "register_array" within register list "apa"'
    )
    register_list.get_register_array("register_array")

    with pytest.raises(ValueError) as exception_info:
        register_list.get_register(register_name="zebra")
    assert str(exception_info.value) == 'Could not find register "zebra" within register list "apa"'

    assert (
        register_list.get_register(register_name="zebra", register_array_name="register_array")
        is zebra
    )

    with pytest.raises(ValueError) as exception_info:
        register_list.get_register(register_name="hest", register_array_name="register_array")
    assert (
        str(exception_info.value)
        == 'Could not find register "hest" within register array "register_array"'
    )


def test_get_register_array():
    register_list = RegisterList(name="apa", source_definition_file=None)

    hest = register_list.append_register_array(name="hest", length=3, description="")
    hest.append_register(name="foo", mode=REGISTER_MODES["r"], description="")

    zebra = register_list.append_register_array(name="zebra", length=2, description="")
    zebra.append_register(name="bar", mode=REGISTER_MODES["r"], description="")

    register_list.append_register(name="register", mode=REGISTER_MODES["r"], description="")

    assert register_list.get_register_array("hest") is hest
    assert register_list.get_register_array("zebra") is zebra

    with pytest.raises(ValueError) as exception_info:
        register_list.get_register_array("non existing")
    assert (
        str(exception_info.value)
        == 'Could not find register array "non existing" within register list "apa"'
    )

    with pytest.raises(ValueError) as exception_info:
        register_list.get_register_array("register")
    assert (
        str(exception_info.value)
        == 'Could not find register array "register" within register list "apa"'
    )
    register_list.get_register("register")


def test_get_register_index():
    register_list = RegisterList(name=None, source_definition_file=None)

    register_list.append_register(name="apa", mode=REGISTER_MODES["r"], description="")
    register_list.append_register(name="hest", mode=REGISTER_MODES["r"], description="")

    zebra = register_list.append_register_array(name="zebra", length=2, description="")
    zebra.append_register(name="bar", mode=REGISTER_MODES["r"], description="")
    zebra.append_register(name="baz", mode=REGISTER_MODES["r"], description="")

    assert register_list.get_register_index(register_name="apa") == 0
    assert register_list.get_register_index(register_name="hest") == 1
    assert (
        register_list.get_register_index(
            register_name="bar", register_array_name="zebra", register_array_index=0
        )
        == 2
    )
    assert (
        register_list.get_register_index(
            register_name="baz", register_array_name="zebra", register_array_index=1
        )
        == 5
    )


def test_repr_basic():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(RegisterList(name="apa", source_definition_file=Path(".")))

    # Different name
    assert repr(RegisterList(name="apa", source_definition_file=Path("."))) != repr(
        RegisterList(name="hest", source_definition_file=Path("."))
    )

    # Different source_definition_file
    assert repr(RegisterList(name="apa", source_definition_file=Path("."))) != repr(
        RegisterList(name="apa", source_definition_file=Path("./zebra"))
    )


def test_repr_with_constant_added():
    register_list_a = RegisterList(name="apa", source_definition_file=Path("."))
    register_list_b = RegisterList(name="apa", source_definition_file=Path("."))
    assert repr(register_list_a) == repr(register_list_b)

    register_list_a.add_constant(name="zebra", value=3, description="")

    assert repr(register_list_a) != repr(register_list_b)


def test_repr_with_register_appended():
    register_list_a = RegisterList(name="apa", source_definition_file=Path("."))
    register_list_b = RegisterList(name="apa", source_definition_file=Path("."))
    assert repr(register_list_a) == repr(register_list_b)

    register_list_a.append_register(name="zebra", mode=REGISTER_MODES["w"], description="")

    assert repr(register_list_a) != repr(register_list_b)


def test_repr_with_register_array_appended():
    register_list_a = RegisterList(name="apa", source_definition_file=Path("."))
    register_list_b = RegisterList(name="apa", source_definition_file=Path("."))
    assert repr(register_list_a) == repr(register_list_b)

    register_list_a.append_register_array(name="zebra", length=4, description="")

    assert repr(register_list_a) != repr(register_list_b)


def test_deep_copy_of_register_list_actually_copies_everything():
    original_list = RegisterList("original", Path("/original_file.txt"))
    original_list.add_constant("original_constant", value=2, description="original constant")
    original_list.append_register(
        "original_register", REGISTER_MODES["w"], description="original register"
    )
    original_array = original_list.append_register_array("original_array", length=4, description="")
    original_array.append_register(
        name="original_register_in_array", mode=REGISTER_MODES["r"], description=""
    )

    copied_list = copy.deepcopy(original_list)

    assert copied_list.constants is not original_list.constants
    assert copied_list.constants[0] is not original_list.constants[0]

    copied_list.add_constant(name="new_constant", value=5, description="")
    assert len(copied_list.constants) == 2 and len(original_list.constants) == 1

    assert copied_list.register_objects is not original_list.register_objects
    assert copied_list.register_objects[0] is not original_list.register_objects[0]

    # Original register in position 0, original register array in position 1, new register in 2
    copied_list.append_register(name="new_register", mode=REGISTER_MODES["r"], description="")
    assert len(copied_list.register_objects) == 3 and len(original_list.register_objects) == 2

    assert copied_list.register_objects[1] is not original_list.register_objects[1]
    assert (
        copied_list.register_objects[1].registers is not original_list.register_objects[1].registers
    )
    assert (
        copied_list.register_objects[1].registers[0]
        is not original_list.register_objects[1].registers[0]
    )
    copied_list.register_objects[1].append_register(
        name="new_register_in_array", mode=REGISTER_MODES["r_w"], description=""
    )
    assert len(copied_list.register_objects[1].registers) == 2
    assert len(original_list.register_objects[1].registers) == 1
