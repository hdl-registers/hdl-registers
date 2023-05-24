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

    type: "ConstantType"
    name: str
    description: str

    @property
    @abstractmethod
    def value(self):
        """
        The value of the constant. Return type depends on the child class.
        """


class ConstantType(IntEnum):
    BOOLEAN = auto()
    FLOAT = auto()
    INTEGER = auto()
    STRING = auto()
    ERROR_NO_TYPE_AVAILABLE = auto()


def get_constant_type(value):
    """
    TODO
    """
    if isinstance(value, int):
        if isinstance(value, bool):
            return ConstantType.BOOLEAN

        return ConstantType.INTEGER

    if isinstance(value, float):
        return ConstantType.FLOAT

    if isinstance(value, str):
        return ConstantType.STRING

    return ConstantType.ERROR_NO_TYPE_AVAILABLE
