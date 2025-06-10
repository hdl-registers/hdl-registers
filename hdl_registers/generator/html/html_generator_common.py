# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from hdl_registers.generator.documentation_code_generator import DocumentationCodeGenerator


class HtmlGeneratorCommon(DocumentationCodeGenerator):
    """
    Common for HTML code generators.
    """

    COMMENT_START = "<!--"
    COMMENT_END = " -->"
