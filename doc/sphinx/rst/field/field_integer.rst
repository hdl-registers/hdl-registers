Integer fields
==============

Register fields can be of the type *integer*.
Meaning, a numeric field, as opposed to a bit vector, that has a defined upper and lower range.

This page will show you how the set up integer fields in a register, and will showcase
all the code that can be generated from it.


Usage in TOML
-------------

The TOML file below shows how to set up a register with two integer fields.
See comments for rules about the different properties.

.. literalinclude:: toml/regs_integer.toml
   :caption: TOML that sets up a register with integer fields.
   :language: TOML
   :linenos:

Note that the second field does not have any lower bound specified, meaning it will default to zero.
It also does not have any default value, meaning that it will automatically default to the lower
bound, i.e. zero.

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

.. literalinclude:: py/generate_integer.py
   :caption: Python code that sets up a register with integer fields.
   :language: Python
   :linenos:
   :lines: 10-

See :meth:`.Register.append_integer` for more Python API details.


Generated code
--------------

See below for a description of the code that can be generated when using integer fields.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.
Each integer field is documented with its valid range.

See :ref:`html_generator` for more details about the HTML generator and its capabilities.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/field/generate_integer/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.
See :ref:`vhdl_generator` for instructions on how it can be used in your VHDL project.

Some interesting things to notice:

1. There is only one register, at index 0.
2. The first field is nine bits wide, occupying bits 8 down to 0, while the second one is three
   bits wide, occupying but 11 down to 9.
3. VHDL supports integer types natively.
   For each field there is a sub-type that is a properly ranged ``integer``.
4. For each integer field, there are conversion functions for

   a. Converting from the integer type to ``std_logic_vector``.
   b. Slicing a register value at the correct range and converting from ``std_logic_vector``
      to integer.


.. collapse:: Click to expand/collapse code.

 .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_integer/api/caesar_regs_pkg.vhd
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

Note that the setters and getters for each field value use an integer type as argument or
return value.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_integer/api/i_caesar.h
     :caption: Generated C++ class interface code.
     :language: C++
     :linenos:

|


C++ implementation
~~~~~~~~~~~~~~~~~~

Note that each setter performs assertions that the supplied argument is withing the legal range of
the field.
This will catch calculation errors during testing and at run-time.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_integer/api/caesar.cpp
     :caption: Generated C++ class implementation code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.
The range and mask of the each field are available as constants.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_integer/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|
