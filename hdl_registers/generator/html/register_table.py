# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import TYPE_CHECKING

# First party libraries
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.register import REGISTER_MODES, Register

# Local folder libraries
from .html_generator_common import HtmlGeneratorCommon
from .html_translator import HtmlTranslator

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register_list import RegisterList


class HtmlRegisterTableGenerator(HtmlGeneratorCommon):
    """
    Generate HTML code with register information in a table.
    """

    SHORT_DESCRIPTION = "HTML register table"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_register_table.html"

    def __init__(self, register_list: "RegisterList", output_folder: Path):
        super().__init__(register_list=register_list, output_folder=output_folder)

        self._html_translator = HtmlTranslator()

    def get_code(self, **kwargs) -> str:
        if not self.register_list.register_objects:
            return ""

        html = f"""\
{self.header}
<table>
<thead>
  <tr>
    <th>Name</th>
    <th>Index</th>
    <th>Address</th>
    <th>Mode</th>
    <th>Default value</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>"""

        for register_object in self.iterate_register_objects():
            if isinstance(register_object, Register):
                html += self._annotate_register(register_object)
            else:
                html += self._annotate_register_array(register_object)

        html += """
</tbody>
</table>"""

        return html

    @staticmethod
    def _to_hex_string(value, num_nibbles=4):
        """
        Convert an integer value to a hexadecimal string. E.g. "0x1000".
        """
        if value < 0:
            return "-"

        formatting_string = f"0x{{:0{num_nibbles}X}}"
        return formatting_string.format(value)

    def _annotate_register_array(self, register_object):
        description = self._html_translator.translate(register_object.description)
        html = f"""
  <tr>
    <td class="array_header" colspan=5>
      Register array <strong>{register_object.name}</strong>, \
repeated {register_object.length} times.
      Iterator <i>i &isin; [0, {register_object.length - 1}].</i>
    </td>
    <td class="array_header">{description}</td>
  </tr>"""
        array_index_increment = len(register_object.registers)
        for register in register_object.registers:
            register_index = register_object.base_index + register.index
            html += self._annotate_register(register, register_index, array_index_increment)

        html += f"""
  <tr>
    <td colspan="6" class="array_footer">
      End register array <strong>{register_object.name}.</strong>
    </td>
  </tr>"""
        return html

    def _annotate_register(self, register, register_array_index=None, array_index_increment=None):
        if register_array_index is None:
            address_readable = self._to_hex_string(register.address)
            index = register.address // 4
        else:
            register_address = self._to_hex_string(4 * register_array_index)
            address_increment = self._to_hex_string(4 * array_index_increment)
            address_readable = f"{register_address} + i &times; {address_increment}"

            index = f"{register_array_index} + i &times; {array_index_increment}"

        description = self._html_translator.translate(register.description)
        html = f"""
  <tr>
    <td><strong>{register.name}</strong></td>
    <td>{index}</td>
    <td>{address_readable}</td>
    <td>{REGISTER_MODES[register.mode].mode_readable}</td>
    <td>{self._to_hex_string(register.default_value, num_nibbles=1)}</td>
    <td>{description}</td>
  </tr>"""

        for field in register.fields:
            html += self._annotate_field(field)

        return html

    def _annotate_field(self, field):
        description = self._html_translator.translate(field.description)

        if isinstance(field, Enumeration):
            description += """\
      <br />
      <br />
      Can be set to the following values:

      <dl>
"""

            for element in field.elements:
                description += f"""\
        <dt style="display: list-item; margin-left:1em">
          <em>{element.name} ({element.value})</em>:
        </dt>
"""

                element_html = self._html_translator.translate(element.description)
                description += f"        <dd>{element_html}</dd>\n"

            description += "      </dl>\n"

        if isinstance(field, Integer):
            description += f"""\
      <br />
      <br />
      Valid numeric range: [{field.min_value} &ndash; {field.max_value}].
"""

        html = f"""
  <tr>
    <td>&nbsp;&nbsp;<em>{field.name}</em></td>
    <td>&nbsp;&nbsp;{field.range_str}</td>
    <td></td>
    <td></td>
    <td>{field.default_value_str}</td>
    <td>
      {description}
    </td>
  </tr>"""

        return html
