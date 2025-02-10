# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Any


class Constant(ABC):
    """
    Meta class for all register constants (integer, boolean, ...).
    Lists a few properties that must be available.
    """

    name: str
    description: str

    @property
    @abstractmethod
    def value(self) -> Any:  # noqa: ANN401
        """
        The value of the constant. Return type depends on the subclass.
        """

    @value.setter
    @abstractmethod
    def value(self, value: Any) -> None:  # noqa: ANN401
        """
        Setter to update the constant value.
        Argument type depends on the subclass.
        Subclasses should perform sanity checks.
        """
