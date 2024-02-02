# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .register import Register


class RegisterArray:
    """
    Represent an array of registers.
    That is, a sequence of registers that shall be repeated a number of times in
    a :class:`.RegisterList`.
    """

    def __init__(self, name: str, base_index: int, length: int, description: str):
        """
        Arguments:
            name: The name of this register array.
            base_index: The zero-based index of the first register of this array in the
                register list.
            length: The number of times the register sequence shall be repeated.
            description: Textual register array description.
        """
        self.name = name
        self.base_index = base_index
        self.length = length
        self.description = description

        self.registers: list[Register] = []

    def append_register(self, name: str, mode: str, description: str) -> Register:
        """
        Append a register to this array.

        Arguments:
            name: The name of the register.
            mode: A valid register mode.
            description: Textual register description.

        Return:
            The register object that was created.
        """
        index = len(self.registers)
        register = Register(name=name, index=index, mode=mode, description=description)

        self.registers.append(register)
        return register

    def get_register(self, name: str) -> Register:
        """
        Get a register from this array. Will raise exception if no register matches.

        Arguments:
            name: The name of the register.
        Return:
            The register.
        """
        for register in self.registers:
            if register.name == name:
                return register

        raise ValueError(f'Could not find register "{name}" within register array "{self.name}"')

    @property
    def index(self) -> int:
        """
        Property exists to be used analogously with ``Register.index``.

        Return:
            The highest index occupied by this array.
        """
        return self.base_index + self.length * len(self.registers) - 1

    def get_start_index(self, array_index: int) -> int:
        """
        The index within the register list where array iteration number ``array_index`` starts.

        Arguments:
            array_index: The array iteration index.
                Must be less than the array ``length``.
        """
        if array_index >= self.length:
            raise ValueError(
                f'Index {array_index} out of range for register array "{self.name}" '
                f"of length {self.length}."
            )

        return self.base_index + array_index * len(self.registers)

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
base_index={self.base_index},\
length={self.length},\
description={self.description},\
registers={','.join([repr(register) for register in self.registers])},\
)"""
