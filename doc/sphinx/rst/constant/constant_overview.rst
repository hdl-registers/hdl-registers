Constant overview
=================

Using register constants is a convenient way to avoid duplication or hard-coding of
important values.
It makes it possible to programmatically provide values from the HDL project build flow to the
software that will integrate it.

We support all conceivable types of constants.
See the menu sidebar for details about the different types and how to use them.

Adding a constant to a register list in Python is done by running
:meth:`.RegisterList.add_constant` on a :class:`.RegisterList` object.
Or in a TOML data file e.g. :ref:`like this <constant_integer_toml>`.
See the menubar to the left for an article about each constant type.
They contain more details about both Python API and TOML format.

