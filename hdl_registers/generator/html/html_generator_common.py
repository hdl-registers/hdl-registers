# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator


class HtmlGeneratorCommon(RegisterCodeGenerator):
    """
    Common for HTML code generators.
    """

    COMMENT_START = "<!--"
    COMMENT_END = " -->"
