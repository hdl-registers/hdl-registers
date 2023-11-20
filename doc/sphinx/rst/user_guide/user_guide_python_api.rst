.. _python_api:

Working with Python API
=======================

The recommended way of defining your registers and fields is to use
a :ref:`.toml data file <toml_format>`.
However depending on your needs it might make sense to define them directly in Python instead.
This page will showcase a simple example of how to get started with this.

The Python code below sets up a :class:`.RegisterList` with two :class:`Registers <.Register>` and some
:class:`fields <.Integer>`.
After this it performs a :ref:`VHDL code generation <generator_vhdl>`.

.. literalinclude:: py/user_guide_python_api.py
  :caption: Register TOML format example.
  :language: Python
  :linenos:
  :lines: 10-

The articles in the the menubar on the left all showcase how to utilize the different features
using the Python API as well as a TOML file.
Please read these articles for further information.
