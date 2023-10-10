Bit fields
==========

Register fields can be of the type *bit*.
Meaning a field of width one that can only take on the logic values of zero or one.

This page will show you how the set up bit fields in a register, and will showcase
all the code that can be generated from it.


Usage in TOML
-------------

The TOML file below shows how to set up a register with two bit fields.
See comments for rules about the different properties.

.. literalinclude:: toml/field_bit.toml
   :caption: TOML that sets up a register with bit fields.
   :language: TOML
   :linenos:

Note that the second field does not have any default value specified, meaning it will default
to zero.

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

.. literalinclude:: py/field_bit.py
   :caption: Python code that sets up a register with bit fields.
   :language: Python
   :linenos:
   :lines: 10-

See :meth:`.Register.append_bit` for more Python API details.



Generated code
--------------

See below for a description of the code that can be generated when using bit fields.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.
Each bit field is documented with its bit index, default value and description.

See :ref:`html_generator` for more details about the HTML generator and its capabilities.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/field/field_bit/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.
See :ref:`vhdl_generator` for instructions on how it can be used in your VHDL project.

Some interesting things to notice:

1. There is only one register, at index 0.
2. For each bit field there is a named constant that defines the bit's index within the register.
3. In VHDL, slicing out a bit from the register value will yield a value of type ``std_ulogic``,
   meaning that typically no casting is needed.
   Hence there are no conversion functions for bit fields, the way there are
   for e.g. :ref:`enumeration fields <field_enumeration_vhdl>`.

.. collapse:: Click to expand/collapse code.

 .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit/api/caesar_regs_pkg.vhd
    :caption: Generated VHDL code.
    :language: VHDL
    :linenos:

|


C++
___

The C++ interface header and implementation code below is produced by the ``generate()`` call in
the Python example above.
Click the button to expand and view each code block.

The class header is skipped here, since its inclusion would make this page very long.
See :ref:`cpp_generator` for more details and an example of how the excluded file might look.


C++ interface header
~~~~~~~~~~~~~~~~~~~~

Note the setters and getters for each individual field value.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit/api/i_caesar.h
     :caption: Generated C++ class interface code.
     :language: C++
     :linenos:

|


C++ implementation
~~~~~~~~~~~~~~~~~~

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit/api/caesar.cpp
     :caption: Generated C++ class implementation code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.
The index and mask of each field are available as constants.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|
