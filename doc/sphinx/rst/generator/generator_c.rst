C code generator
================

A C header can be generated with a call to :meth:`.RegisterList.create_c_header`.
It contains all information about registers, fields and constants.
Below is the resulting code from the :ref:`TOML format example <toml_format>`:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/c/example_regs.h
   :caption: example_regs.h
   :language: C
   :linenos:

It provides two methods for usage: A struct that can be memory mapped, or address definitions that
can be offset a base address.
For the addresses, array registers use a macro with an array index argument.
