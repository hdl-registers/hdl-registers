# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from docutils.core import publish_parts
from docutils.writers.html5_polyglot import Writer


class HtmlTranslator:
    """
    Translate a raw text with RST annotations into HTML code.
    """

    def translate(self, text: str) -> str:
        """
        Translate the text to have HTML tags where appropriate.
        """
        return publish_parts(source=text, writer=Writer())["fragment"].strip()
