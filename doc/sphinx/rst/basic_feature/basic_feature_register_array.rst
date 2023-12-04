.. _basic_feature_register_array:

Register arrays
===============

A register list, i.e. the register set of one module, can contain *register arrays*.
Meaning, a set of registers within the register list that are repeated a number of times.

This page will show you how to set up register arrays, and will showcase
all the code that can be generated from it.


Usage in TOML
-------------

The TOML file below shows how to set up a register array.
See comments for rules about the different properties.

.. literalinclude:: toml/basic_feature_register_array.toml
   :caption: TOML that sets up a register array.
   :language: TOML
   :linenos:

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

.. literalinclude:: py/basic_feature_register_array.py
   :caption: Python code that sets up a register array.
   :language: Python
   :linenos:
   :lines: 10-

See :meth:`.RegisterList.append_register_array` for more Python API details.


Generated code
--------------

See below for a description of the code that can be generated when using register arrays.


HTML page
_________

See HTML file below for the human-readable documentation that is produced by the
``generate()`` call in the Python example above.

See :ref:`generator_html` for more details about the HTML generator and its capabilities.

:download:`HTML page <../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_array/api/caesar_regs.html>`


VHDL package
____________

The VHDL code below is produced by the ``generate()`` call in the Python example above.
Click the button to expand and view the code.
See :ref:`generator_vhdl` for instructions on how it can be used in your VHDL project.


Base register package
~~~~~~~~~~~~~~~~~~~~~

Note how the register indexes are functions here, as opposed to constants as they usually are
for plain registers.
The argument to the function decides which array index to use.
There is an assertion that the array index argument does not exceed the number of times the register
array is repeated.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_array/api/caesar_regs_pkg.vhd
     :caption: Generated VHDL register package.
     :language: VHDL
     :linenos:

|


Record package
~~~~~~~~~~~~~~

The record package is quite hard to understand in this example, but lets try:

* The ``caesar_regs_down_t`` type is a record with a member ``base_addresses``, which is the name
  of the register array.
* The type of this member is a ranged array of another record with two members: ``read_address``
  and ``write_address``, which are the names of the registers in the array.
* Both of these are of a record type that contain the ``address`` bit vector field set up in
  this example.

So in our VHDL code we can access a field value for example like this:

.. code-block:: vhdl

  job.address <= regs_down.base_addresses[1].read_address.address;

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_array/api/caesar_register_record_pkg.vhd
     :caption: Generated VHDL record package.
     :language: VHDL
     :linenos:

|


C++
___

The C++ interface header and implementation code below is produced by the ``generate()`` call in
the Python example above.
Click the button to expand and view each code block.

The class header is skipped here, since its inclusion would make this page very long.
See :ref:`generator_cpp` for more details and an example of how the excluded file might look.


C++ interface header
~~~~~~~~~~~~~~~~~~~~

Note how setters and getters for register and field values have a new argument for the array index.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_array/api/i_caesar.h
     :caption: Generated C++ interface class code.
     :language: C++
     :linenos:

|


C++ implementation
~~~~~~~~~~~~~~~~~~

The C++ implementation code below is produced by the ``generate()`` call in the Python
example above.
Click the button to expand and view the code.

Note that there is an assertion in every setter and getter that the provided array index does not
exceed the number of times the register array is repeated.
This will catch calculation errors during testing and at run-time.


.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_array/api/i_caesar.h
     :caption: Generated C++ interface class code.
     :language: C++
     :linenos:

|


C header
________

The C code below is produced by the ``generate()`` call in the Python example above.
The index and address of each register are given by a macro where the array index is supplied as
an argument.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_array/api/caesar_regs.h
     :caption: Generated C code.
     :language: C
     :linenos:

|
