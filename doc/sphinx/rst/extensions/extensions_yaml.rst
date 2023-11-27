.. _extensions_json:

Using other data file formats
===============================

The recommended way to define your registers is using a :ref:`TOML file <toml_format>`, due
to :ref:`the benefits <why_toml>` this format offers.
Or to use the :ref:`Python API <python_api>`, or even a mix of the two depending on your use case.
However, if using another data file format, such as YAML or XML, is necessary then that is
also possible.

In this case you need to construct your data on the exact format as the
:ref:`TOML format <toml_format>` and then parse it with a manual call.
Below is an example YAML snippet that sets up some registers, fields and constants.
It uses the third party `PyYAML package <https://pypi.org/project/PyYAML/>`_.

.. literalinclude:: yaml/extensions_yaml.yaml
   :caption: Register data in YAML format.
   :language: yaml
   :linenos:

.. literalinclude:: py/extensions_yaml.py
   :caption: Manually parsing a YAML file with register definitions.
   :language: Python
   :linenos:
   :lines: 10-
