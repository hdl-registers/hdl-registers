# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from .bit import Bit
from .bit_vector import BitVector


class RegisterMode:
    def __init__(self, mode_readable, description):
        self.mode_readable = mode_readable
        self.description = description


REGISTER_MODES = dict(
    r=RegisterMode("Read", "Bus can read a value that fabric provides."),
    w=RegisterMode("Write", "Bus can write a value that is available for fabric usage."),
    r_w=RegisterMode(
        "Read, Write",
        "Bus can write a value and read it back. The written value is available for fabric usage.",
    ),
    wpulse=RegisterMode(
        "Write-pulse", "Bus can write a value that is asserted for one clock cycle in fabric."
    ),
    r_wpulse=RegisterMode(
        "Read, Write-pulse",
        "Bus can read a value that fabric provides. "
        "Bus can write a value that is asserted for one clock cycle in fabric.",
    ),
)


class Register:

    """
    Used to represent a register and its fields.
    """

    def __init__(self, name, index, mode, description):
        """
        Arguments:
            name (str): The name of the register.
            index (int): The zero-based index of this register.
                If this register is part of a register array, the index shall be relative to the
                start of the array. I.e. the index is zero for the first register in the array.
                If the register is a plain register, the index shall be relative to the start of
                the register list.
            mode (str): A valid register mode.
            description (str): Textual register description.
        """
        if mode not in REGISTER_MODES:
            raise ValueError(f'Invalid mode "{mode}" for register "{name}"')

        self.name = name
        self.index = index
        self.mode = mode
        self.description = description
        self.fields = []
        self.bit_index = 0

    def append_bit(self, name, description, default_value):
        """
        Append a bit field to this register.

        Arguments:
            name (str): The name of the bit.
            description (str): Description of the bit.
            default_value (str): Default value. Either "1" or "0".

        Return:
            :class:`.Bit`: The bit object that was created.
        """
        bit = Bit(
            name=name, index=self.bit_index, description=description, default_value=default_value
        )
        self.fields.append(bit)

        self.bit_index += bit.width
        if self.bit_index > 32:
            raise ValueError(f'Maximum width exceeded for register "{self.name}"')

        return bit

    def append_bit_vector(self, name, description, width, default_value):
        """
        Append a bit vector field to this register.

        Arguments:
            name (str): The name of the bit vector.
            width (int) : The width of the bit vector.
            description (str): Description of the bit vector.
            default_value (str): Default value as a string. Must be of length ``width`` and contain
                only "1" and "0".

        Return:
            :class:`.BitVector`: The bit vector object that was created.
        """
        bit_vector = BitVector(
            name=name,
            base_index=self.bit_index,
            description=description,
            width=width,
            default_value=default_value,
        )
        self.fields.append(bit_vector)

        self.bit_index += bit_vector.width
        if self.bit_index > 32:
            raise ValueError(f'Maximum width exceeded for register "{self.name}"')

        return bit_vector

    @property
    def default_value(self):
        """
        The default value of the register. Depends on the default values of it's fields.

        Returns:
            int: The default value.
        """
        default_value = 0
        for field in self.fields:
            default_value += field.default_value_uint * 2 ** field.base_index
        return default_value

    def get_field(self, name):
        """
        Get the field within this register that has the given name. Will raise exception if no
        field matches.

        Arguments:
            name (str): The name of the field.

        Returns:
            :class:`.RegisterField`: The field.
        """
        for field in self.fields:
            if field.name == name:
                return field

        raise ValueError(f'Could not find field "{name}" within register "{self.name}"')

    @property
    def address(self):
        """
        int: Byte address, within the register list, of this register.
        """
        return 4 * self.index

    @property
    def is_bus_readable(self):
        """
        True if the register is readable by bus. Based on the register type.
        """
        return self.mode in ["r", "r_w", "r_wpulse"]

    @property
    def is_bus_writeable(self):
        """
        True if the register is writeable by bus. Based on the register type.
        """
        return self.mode in ["w", "r_w", "wpulse", "r_wpulse"]

    def __repr__(self):
        return f"""{self.__class__.__name__}(\
name={self.name},\
index={self.index},\
mode={self.mode},\
description={self.description},\
default_value={self.default_value},\
fields={','.join([repr(field) for field in self.fields])},\
)"""
