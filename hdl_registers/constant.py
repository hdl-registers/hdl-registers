# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to be run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------


class Constant:
    def __init__(self, name, value, description=None):
        """
        Arguments:
            name (str): The name of the constant.
            value (int): The constant value (signed).
            description (str): Textual description for the constant.
        """
        self.name = name
        self.value = value
        self.description = "" if description is None else description

    def __repr__(self):
        return f"""{self.__class__.__name__}(\
name={self.name},\
value={self.value},\
description={self.description},
)"""
