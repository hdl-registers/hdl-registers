.. _basic_feature_default_registers:

Default registers
=================

A lot of projects use a few default registers in standard locations that shall be present in
all modules.
For example, very commonly the first register of a module is an interrupt status register and the
second one is an interrupt mask.
In order to handle this, without having to duplicate names and descriptions in many places, there
is a ``default_registers`` flag to the :func:`.from_toml` function.
Passing a list of :class:`.Register` objects will insert these registers first in
the :class:`.RegisterList`.


Usage in TOML
-------------

The TOML file below is used to showcase insertion of default registers.

.. literalinclude:: toml/basic_feature_default_registers.toml
   :caption: TOML for showcasing default registers.
   :language: TOML
   :linenos:



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

.. literalinclude:: py/basic_feature_default_registers.py
   :caption: Python code to showcase default registers.
   :language: Python
   :linenos:
   :lines: 10-

See :meth:`.RegisterList.from_default_registers` for more Python API details.


Generated code
--------------

See below for a description of the code that can be generated when using register arrays.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.

See :ref:`html_generator` for more details about the HTML generator and its capabilities.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_default_registers/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.
See :ref:`vhdl_generator` for instructions on how it can be used in your VHDL project.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_default_registers/api/caesar_regs_pkg.vhd
     :caption: Generated VHDL code.
     :language: VHDL
     :linenos:

|


C++ interface header
____________________

The C++ interface header code below is produced by the ``generate()`` call in
the Python example above.
Click the button to expand and view the code.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_default_registers/api/i_caesar.h
     :caption: Generated C++ interface class code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_default_registers/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|
