.. _generator_html:

HTML code generator
===================

A complete HTML page can be generated, with register details as well as textual description of the
different register modes.
This is done by using the :class:`.HtmlPageGenerator` class e.g. like this:

.. code-block:: python

   HtmlPageGenerator(register_list=register_list, output_folder=output_folder).create()

A HTML page generated from the :ref:`TOML format example <toml_format>` can be viewed here:
:download:`example_regs.html <../../../../generated/sphinx_rst/register_code/user_guide/toml_format/html/example_regs.html>`

.. note::
   Markdown/reStructuredText syntax can be used in register and bit descriptions, which will be
   converted to appropriate HTML tags.
   Text can be set bold with double asterisks, and italicised with a single asterisk.
   A paragraph break can be inserted with consecutive newlines.


Tables only
-----------

Optionally, only the tables with register and constant descriptions can be generated to HTML,
using the :class:`.HtmlRegisterTableGenerator` and :class:`.HtmlConstantTableGenerator` classes.
These can be included in a separate documentation flow.

Generated HTML file here:
:download:`example_register_table.html <../../../../generated/sphinx_rst/register_code/user_guide/toml_format/html/example_register_table.html>`

Generated HTML file here:
:download:`example_constant_table.html <../../../../generated/sphinx_rst/register_code/user_guide/toml_format/html/example_constant_table.html>`
