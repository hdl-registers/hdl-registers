.. _generator_html:

HTML code generator
===================

A complete HTML page can be generated, with register details as well as textual description of the
different register modes.
This is done by using the :class:`.HtmlPageGenerator` class e.g. like this:

.. literalinclude:: py/generator_html.py
   :caption: Python code that parses the example TOML file and generates the HTML code we need.
   :language: Python
   :linenos:
   :lines: 10-

A HTML page generated from the :ref:`TOML format example <toml_format>` can be viewed here:
:download:`example_regs.html <../../../../generated/sphinx_rst/register_code/generator/generator_html/example_regs.html>`

.. note::
   Any reStructuredText (RST) code in description fields will be converted to HTML.
   See the HTML file above for an example of this.


Tables only
-----------

Optionally, only the tables with register and constant descriptions can be generated to HTML,
using the :class:`.HtmlRegisterTableGenerator` and :class:`.HtmlConstantTableGenerator` classes.
These can be included in a separate documentation flow.

Generated HTML file here:
:download:`example_register_table.html <../../../../generated/sphinx_rst/register_code/generator/generator_html/example_register_table.html>`

Generated HTML file here:
:download:`example_constant_table.html <../../../../generated/sphinx_rst/register_code/generator/generator_html/example_constant_table.html>`
