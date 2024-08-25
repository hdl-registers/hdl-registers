# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import TYPE_CHECKING, Optional

# Local folder libraries
from .field.bit import Bit
from .field.bit_vector import BitVector
from .field.enumeration import Enumeration
from .field.integer import Integer
from .register_mode import RegisterMode

if TYPE_CHECKING:
    # Local folder libraries
    from .field.numerical_interpretation import NumericalInterpretation
    from .field.register_field import RegisterField


class Register:
    """
    Used to represent a register and its fields.
    """

    def __init__(self, name: str, index: int, mode: "RegisterMode", description: str):
        """
        Arguments:
            name: The name of the register.
            index: The zero-based index of this register.
                If this register is part of a register array, the index shall be relative to the
                start of the array. I.e. the index is zero for the first register in the array.
                If the register is a plain register, the index shall be relative to the start of
                the register list.
            mode: A mode that decides the behavior of this register.
                See https://hdl-registers.com/rst/basic_feature/basic_feature_register_modes.html
                for more information about the different modes.
            description: Textual register description.
        """
        if not isinstance(mode, RegisterMode):
            # This check should be removed eventually.
            # It is only here to help users during the transition period.
            raise ValueError(
                f'Invalid mode: "{mode}". '
                "Since version 6.0.0, the mode should be a 'RegisterMode' object, not a string."
            )

        self.name = name
        self.index = index
        self.mode = mode
        self.description = description
        self.fields: list["RegisterField"] = []
        self.bit_index = 0

    def append_bit(self, name: str, description: str, default_value: str) -> Bit:
        """
        Append a bit field to this register.

        See :class:`.Bit` for documentation of the arguments.

        Return:
            The bit field object that was created.
        """
        bit = Bit(
            name=name, index=self.bit_index, description=description, default_value=default_value
        )
        self._append_field(field=bit)

        return bit

    def append_bit_vector(
        self,
        name: str,
        description: str,
        width: int,
        default_value: str,
        numerical_interpretation: Optional["NumericalInterpretation"] = None,
    ) -> BitVector:
        """
        Append a bit vector field to this register.

        See :class:`.BitVector` for documentation of the arguments.

        Return:
            The bit vector field object that was created.
        """
        bit_vector = BitVector(
            name=name,
            base_index=self.bit_index,
            description=description,
            width=width,
            default_value=default_value,
            numerical_interpretation=numerical_interpretation,
        )
        self._append_field(field=bit_vector)

        return bit_vector

    def append_enumeration(
        self, name: str, description: str, elements: dict[str, str], default_value: str
    ) -> Enumeration:
        """
        Append an enumeration field to this register.

        See :class:`.Enumeration` for documentation of the arguments.

        Return:
            The enumeration field object that was created.
        """
        field = Enumeration(
            name=name,
            base_index=self.bit_index,
            description=description,
            elements=elements,
            default_value=default_value,
        )
        self._append_field(field=field)

        return field

    def append_integer(
        self, name: str, description: str, min_value: int, max_value: int, default_value: int
    ) -> Integer:
        """
        Append an integer field to this register.

        See :class:`.Integer` for documentation of the arguments.

        Return:
            The integer field object that was created.
        """
        integer = Integer(
            name=name,
            base_index=self.bit_index,
            description=description,
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
        )
        self._append_field(field=integer)

        return integer

    def _append_field(self, field: "RegisterField") -> None:
        self.fields.append(field)

        self.bit_index += field.width
        if self.bit_index > 32:
            raise ValueError(f'Maximum width exceeded for register "{self.name}".')

    @property
    def default_value(self) -> int:
        """
        The default value of this register as an unsigned integer.
        Depends on the default values of the fields in this register.
        """
        default_value = 0
        for field in self.fields:
            default_value += field.default_value_uint * 2**field.base_index

        return default_value

    def get_field(self, name: str) -> "RegisterField":
        """
        Get the field within this register that has the given name. Will raise exception if no
        field matches.

        Arguments:
            name: The name of the field.

        Return:
            The field.
        """
        for field in self.fields:
            if field.name == name:
                return field

        raise ValueError(f'Could not find field "{name}" within register "{self.name}"')

    @property
    def address(self) -> int:
        """
        Byte address, within the register list, of this register.
        """
        return 4 * self.index

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
index={self.index},\
mode={self.mode},\
description={self.description},\
fields={','.join([repr(field) for field in self.fields])},\
)"""
