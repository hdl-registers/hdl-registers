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
from typing import TYPE_CHECKING, Any

# First party libraries
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant

# Local folder libraries
from .html_generator_common import HtmlGeneratorCommon
from .html_translator import HtmlTranslator

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.constant.constant import Constant
    from hdl_registers.register_list import RegisterList


class HtmlConstantTableGenerator(HtmlGeneratorCommon):
    """
    Generate HTML code with register constant information in a table.
    See the :ref:`generator_html` article for usage details.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "HTML constant table"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_constant_table.html"

    def __init__(self, register_list: "RegisterList", output_folder: Path):
        super().__init__(register_list=register_list, output_folder=output_folder)

        self._html_translator = HtmlTranslator()

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a HTML table with information about register constants.
        """
        if not self.register_list.constants:
            return ""

        html = f"""\
{self.header}
<table>
<thead>
  <tr>
    <th>Name</th>
    <th>Value</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>"""

        for constant in self.iterate_constants():
            description = self._html_translator.translate(constant.description)
            html += f"""
  <tr>
    <td><strong>{constant.name}</strong></td>
    <td>{self._format_constant_value(constant=constant)}</td>
    <td>{description}</td>
  </tr>"""

        html += """
</tbody>
</table>"""
        return html

    def _format_constant_value(self, constant: "Constant") -> str:
        if isinstance(constant, UnsignedVectorConstant):
            return f"{constant.prefix}{constant.value}"

        if isinstance(constant, StringConstant):
            return f'"{constant.value}"'

        # For others, just cast to string.
        if isinstance(constant, (BooleanConstant, IntegerConstant, FloatConstant)):
            return str(constant.value)

        raise ValueError(f'Got unexpected constant type. "{constant}".')
