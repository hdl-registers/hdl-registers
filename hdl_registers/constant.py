# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------


class Constant:
    def __init__(self, name, value, description=None):
        """
        Arguments:
            name (str): The name of the constant.
            length (int): The constant value (signed).
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
