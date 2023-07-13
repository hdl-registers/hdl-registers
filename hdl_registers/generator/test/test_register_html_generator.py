# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import unittest

# Third party libraries
import pytest
from tsfpga.system_utils import read_file

# First party libraries
from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.parser import from_toml


@pytest.mark.usefixtures("fixture_tmp_path")
class TestRegisterHtmlGenerator(unittest.TestCase):
    tmp_path = None

    def setUp(self):
        toml_file = HDL_REGISTERS_TEST / "regs_test.toml"
        self.registers = from_toml("test", toml_file)

    def test_registers(self):
        """
        Test that all registers show up in the HTML with correct attributes.
        """
        html = self._create_html_page()

        self._check_register(
            name="plain_dummy_reg",
            index=0,
            address="0x0000",
            mode="Read, Write",
            default_value="0xE",
            description="A plain <strong>dummy</strong> register.",
            html=html,
        )

        self._check_register_array(
            name="dummy_regs",
            length=3,
            iterator_range="i &isin; [0, 2]",
            description="An <strong>array</strong> with some dummy regs",
            html=html,
        )

        self._check_register(
            name="array_dummy_reg",
            index="5 + i &times; 2",
            address="0x0014 + i &times; 0x0008",
            mode="Read, Write",
            default_value="0x31",
            description="The first register in the array.",
            html=html,
        )

        self._check_register(
            name="second_array_dummy_reg",
            index="6 + i &times; 2",
            address="0x0018 + i &times; 0x0008",
            mode="Read",
            default_value="0x0",
            description="The second register in the array.",
            html=html,
        )

    def test_register_fields(self):
        """
        Test that all bits show up in the HTML with correct attributes.
        """
        html = self._create_html_page()

        # Fields in plain register
        self._check_field(
            name="plain_bit_a",
            index="0",
            default_value="0b0",
            description="Bit A",
            html=html,
        )
        self._check_field(
            name="plain_bit_b",
            index="1",
            default_value="0b1",
            description="Bit B",
            html=html,
        )
        self._check_field(
            name="plain_bit_vector",
            index="5:2",
            default_value="0b0011",
            description="Bit <strong>vector</strong>",
            html=html,
        )

        # Fields in register array
        self._check_field(
            name="array_bit_a",
            index="0",
            default_value="0b1",
            description="Array register bit A",
            html=html,
        )
        self._check_field(
            name="array_bit_b",
            index="1",
            default_value="0b0",
            description="Array register bit B",
            html=html,
        )
        self._check_field(
            name="array_bit_vector",
            index="6:2",
            default_value="0b01100",
            description="Array register bit vector",
            html=html,
        )

    def test_registers_and_constants(self):
        """
        Test that all constant show up in the HTML with correct attributes.
        Should only appear if there are actually any constants set.
        """
        constants_text = "The following constants are part of the register interface"

        html = self._create_html_page()

        # Check that registers are there
        assert "Registers" in html, html
        assert "dummy_regs" in html, html

        # Check that constants are there
        assert constants_text in html, html
        self._check_constant(name="data_width", value=24, html=html)
        self._check_constant(name="decrement", value=-8, html=html)
        self._check_constant(name="enabled", value="True", html=html)
        self._check_constant(name="disabled", value="False", html=html)
        self._check_constant(name="rate", value="3.5", html=html)
        self._check_constant(name="paragraph", value='"hello there :)"', html=html)

        # Test again with no constants
        self.registers.constants = []
        html = self._create_html_page()

        # Registers should still be there
        assert "Registers" in html, html
        assert "dummy_regs" in html, html

        # But no constants
        assert constants_text not in html, html

    def test_constants_and_no_registers(self):
        self.registers.register_objects = []

        html = self._create_html_page()

        assert "This module does not have any registers" in html, html
        assert "dummy_regs" not in html, html

        assert "<h2>Constants</h2>" in html, html
        self._check_constant(name="data_width", value=24, html=html)
        self._check_constant(name="decrement", value=-8, html=html)

    def _create_html_page(self):
        self.registers.create_html_page(self.tmp_path)
        html = read_file(self.tmp_path / "test_regs.html")
        return html

    @staticmethod
    # pylint: disable=too-many-arguments
    def _check_register(name, index, address, mode, default_value, description, html):
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
    def _check_field(name, index, default_value, description, html):
        expected = f"""
  <tr>
    <td>&nbsp;&nbsp;<em>{name}</em></td>
    <td>&nbsp;&nbsp;{index}</td>
    <td></td>
    <td></td>
    <td>{default_value}</td>
    <td>{description}</td>
"""
        assert expected in html, f"{expected}\n\n{html}"

    @staticmethod
    def _check_register_array(name, length, iterator_range, description, html):
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
    def _check_constant(name, value, html):
        expected = f"""
  <tr>
    <td><strong>{name}</strong></td>
    <td>{value}</td>
"""
        assert expected in html, f"{expected}\n\n{html}"

    def test_register_table_is_empty_string_if_no_registers_are_available(self):
        self.registers.register_objects = []

        self.registers.create_html_register_table(self.tmp_path)
        html = read_file(self.tmp_path / "test_register_table.html")
        assert html == "", html

    def test_constant_table_is_empty_string_if_no_constants_are_available(self):
        self.registers.constants = []

        self.registers.create_html_constant_table(self.tmp_path)
        html = read_file(self.tmp_path / "test_constant_table.html")
        assert html == "", html
