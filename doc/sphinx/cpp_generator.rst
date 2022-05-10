C++ code generator
==================

A complete C++ class can be generated with methods that read or write the registers.
This is done with a call to :meth:`.RegisterList.create_cpp_interface`,
:meth:`.RegisterList.create_cpp_header`, or :meth:`.RegisterList.create_cpp_implementation`.
The first call will create an abstract interface header that can be used for mocking in a unit
test environment.


.. _interface_header:

Interface header
----------------

Below is the resulting interface header code, generated from the
:doc:`TOML format example <toml_format>`:

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/i_example.h
   :caption: Example interface header
   :language: C++


Class header
------------

Below is the generated class header:

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/example.h
   :caption: Example class header
   :language: C++


Implementation
--------------

Below is the generated class implementation:

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/example.cpp
   :caption: Example class implementation
   :language: C++

Note that when the register is part of an array, the register setter/getter takes a second
argument ``array_index``.
There is an assert that the user-provided array index is within the bounds of the array.


Getters
-------

It can be noted, most clearly in the :ref:`interface_header`, that there are three ways to read a
register field:

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


Setters
-------

Conversely there are three ways to write a register field:

1. The method that writes the whole register, e.g. ``set_configuration()``.

2. The method that reads the register, updates the value of the field, and then writes the register
   back, e.g. ``set_configuration_enable()``.

3. The method that updates the value of the field given a previously read register value,
   and returns an updated register value,
   e.g. ``set_configuration_enable_from_value(register_value)``.

Method (2) is the most convenient in most cases.
However if we want to update more than one field of a register it would be very inefficient to
read and write the register more than once over the register bus, which would be the result of
calling (2) multiple times.
Instead we can call a register getter once, e.g. ``get_configuration()``, and then (3) multiple
times to get our updated register value.
This value is then written over the register bus using (1).

Exceptions
__________

The discussion about setters above is valid for "read write" mode registers, which is arguably the
most common type.
However there are three register modes where the previously written register value can not be
read back over the bus and then modified: "write only", "write pulse", and "read, write pulse".
The field setters for registers of this mode will write all bits outside of the current field
as zero.
This can for example be seen in the setter ``set_command_start()`` in the generated code above.
