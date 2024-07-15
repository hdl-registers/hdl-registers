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
from hdl_registers.field.enumeration import Enumeration, EnumerationElement


def test_enumeration_element():
    enumeration_element = EnumerationElement(name="apa", value=3, description="hest")

    assert enumeration_element.name == "apa"
    assert enumeration_element.value == 3
    assert enumeration_element.description == "hest"

    assert repr(enumeration_element) == "EnumerationElement(_name=apa,_value=3,description=hest,)"


def test_enumeration_basics():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="hest",
        elements={
            "element0": "desc0",
            "element1": "desc1",
            "element2": "desc2",
            "element3": "desc3",
            "element4": "desc4",
        },
        default_value="element2",
    )

    assert enumeration.name == "apa"
    assert enumeration.base_index == 3
    assert enumeration.description == "hest"

    for idx, element in enumerate(enumeration.elements):
        assert element.name == f"element{idx}"
        assert element.value == idx
        assert element.description == f"desc{idx}"

    assert enumeration.width == 3

    assert enumeration.default_value is enumeration.elements[2]
    assert enumeration.default_value_uint == 2


def test_no_elements_should_raise_exception():
    with pytest.raises(ValueError) as exception_info:
        Enumeration(
            name="apa",
            base_index=3,
            description="",
            elements=dict(),
            default_value="element0",
        )
    assert str(exception_info.value) == 'Enumeration "apa", must have at least one element.'


def test_get_element_by_name():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="",
        elements={"element0": "", "element1": ""},
        default_value="element0",
    )

    assert enumeration.get_element_by_name("element0") is enumeration.elements[0]
    assert enumeration.get_element_by_name("element1") is enumeration.elements[1]


def test_get_element_by_name_with_invalid_name_should_raise_exception():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="",
        elements={"element0": ""},
        default_value="element0",
    )

    with pytest.raises(ValueError) as exception_info:
        enumeration.get_element_by_name("element1")
    assert (
        str(exception_info.value)
        == 'Enumeration "apa", requested element name does not exist. Got: "element1".'
    )


def test_get_element_by_value():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="",
        elements={"element0": "", "element1": ""},
        default_value="element0",
    )

    assert enumeration.get_element_by_value(0) is enumeration.elements[0]
    assert enumeration.get_element_by_value(1) is enumeration.elements[1]


def test_get_element_by_value_with_invalid_value_should_raise_exception():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="",
        elements={"element0": ""},
        default_value="element0",
    )

    with pytest.raises(ValueError) as exception_info:
        enumeration.get_element_by_value(1)
    assert (
        str(exception_info.value)
        == 'Enumeration "apa", requested element value does not exist. Got: "1".'
    )


def test_setting_default_value():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="",
        elements={"element0": "", "element1": ""},
        default_value="element0",
    )
    assert enumeration.default_value is enumeration.elements[0]

    enumeration.set_default_value("element1")
    assert enumeration.default_value is enumeration.elements[1]


def test_setting_default_value_that_does_not_exist_should_raise_exception():
    # Invalid value to constructor.
    with pytest.raises(ValueError) as exception_info:
        Enumeration(
            name="apa",
            base_index=3,
            description="",
            elements={"element0": ""},
            default_value="element1",
        )
    assert (
        str(exception_info.value)
    ) == 'Enumeration "apa", requested element name does not exist. Got: "element1".'

    # Valid value to constructor but then an invalid update of the value.
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="",
        elements={"element0": ""},
        default_value="element0",
    )
    with pytest.raises(ValueError) as exception_info:
        enumeration.set_default_value("element1")
    assert (
        str(exception_info.value)
    ) == 'Enumeration "apa", requested element name does not exist. Got: "element1".'


def test_get_value():
    base_index = 3

    enumeration = Enumeration(
        name="apa",
        base_index=base_index,
        description="",
        elements={
            "element0": "",
            "element1": "",
            "element2": "",
        },
        default_value="element0",
    )

    assert enumeration.width == 2

    # Ones outside of this field. Should be masked out when getting value.
    register_base_value = 0b111_00_111

    register_value = register_base_value
    assert enumeration.get_value(register_value=register_value) is enumeration.elements[0]

    register_value = register_base_value + (1 << base_index)
    assert enumeration.get_value(register_value=register_value) is enumeration.elements[1]

    register_value = register_base_value + (2 << base_index)
    assert enumeration.get_value(register_value=register_value) is enumeration.elements[2]

    register_value = register_base_value + (3 << base_index)
    with pytest.raises(ValueError) as exception_info:
        enumeration.get_value(register_value=register_value)
    assert (
        str(exception_info.value)
        == 'Enumeration "apa", requested element value does not exist. Got: "3".'
    )


def test_set_value():
    base_index = 4

    enumeration = Enumeration(
        name="apa",
        base_index=base_index,
        description="",
        elements={
            "element0": "",
            "element1": "",
            "element2": "",
        },
        default_value="element0",
    )

    assert enumeration.width == 2

    assert enumeration.set_value(field_value=enumeration.elements[0]) == 0
    assert enumeration.set_value(field_value=enumeration.elements[1]) == 1 << base_index
    assert enumeration.set_value(field_value=enumeration.elements[2]) == 2 << base_index


def test_repr():
    enumeration = Enumeration(
        name="apa",
        base_index=3,
        description="hest",
        elements={"element0": "element0 description"},
        default_value="element0",
    )
    element = "EnumerationElement(_name=element0,_value=0,description=element0 description,)"
    assert repr(enumeration) == (
        "Enumeration(name=apa,_base_index=3,description=hest,"
        f"_elements=[{element}],"
        f"_default_value={element},)"
    )
