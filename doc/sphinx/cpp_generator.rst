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

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/example.h
   :caption: Example class header
   :language: C++

.. literalinclude:: ../../generated/sphinx_rst/register_code/cpp/example.cpp
   :caption: Example class implementation
   :language: C++

Note that when the register is part of an array, the setter/getter takes a second
argument ``array_index``.
There is an assert that the user-provided array index is within the bounds of the array.

