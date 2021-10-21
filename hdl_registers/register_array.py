# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from .register import Register


class RegisterArray:

    """
    Represent an array of registers. That is, a sequence of registers that shall be repeated a
    number of times in a register list.
    """

    def __init__(self, name, base_index, length, description):
        """
        Arguments:
            name (str): The name of this register array.
            base_index (int): The zero-based index of the first register of this array in
                the register list.
            length (int): The number of times the register sequence shall be repeated.
            description (str): Textual register array description.
        """
        self.name = name
        self.base_index = base_index
        self.length = length
        self.description = description

        self.registers = []

    def append_register(self, name, mode, description):
        """
        Append a register to this array.

        Arguments:
            name (str): The name of the register.
            mode (str): A valid register mode.
            description (str): Textual register description.

        Return:
            :class:`.Register`: The register object that was created.
        """
        index = len(self.registers)
        register = Register(name, index, mode, description)

        self.registers.append(register)
        return register

    def get_register(self, name):
        """
        Get a register from this array. Will raise exception if no register matches.

        Arguments:
            name (str): The name of the register.
        Return:
            :class:`.Register`: The register.
        """
        for register in self.registers:
            if register.name == name:
                return register

        raise ValueError(f'Could not find register "{name}" within register array "{self.name}"')

    @property
    def index(self):
        """
        Property exists to be used analogously with ``Register.index``.

        Return:
            int: The highest index occupied by this array.
        """
        return self.base_index + self.length * len(self.registers) - 1

    def get_start_index(self, array_index):
        """
        The index within the register list where array iteration number ``array_index`` starts.

        Arguments:
            array_index (int): The array iteration index.
                Shall be less than or equal to the array ``length``.
        """
        if array_index >= self.length:
            raise ValueError(
                f'Index {array_index} out of range for register array "{self.name}" '
                f"of length {self.length}."
            )

        return self.base_index + array_index * len(self.registers)

    def __repr__(self):
        return f"""{self.__class__.__name__}(\
name={self.name},\
base_index={self.base_index},\
length={self.length},\
description={self.description},\
registers={','.join([repr(register) for register in self.registers])},\
)"""
