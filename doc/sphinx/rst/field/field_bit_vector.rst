.. _field_bit_vector:

Bit vector fields
=================

Register fields can be of the type *bit vector*.
Meaning, an array of logic bits.

This page will show you how the set up bit vector fields in a register, and will showcase
all the code that can be generated from it.


Usage in TOML
-------------

The TOML file below shows how to set up a register with two bit vector fields.
See comments for rules about the different properties.

.. literalinclude:: toml/field_bit_vector.toml
   :caption: TOML that sets up a register with bit vector fields.
   :language: TOML
   :linenos:

Note that the second field does not have any default value specified, meaning it will default to
all zeros.

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

.. literalinclude:: py/field_bit_vector.py
   :caption: Python code that sets up a register with bit vector fields.
   :language: Python
   :linenos:
   :lines: 10-

See :meth:`.Register.append_bit_vector` for more Python API details.


Generated code
--------------

See below for a description of the code that can be generated when using bit vector fields.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.
Each bit vector field is documented with its range, default value and description.

See :ref:`html_generator` for more details about the HTML generator and its capabilities.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/field/field_bit_vector/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.
See :ref:`vhdl_generator` for instructions on how it can be used in your VHDL project.

Some interesting things to notice:

1. There is only one register, at index 0.
2. The first field is four bits wide, occupying bits 3 down to 0, while the second one is eight
   bits wide, occupying but 11 down to 4.
3. For each bit vector field there is a named integer subtype that defines the fields's bit range
   within the register.
4. In VHDL, slicing out a range from the register value will yield a value of type
   ``std_ulogic_vector``, meaning that typically no casting is needed.
   Hence there are no conversion functions for bit vector fields, the way there are
   for e.g. :ref:`enumeration fields <field_enumeration_vhdl>`.

.. collapse:: Click to expand/collapse code.

 .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit_vector/api/caesar_regs_pkg.vhd
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

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit_vector/api/i_caesar.h
     :caption: Generated C++ class interface code.
     :language: C++
     :linenos:

|


C++ implementation
~~~~~~~~~~~~~~~~~~

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit_vector/api/caesar.cpp
     :caption: Generated C++ class implementation code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.
The range and mask of the each field are available as constants.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/field_bit_vector/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|
