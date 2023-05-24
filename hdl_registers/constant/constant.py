# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from abc import ABC, abstractmethod
from enum import IntEnum, auto


class Constant(ABC):

    """
    Meta class for all register constants (integer, boolean, ...).
    Lists a few properties that must be available.
    """

    name: str
    description: str

    @property
    @abstractmethod
    def value(self):
        """
        The value of the constant. Return type depends on the child class.
        """


class StringConstantDataType(IntEnum):
    """
    The data types that are supported for constants where the value is of type string.

    We use pylint disable since Python constants shall usually be upper case.
    In this case we want the enum key to exactly match the data type name, which we want as
    lower case for readability in TOML.
    """

    string = auto()  # pylint: disable=invalid-name
    unsigned = auto()  # pylint: disable=invalid-name
