C++ code generator
==================

A complete C++ class can be generated with methods that read or write the registers.
This is done with a call to :meth:`.RegisterList.create_cpp_interface`,
:meth:`.RegisterList.create_cpp_header`, or :meth:`.RegisterList.create_cpp_implementation`.
The first call will create an abstract interface header that can be used for mocking in a unit
test environment.

Below is the resulting code from the :doc:`TOML format example <toml_format>`:

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/i_example.h
   :caption: Example interface header
   :language: C++

Note that there are three ways to read a register field:

1. The method that reads the whole register, e.g. ``get_configuration()``.

2. The method that reads the register and then slices out the field value,
   e.g. ``get_configuration_enable()``.

3. The method that slices out the field value given a previously read register value,
   e.g. ``get_configuration_enable_from_value(register_value)``.

Method (2) is the most convenient in most cases.
However if we want to read out more than one field from a register it would be very inefficient to
read the register value more than once over the register bus, which would be the result of calling
(2) multiple times.
Instead we can call (1) once and then (3) multiple times to get our field values.

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/example.h
   :caption: Example class header
   :language: C++

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/example.cpp
   :caption: Example class implementation
   :language: C++

Note that when the register is part of an array, the setter/getter takes a second
argument ``array_index``.
There is an assert that the user-provided array index is within the bounds of the array.

