# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Local folder libraries
from .html_translator import HtmlTranslator
from .register import REGISTER_MODES, Register


class RegisterHtmlGenerator:
    """
    Generate a HTML page with register information.
    """

    def __init__(self, module_name, generated_info):
        """
        Arguments:
            module_name (str): The name of the register map.
            generated_info (list(str)): Will be placed in the file headers.
        """
        self.module_name = module_name
        self.generated_info = generated_info
        self._html_translator = HtmlTranslator()

    def get_register_table(self, register_objects):
        """
        Get a HTML table with register infomation. Can be included in other documents.

        Arguments:
            register_objects (list): Register arrays and registers to be included.

        Returns:
            str: HTML code.
        """
        if not register_objects:
            return ""

        html = self._file_header()
        html += self._get_register_table(register_objects)
        return html

    def get_constant_table(self, constants):
        """
        Get a HTML table with constant infomation. Can be included in other documents.

        Arguments:
            constants (list(Constant)): Constants to be included.

        Returns:
            str: HTML code.
        """
        if not constants:
            return ""

        html = self._file_header()
        html += self._get_constant_table(constants)
        return html

    def get_page(self, register_objects, constants):
        """
        Get a complete HTML page with register and constant infomation.

        Arguments:
            register_objects (list): Register arrays and registers to be included.
            constants (list(Constant)): Constants to be included.

        Returns:
            str: HTML code.
        """
        title = f"Documentation of {self.module_name} registers"
        html = f"""\
{self._file_header()}

<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
    <!-- Include the style both inline and as a link to a separate CSS file. -->
    <!-- Some tools, e.g. Jenkins, will not render with an inline styleesheet. -->
    <!-- For other tools, e.g. page inclusion in sphinx, the style must be in the file. -->
    <link rel="stylesheet" href="regs_style.css">
    <style>
      {self.get_page_style()}
    </style>
</head>
<body>
  <h1>{title}</h1>
  <p>This document is a specification for the register interface of the FPGA module \
<b>{self.module_name}</b>.</p>
  <p>{' '.join(self.generated_info)}</p>
  <h2>Register modes</h2>
  <p>The following register modes are available.</p>
{self._get_mode_descriptions()}
"""

        html += "  <h2>Registers</h2>\n"
        if register_objects:
            html += f"""
  <p>The following registers make up the register map.</p>
{self._get_register_table(register_objects)}
"""
        else:
            html += "  <p>This module does not have any registers.</p>"

        html += "  <h2>Constants</h2>\n"
        if constants:
            html += f"""
  <p>The following constants are part of the register interface.</p>
{self._get_constant_table(constants)}"""
        else:
            html += "  <p>This module does not have any constants.</p>"

        html += """
</body>
</html>"""

        return html

    @staticmethod
    def get_page_style(table_style=None, font_style=None, extra_style=""):
        """
        Get a CSS style for the register pages. Shall be saved to a file called ``regs_style.css``.

        Returns:
            str: CSS code.
        """
        if font_style is None:
            font_style = """
html * {
  font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
}"""

        if table_style is None:
            table_style = """
table {
  border-collapse: collapse;
}
td, th {
  border-width: 1px;
  border-style: solid;
  border-color: #ddd;
  padding: 8px;
}
td.array_header {
  border-top-width: 10px;
  border-top-color: #4cacaf;
}
td.array_footer {
  border-bottom-width: 10px;
  border-bottom-color: #4cacaf;
}
tr:nth-child(even) {
  background-color: #f2f2f2;
}
th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #4CAF50;
  color: white;
}"""

        style = f"""
{font_style}
{table_style}
{extra_style}"""
        return style

    @staticmethod
    def _comment(comment):
        return f"<!-- {comment} -->\n"

    def _file_header(self):
        return "".join([self._comment(header_line) for header_line in self.generated_info])

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
        html = f"""
  <tr>
    <td>&nbsp;&nbsp;<em>{field.name}</em></td>
    <td>&nbsp;&nbsp;{field.range}</td>
    <td></td>
    <td></td>
    <td>{field.default_value_str}</td>
    <td>{description}</td>
  </tr>"""

        return html

    def _get_register_table(self, register_objects):
        html = """
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

        for register_object in register_objects:
            if isinstance(register_object, Register):
                html += self._annotate_register(register_object)
            else:
                html += self._annotate_register_array(register_object)

        html += """
</tbody>
</table>"""

        return html

    def _format_constant_value(self, constant):
        if constant.is_string:
            return f'"{constant.value}"'

        # For others, just cast to string
        if constant.is_boolean or constant.is_integer or constant.is_float:
            return str(constant.value)

        raise ValueError(f"Got unexpected constant type. {constant}")

    def _format_hex_constant_value(self, constant):
        if constant.is_integer:
            return self._to_hex_string(value=constant.value, num_nibbles=8)

        # No hex formatting available for the other types
        if constant.is_boolean or constant.is_float or constant.is_string:
            return "-"

        raise ValueError(f"Got unexpected constant type. {constant}")

    def _get_constant_table(self, constants):
        html = """
<table>
<thead>
  <tr>
    <th>Name</th>
    <th>Value</th>
    <th>Value (hexadecimal)</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>"""

        for constant in constants:
            description = self._html_translator.translate(constant.description)
            html += f"""
  <tr>
    <td><strong>{constant.name}</strong></td>
    <td>{self._format_constant_value(constant=constant)}</td>
    <td>{self._format_hex_constant_value(constant=constant)}</td>
    <td>{description}</td>
  </tr>"""

        html += """
</tbody>
</table>"""
        return html

    @staticmethod
    def _get_mode_descriptions():
        html = """
<table>
<thead>
  <tr>
    <th>Mode</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>"""

        for mode in REGISTER_MODES.values():
            html += f"""
<tr>
  <td>{mode.mode_readable}</td>
  <td>{mode.description}</td>
</tr>
"""
        html += """
</tbody>
</table>"""
        return html
