# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator


class HtmlGeneratorCommon(RegisterCodeGenerator):
    """
    Common for HTML code generators.
    """

    COMMENT_START = "<!--"
    COMMENT_END = " -->"
