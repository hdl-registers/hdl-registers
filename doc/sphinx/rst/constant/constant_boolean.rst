Boolean constants
=================

Register constants can be of type *boolean*.
This page will show you how the set up boolean constants, as well as showcase
all the code that can be generated from it.


Usage in TOML
-------------

The TOML file below shows how to set up a register list with two boolean constants.
Note that in the TOML, the type of the constant is determined by the type of the literal value.

.. literalinclude:: toml/constant_boolean.toml
   :caption: TOML that sets up a register list with boolean constants.
   :language: TOML
   :linenos:

Note that the second constant does not have a description specified, meaning it will default to an
empty string.

Below you will see how you can parse this TOML file and generate artifacts from it.


Usage with Python API
---------------------

The Python code below shows

1. How to parse the TOML file listed above.
2. How to create an identical register list when instead using the Python API.
3. How to generate register artifacts.

Note that the result of the ``create_from_api`` call is identical to that of the
``parse_toml`` call.
Meaning that using a TOML file or using the Python API is completely equivalent.
You choose yourself which method you want to use in your code base.

.. literalinclude:: py/constant_boolean.py
   :caption: Python code that sets up a register list with boolean constants.
   :language: Python
   :linenos:
   :lines: 10-

See :meth:`.RegisterList.add_constant` for more Python API details.


Generated code
--------------

See below for a description of the code that can be generated with these constants.

Note that the examples on this page set up a register list with only constants, no registers.
This allowed of course, but albeit a little bit rare.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/constant/constant_boolean/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/constant/constant_boolean/api/caesar_regs_pkg.vhd
     :caption: Generated VHDL code.
     :language: VHDL
     :linenos:

|


C++ interface
_____________

The C++ interface header code below is produced by the ``generate()`` call in the Python
example above.
Click the button to expand and view the code.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/constant/constant_boolean/api/i_caesar.h
     :caption: Generated C++ interface class code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/constant/constant_boolean/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|

