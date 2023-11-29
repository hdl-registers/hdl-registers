# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
import pytest

# First party libraries
from hdl_registers.generator.html.html_translator import HtmlTranslator


@pytest.fixture
def html_translator():
    return HtmlTranslator()


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_markdown_parser_can_handle_annotating_sentences(html_translator):
    expected = "This sentence <strong>should have a large portion</strong> in bold face"
    text = r"This sentence **should have a large portion** in bold face"
    assert expected in html_translator.translate(text)

    expected = "This sentence <em>should have a large portion</em> in italics"
    text = "This sentence *should have a large portion* in italics"
    assert expected in html_translator.translate(text)


def test_markdown_parser_can_handle_escaped_asterisks(html_translator):
    expected = "Part of this sentence **should be surrounded** by double asterisks"
    text = r"Part of this sentence \*\*should be surrounded\*\* by double asterisks"
    assert expected in html_translator.translate(text)

    expected = "Part of this sentence *should be surrounded* by asterisks"
    text = r"Part of this sentence \*should be surrounded\* by asterisks"
    assert expected in html_translator.translate(text)

    expected = "Part of this sentence <em>*should be in italics and surrounded*</em> by asterisks"
    text = r"Part of this sentence *\*should be in italics and surrounded\** by asterisks"
    assert expected in html_translator.translate(text)

    expected = "Part of this sentence *<em>should be in italics and surrounded</em>* by asterisks"
    text = r"Part of this sentence \**should be in italics and surrounded*\* by asterisks"
    assert expected in html_translator.translate(text)

    expected = "Part of this sentence should have an <em>*</em> in italics"
    text = r"Part of this sentence should have an *\** in italics"
    assert expected in html_translator.translate(text)


def test_line_breaks(html_translator):
    expected = "Two empty lines<br />\n<br />\nbetween paragraphs."
    text = "Two empty lines\n\nbetween paragraphs."
    assert expected in html_translator.translate(text)

    expected = "Three empty lines<br />\n<br />\nbetween paragraphs."
    text = "Three empty lines\n\n\nbetween paragraphs."
    assert expected in html_translator.translate(text)

    expected = r"Escaped \n\n\n should not result in paragraph break."
    text = r"Escaped \n\n\n should not result in paragraph break."
    assert expected in html_translator.translate(text)

    expected = "One empty line means same paragraph."
    text = "One empty line\nmeans same paragraph."
    assert expected in html_translator.translate(text)


def test_literal_underscore_can_be_used(html_translator):
    # We do not translate underscores, unlike some markdown
    expected = "This sentence <strong>contains_underscores</strong> in some_places"
    text = r"This sentence **contains_underscores** in some_places"
    assert expected in html_translator.translate(text)


def test_angle_brackets_should_be_translated_to_html(html_translator):
    expected = "This string &lt;&lt; contains &gt; brackets &gt;&lt;"
    text = "This string << contains > brackets ><"
    assert expected in html_translator.translate(text)
