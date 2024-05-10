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
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers import HDL_REGISTERS_TESTS
from hdl_registers.generator.html.constant_table import HtmlConstantTableGenerator
from hdl_registers.generator.html.page import HtmlPageGenerator
from hdl_registers.generator.html.register_table import HtmlRegisterTableGenerator
from hdl_registers.parser.toml import from_toml


class HtmlTest:
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path
        self.register_list = from_toml(
            name="caesar", toml_file=HDL_REGISTERS_TESTS / "regs_test.toml"
        )

    def create_html_page(self):
        html = read_file(HtmlPageGenerator(self.register_list, self.tmp_path).create())
        return html

    @staticmethod
    # pylint: disable=too-many-arguments
    def check_register(name, index, address, mode, default_value, description, html):
        expected = f"""
  <tr>
    <td><strong>{name}</strong></td>
    <td>{index}</td>
    <td>{address}</td>
    <td>{mode}</td>
    <td>{default_value}</td>
    <td>{description}</td>
  </tr>
"""
        assert expected in html, f"{expected}\n\n{html}"

    @staticmethod
    def check_field(name, index, default_value, html, description=None):
        expected = f"""
  <tr>
    <td>&nbsp;&nbsp;<em>{name}</em></td>
    <td>&nbsp;&nbsp;{index}</td>
    <td></td>
    <td></td>
    <td>{default_value}</td>
"""
        if description:
            expected += f"""\
    <td>
      {description}
    </td>
"""

        assert expected in html, f"{expected}\n\n{html}"

    @staticmethod
    def check_register_array(name, length, iterator_range, description, html):
        expected = f"""
  <tr>
    <td class="array_header" colspan=5>
      Register array <strong>{name}</strong>, repeated {length} times.
      Iterator <i>{iterator_range}.</i>
    </td>
    <td class="array_header">{description}</td>
  </tr>
"""
        assert expected in html, f"{expected}\n\n{html}"

    @staticmethod
    def check_constant(name, value, html):
        expected = f"""
  <tr>
    <td><strong>{name}</strong></td>
    <td>{value}</td>
"""
        assert expected in html, f"{expected}\n\n{html}"


@pytest.fixture
def html_test(tmp_path):
    return HtmlTest(tmp_path=tmp_path)


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_registers(html_test):
    """
    Test that all registers show up in the HTML with correct attributes.
    """
    html = html_test.create_html_page()

    html_test.check_register(
        name="config",
        index=0,
        address="0x0000",
        mode="Read, Write",
        default_value="0x14846",
        description="A plain <strong>dummy</strong> register.",
        html=html,
    )

    html_test.check_register_array(
        name="dummies",
        length=3,
        iterator_range="i &isin; [0, 2]",
        description="An <strong>array</strong> with some dummy regs",
        html=html,
    )

    html_test.check_register(
        name="first",
        index="7 + i &times; 2",
        address="0x001C + i &times; 0x0008",
        mode="Read, Write",
        default_value="0x5880",
        description="The first register in the array.",
        html=html,
    )

    html_test.check_register(
        name="second",
        index="8 + i &times; 2",
        address="0x0020 + i &times; 0x0008",
        mode="Read",
        default_value="0xC7",
        description="The second register in the array.",
        html=html,
    )


def test_register_fields(html_test):
    """
    Test that all bits show up in the HTML with correct attributes.
    """
    html = html_test.create_html_page()

    # Fields in plain register
    html_test.check_field(
        name="plain_bit_a",
        index="0",
        default_value="0b0",
        description="Bit A",
        html=html,
    )
    html_test.check_field(
        name="plain_bit_vector",
        index="4:1",
        default_value="0b0011",
        description="Bit <strong>vector</strong>",
        html=html,
    )
    html_test.check_field(
        name="plain_integer",
        index="12:5",
        default_value="66",
        html=html,
    )
    html_test.check_field(
        name="plain_enumeration",
        index="15:13",
        default_value="third",
        html=html,
    )
    html_test.check_field(
        name="plain_bit_b",
        index="16",
        default_value="0b1",
        description="Bit B",
        html=html,
    )

    # Fields in register array
    html_test.check_field(
        name="array_bit_a",
        index="7",
        default_value="0b1",
        description="Array register bit A",
        html=html,
    )
    html_test.check_field(
        name="array_bit_b",
        index="8",
        default_value="0b0",
        description="Array register bit B",
        html=html,
    )
    html_test.check_field(
        name="array_bit_vector",
        index="13:9",
        default_value="0b01100",
        description="Array register bit vector",
        html=html,
    )


def test_registers_and_constants(html_test):
    """
    Test that all constant show up in the HTML with correct attributes.
    Should only appear if there are actually any constants set.
    """
    constants_text = "The following constants are part of the register interface"

    html = html_test.create_html_page()

    # Check that registers are there
    assert "Registers" in html, html
    assert "dummies" in html, html

    # Check that constants are there
    assert constants_text in html, html
    html_test.check_constant(name="data_width", value=24, html=html)
    html_test.check_constant(name="decrement", value=-8, html=html)
    html_test.check_constant(name="enabled", value="True", html=html)
    html_test.check_constant(name="disabled", value="False", html=html)
    html_test.check_constant(name="rate", value="3.5", html=html)
    html_test.check_constant(name="paragraph", value='"hello there :)"', html=html)

    # Test again with no constants
    html_test.register_list.constants = []
    html = html_test.create_html_page()

    # Registers should still be there
    assert "Registers" in html, html
    assert "dummies" in html, html

    # But no constants
    assert constants_text not in html, html


def test_constants_and_no_registers(html_test):
    html_test.register_list.register_objects = []

    html = html_test.create_html_page()

    assert "This module does not have any registers" in html, html
    assert "dummies" not in html, html

    assert "<h2>Constants</h2>" in html, html
    html_test.check_constant(name="data_width", value=24, html=html)
    html_test.check_constant(name="decrement", value=-8, html=html)


def test_register_table_is_empty_string_if_no_registers_are_available(html_test):
    html_test.register_list.register_objects = []

    html = read_file(
        HtmlRegisterTableGenerator(html_test.register_list, html_test.tmp_path).create()
    )
    assert html == "", html


def test_constant_table_is_empty_string_if_no_constants_are_available(html_test):
    html_test.register_list.constants = []

    html = read_file(
        HtmlConstantTableGenerator(html_test.register_list, html_test.tmp_path).create()
    )
    assert html == "", html
