# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register_field import RegisterField


class EnumerationElement:
    """
    Represent a single element, also known as a "member"/"enumerator"/"option"/"choice",
    within an enumeration type.

    Optionally we could use a python dataclass: https://docs.python.org/3/library/dataclasses.html
    Would get the __repr__ method for free, but also a lot of other stuff that we do not need.

    We could also use Python enum class: https://docs.python.org/3/library/enum.html
    Which would be a whole other concept.

    It is deemed more flexible to use a simple class for now.
    """

    def __init__(self, name: str, value: int, description: str):
        self._name = name
        self._value = value
        self.description = description

    @property
    def name(self) -> str:
        """
        Getter for ``name``.
        This member is read-only, since changing the name of an element poses some risks for
        the functionality of the enumeration field:

        * Could cause name collisions with other elements.
        * Could invalidate the currently selected default value of the field.
        """
        return self._name

    @property
    def value(self) -> int:
        """
        Getter for ``value``.
        This member is read-only, since changing the value of an element poses the risk of value
        collisions with other elements in the enumeration field.
        """
        return self._value

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
_name={self._name},\
_value={self._value},\
description={self.description},\
)"""


class Enumeration(RegisterField):
    """
    Used to represent an enumeration field in a register.
    """

    def __init__(
        self,
        name: str,
        base_index: int,
        description: str,
        elements: dict[str, str],
        default_value: str,
    ):
        """
        Arguments:
            name: The name of the register field.
            base_index: The zero-based index within the register for the lowest bit of this field.
            description: Textual field description.
            elements: Dictionary mapping element names to their description.
            default_value: The name of the element that shall be set as default.
        """
        self.name = name
        self._base_index = base_index
        self.description = description

        # The number of elements decides the width of the field.
        # Hence the user is not allowed to change the element set after initialization.
        self._elements = []

        if not elements:
            message = f'Enumeration "{self.name}", must have at least one element.'
            raise ValueError(message)

        # The enumeration values are sequentially incremented starting from zero.
        # This works because the 'value' field of the enumeration element is read-only.
        # Note that dictionaries in Python are guaranteed ordered since version 3.7.
        for element_index, (element_name, element_description) in enumerate(elements.items()):
            element = EnumerationElement(
                name=element_name, value=element_index, description=element_description
            )
            self._elements.append(element)

        self._default_value = self._elements[0]
        self.set_default_value(name=default_value)

        self._width = self._calculate_width()

    def _calculate_width(self) -> int:
        num_elements = len(self._elements)
        num_bits = (num_elements - 1).bit_length() if num_elements > 1 else 1

        return num_bits

    @property
    def elements(self) -> list[EnumerationElement]:
        """
        Getter for elements.
        """
        return self._elements

    def get_element_by_name(self, name: str) -> EnumerationElement:
        """
        Get an enumeration element by name.

        Arguments:
            name: The name of the element.

        Return:
            The enumeration element with the provided name.
        """
        for element in self._elements:
            if element.name == name:
                return element

        message = (
            f'Enumeration "{self.name}", requested element name does not exist. Got: "{name}".'
        )
        raise ValueError(message)

    def get_element_by_value(self, value: int) -> EnumerationElement:
        """
        Get an enumeration element by value.

        Arguments:
            value: The value of the element.

        Return:
            The enumeration element with the provided value.
        """
        for element in self._elements:
            if element.value == value:
                return element

        message = (
            f'Enumeration "{self.name}", requested element value does not exist. Got: "{value}".'
        )
        raise ValueError(message)

    @property  # type: ignore[override]
    def default_value(self) -> EnumerationElement:
        """
        Getter for ``default_value``.
        """
        return self._default_value

    def set_default_value(self, name: str) -> None:
        """
        Set the default value for this enumeration field.

        Arguments:
            value: The name of the enumeration element that shall be set as default.
        """
        self._default_value = self.get_element_by_name(name=name)

    @property
    def default_value_uint(self) -> int:
        return self.default_value.value

    def get_value(self, register_value: int) -> EnumerationElement:  # type: ignore[override]
        """
        See super method for details.
        This subclass method uses a different type to represent the field value, and also
        adds some sanity checks.
        """
        value_integer = super().get_value(register_value=register_value)
        return self.get_element_by_value(value=value_integer)

    def set_value(self, field_value: EnumerationElement) -> int:  # type: ignore[override]
        """
        See super method for details.
        This subclass method uses a different type to represent the field value.
        """
        return super().set_value(field_value=field_value.value)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
_base_index={self._base_index},\
description={self.description},\
_elements={self._elements},\
_default_value={self._default_value},\
)"""
