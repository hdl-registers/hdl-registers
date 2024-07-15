# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import Any, Optional

# First party libraries
from hdl_registers.register_modes import REGISTER_MODES

# Local folder libraries
from .constant_table import HtmlConstantTableGenerator
from .html_generator_common import HtmlGeneratorCommon
from .register_table import HtmlRegisterTableGenerator


class HtmlPageGenerator(HtmlGeneratorCommon):
    """
    Generate a HTML page with register and constant information.
    See the :ref:`generator_html` article for usage details.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "HTML page"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_regs.html"

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete HTML page with register and constant information.
        """
        title = f"Documentation of {self.name} registers"
        html = f"""\
{self.header}
<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
    <!-- Include the style both inline and as a link to a separate CSS file. -->
    <!-- Some tools, e.g. Jenkins, will not render with an inline stylesheet. -->
    <!-- For other tools, e.g. page inclusion in sphinx, the style must be in the file. -->
    <link rel="stylesheet" href="regs_style.css">
    <style>
      {self.get_page_style()}
    </style>
</head>
<body>
  <h1>{title}</h1>
  <p>This document is a specification for the register interface of the FPGA module \
<b>{self.name}</b>.</p>
  <p>{' '.join(self.generated_source_info)}</p>
  <h2>Register modes</h2>
  <p>The following register modes are available.</p>
{self._get_mode_descriptions()}
"""

        html += "  <h2>Registers</h2>\n"
        if self.register_list.register_objects:
            register_table_generator = HtmlRegisterTableGenerator(
                register_list=self.register_list, output_folder=self.output_folder
            )
            html += f"""
  <p>The following registers make up the register map.</p>
{register_table_generator.get_code()}
"""
        else:
            html += "  <p>This module does not have any registers.</p>"

        html += "  <h2>Constants</h2>\n"
        if self.register_list.constants:
            constant_table_generator = HtmlConstantTableGenerator(
                register_list=self.register_list, output_folder=self.output_folder
            )
            html += f"""
  <p>The following constants are part of the register interface.</p>
{constant_table_generator.get_code()}"""
        else:
            html += "  <p>This module does not have any constants.</p>"

        html += """
</body>
</html>"""

        return html

    @staticmethod
    def get_page_style(
        table_style: Optional[str] = None, font_style: Optional[str] = None, extra_style: str = ""
    ) -> str:
        """
        Get a CSS style for the register pages. Shall be saved to a file called ``regs_style.css``.

        Return:
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
    def _get_mode_descriptions() -> str:
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
  <td>{mode.name}</td>
  <td>{mode.description}</td>
</tr>
"""
        html += """
</tbody>
</table>"""
        return html
