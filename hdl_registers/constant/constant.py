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
