Enumeration fields
==================

Register fields can be of the type *enumeration*.
Meaning, a field that can only take on a limited, pre-defined, and named, set of values.
This is a very common and highly useful programming concept.
See Wikipedia if you are unfamiliar with this: https://en.wikipedia.org/wiki/Enumerated_type

This page will show you how the set up enumeration fields in a register, and will showcase
all the code that can be generated from it.


Usage in TOML
-------------

The TOML file below shows how to set up a register with two enumeration fields.
See comments for rules about the different properties.

.. literalinclude:: toml/regs_enumeration.toml
   :caption: TOML that sets up a register with enumeration fields.
   :language: TOML
   :linenos:

Note that the second field does not have any default value, meaning that it will automatically
default to the first element (``streaming``).

Below you will see how you can parse this TOML file and generate artifacts from it.


Usage with Python API
---------------------

The Python code below shows

1. How to parse the TOML file listed above.
2. How to create an identical register list when instead using the Python API.
3. How to generate register artifacts.

Note that the result of the ``create_from_api`` call is identical to that of the
``parser_toml`` call.
Meaning that using a TOML file or using the Python API is equivalent.

.. literalinclude:: py/generate_enumeration.py
   :caption: Python code that sets up a register with enumeration fields.
   :language: Python
   :linenos:
   :lines: 10-


Generated code
--------------

See below for a description of the code that can be generated when using enumeration fields.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.
Each enumeration field is documented and the description of each element is included.

See :ref:`html_generator` for more details about the HTML generator and its capabilities.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/field/generate_enumeration/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.
See :ref:`vhdl_generator` for instructions on how it can be used in your VHDL project.

Some interesting things to notice:

1. There is only one register, at index 0.
2. The first field is two bits wide, occupying bits 1 and 0, while the second one is only one
   bit wide, occupying but 3.
3. VHDL supports enumeration types natively.
   The elements of the enumeration are exposed to the scope of the package, and all files that
   include it.
4. For each enumeration field, there are conversion functions for

   a. Converting from the enumeration type to ``std_logic_vector``.
   b. Slicing a register value at the correct range and converting from ``std_logic_vector``
      to enumeration.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_enumeration/api/caesar_regs_pkg.vhd
     :caption: Generated VHDL code.
     :language: VHDL
     :linenos:

|


C++ interface
_____________

The C++ interface header code below is produced by the ``generate()`` call in the Python
example above.
Click the button to expand and view the code.

The class header and implementation are skipped here, since their inclusion would make this page
very long.
See :ref:`cpp_generator` for more details and an example of how the excluded files might look.

Some interesting things to notice in the interface header:

1. The valid enumeration values are defined using a C++ ``enum`` declaration in the namespace of
   each field.
2. The setters and getters for each field value uses the enumeration type as argument or return
   value.


.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_enumeration/api/i_caesar.h
     :caption: Generated C++ interface class code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.
Note how the valid enumeration values are defined using a C ``enum`` declaration.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/field/generate_enumeration/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|
