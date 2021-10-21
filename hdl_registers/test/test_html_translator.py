# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import unittest

from tsfpga.registers.html_translator import HtmlTranslator


class TestTranslator(unittest.TestCase):
    def setUp(self):
        self.html_translator = HtmlTranslator()

    def test_markdown_parser_can_handle_annotating_sentences(self):
        expected = "This sentence <strong>should have a large portion</strong> in bold face"
        text = r"This sentence **should have a large portion** in bold face"
        assert expected in self.html_translator.translate(text)

        expected = "This sentence <em>should have a large portion</em> in italics"
        text = "This sentence *should have a large portion* in italics"
        assert expected in self.html_translator.translate(text)

    def test_markdown_parser_can_handle_escaped_asterisks(self):
        expected = "Part of this sentence **should be surrounded** by double asterisks"
        text = r"Part of this sentence \*\*should be surrounded\*\* by double asterisks"
        assert expected in self.html_translator.translate(text)

        expected = "Part of this sentence *should be surrounded* by asterisks"
        text = r"Part of this sentence \*should be surrounded\* by asterisks"
        assert expected in self.html_translator.translate(text)

        expected = (
            "Part of this sentence <em>*should be in italics and surrounded*</em> by asterisks"
        )
        text = r"Part of this sentence *\*should be in italics and surrounded\** by asterisks"
        assert expected in self.html_translator.translate(text)

        expected = (
            "Part of this sentence *<em>should be in italics and surrounded</em>* by asterisks"
        )
        text = r"Part of this sentence \**should be in italics and surrounded*\* by asterisks"
        assert expected in self.html_translator.translate(text)

        expected = "Part of this sentence should have an <em>*</em> in italics"
        text = r"Part of this sentence should have an *\** in italics"
        assert expected in self.html_translator.translate(text)

    def test_line_breaks(self):
        expected = "Two empty lines<br />\n<br />\nbetween paragraphs."
        text = "Two empty lines\n\nbetween paragraphs."
        assert expected in self.html_translator.translate(text)

        expected = "Three empty lines<br />\n<br />\nbetween paragraphs."
        text = "Three empty lines\n\n\nbetween paragraphs."
        assert expected in self.html_translator.translate(text)

        expected = r"Escaped \n\n\n should not result in paragraph break."
        text = r"Escaped \n\n\n should not result in paragraph break."
        assert expected in self.html_translator.translate(text)

        expected = "One empty line means same paragraph."
        text = "One empty line\nmeans same paragraph."
        assert expected in self.html_translator.translate(text)

    def test_literal_underscore_can_be_used(self):
        # We do not translate underscores, unlike some markdown
        expected = "This sentence <strong>contains_underscores</strong> in some_places"
        text = r"This sentence **contains_underscores** in some_places"
        assert expected in self.html_translator.translate(text)

    def test_angle_brackets_should_be_translated_to_html(self):
        expected = "This string &lt;&lt; contains &gt; brackets &gt;&lt;"
        text = "This string << contains > brackets ><"
        assert expected in self.html_translator.translate(text)
