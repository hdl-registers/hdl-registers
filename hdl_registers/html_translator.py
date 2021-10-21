# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import re


class HtmlTranslator:

    r"""
    Translate a raw text with markdown/rst annotations into HTML code.

    Supports:

    * Strong: **double asterisks**
    * Emphasis: *single asterisks*

    Literal asterisks should be escaped: \*
    """

    _not_escaped = r"(?<!\\)"
    _double_asterisks = r"\*\*"
    _single_asterisk = r"\*"
    _match_text = r"(.*?)"

    # These patterns match asterisks only if they are not preceded by \escape
    _re_strong_pattern = re.compile(
        _not_escaped + _double_asterisks + _match_text + _not_escaped + _double_asterisks
    )
    _re_emphasis_pattern = re.compile(
        _not_escaped + _single_asterisk + _match_text + _not_escaped + _single_asterisk
    )

    # This pattern matches escaped asterisks
    _re_escaped_literal_pattern = re.compile(r"\\(\*)")

    # Consecutive newlines is a paragraph separator
    _re_paragraph_separator = re.compile(r"\n{2,}")

    def translate(self, text):
        """
        Translate the text to have HTML tags where appropriate.
        """
        result = self._translate_angle_brackets(text)
        result = self._annotate(result)
        result = self._insert_line_breaks(result)
        return result

    def _annotate(self, text):
        """
        Replace markdown/rst syntax with HTML tags.
        """
        result = re.sub(self._re_strong_pattern, r"<strong>\g<1></strong>", text)
        result = re.sub(self._re_emphasis_pattern, r"<em>\g<1></em>", result)
        # Remove the escape sign
        result = re.sub(self._re_escaped_literal_pattern, r"\g<1>", result)
        return result

    def _insert_line_breaks(self, text):
        """
        Insert HTML line break tag instead of consecutive newlines.
        """
        # Two line breaks to get new paragraph.
        result = re.sub(self._re_paragraph_separator, "<br /><br />", text)
        # A single newline in Markdown should be a space
        result = result.replace("\n", " ")
        # Split to get nicer HTML file formatting
        result = result.replace("<br />", "<br />\n")
        return result

    @staticmethod
    def _translate_angle_brackets(text):
        """
        The HTML may not contain raw angle brackets ("<", ">") since they will be interpreted as
        HTML tags by the web browse.
        """
        result = text.replace("<", "&lt;")
        result = result.replace(">", "&gt;")
        return result
