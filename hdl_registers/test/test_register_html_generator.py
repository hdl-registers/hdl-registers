# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import unittest

import pytest

import tsfpga
from tsfpga.system_utils import read_file
from tsfpga.registers.parser import from_toml


@pytest.mark.usefixtures("fixture_tmp_path")
class TestRegisterHtmlGenerator(unittest.TestCase):
    tmp_path = None

    def setUp(self):
        toml_file = tsfpga.TSFPGA_EXAMPLE_MODULES / "artyz7" / "regs_artyz7.toml"
        self.registers = from_toml("artyz7", toml_file)

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
            index="1 + i &times; 2",
            address="0x0004 + i &times; 0x0008",
            mode="Read, Write",
            default_value="0x31",
            description="The first register in the array.",
            html=html,
        )

        self._check_register(
            name="second_array_dummy_reg",
            index="2 + i &times; 2",
            address="0x0008 + i &times; 0x0008",
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
        html = self._create_html_page()
        assert "The following constants are part of the register interface" not in html, html

        # Add some constants and assert
        self.registers.add_constant("data_width", 24)
        self.registers.add_constant("decrement", -8)
        html = self._create_html_page()

        assert "Registers" in html, html
        assert "dummy_regs" in html, html

        assert "The following constants are part of the register interface" in html, html
        self._check_constant(name="data_width", value=24, html=html)
        self._check_constant(name="decrement", value=-8, html=html)

    def test_constants_and_no_registers(self):
        self.registers.register_objects = []

        # Add some constants and assert
        self.registers.add_constant("data_width", 24)
        self.registers.add_constant("decrement", -8)
        html = self._create_html_page()

        assert "This module does not have any registers" in html, html
        assert "dummy_regs" not in html, html

        assert "<h2>Constants</h2>" in html, html
        self._check_constant(name="data_width", value=24, html=html)
        self._check_constant(name="decrement", value=-8, html=html)

    def _create_html_page(self):
        self.registers.create_html_page(self.tmp_path)
        html = read_file(self.tmp_path / "artyz7_regs.html")
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
        html = read_file(self.tmp_path / "artyz7_register_table.html")
        assert html == "", html

    def test_constant_table_is_empty_string_if_no_constants_are_available(self):
        self.registers.constants = []

        self.registers.create_html_constant_table(self.tmp_path)
        html = read_file(self.tmp_path / "artyz7_constant_table.html")
        assert html == "", html
