.. _generator_c:

C code generator
================

A C header can be generated, that contains all information about registers, fields and constants.
The code is generated from the :class:`.CHeaderGenerator` class by calling
the :meth:`.RegisterCodeGenerator.create` method.

.. literalinclude:: py/generator_c.py
   :caption: Python code that parses the example TOML file and generates the C code we need.
   :language: Python
   :linenos:
   :lines: 10-

The C header provides two methods for usage: A struct that can be memory mapped, or address definitions that
can be offset a base address.
For the addresses, array registers use a macro with an array index argument.

Below is the resulting code from the :ref:`TOML format example <toml_format>`:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_c/example_regs.h
   :caption: example_regs.h
   :language: C
   :linenos:
