.. _generator_c:

C code generator
================

A C header can be generated from the :class:`.CHeaderGenerator` class by calling
the :meth:`.RegisterCodeGenerator.create` method.
It contains all information about registers, fields and constants.

.. code-block:: python

   CHeaderGenerator(register_list=register_list, output_folder=output_folder).create()

The C header provides two methods for usage: A struct that can be memory mapped, or address definitions that
can be offset a base address.
For the addresses, array registers use a macro with an array index argument.

Below is the resulting code from the :ref:`TOML format example <toml_format>`:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/user_guide/toml_format/c/example_regs.h
   :caption: example_regs.h
   :language: C
   :linenos:
