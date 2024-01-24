.. _generator_python:

Python code generator
=====================

The Python code "generator" is an automated way of saving a :class:`.RegisterList`
object to a Python :py:mod:`pickle`.
It is not intended to be used during development, but bundling the Python class pickles when making
an FPGA release can be very useful.
It is accessed via the :class:`.PythonPickleGenerator` class.

The pickle is created e.g. like this:

.. literalinclude:: py/generator_python.py
   :caption: Python code that parses the example TOML file and generates Python register artifacts.
   :language: Python
   :linenos:
   :lines: 10-

This will save the binary pickle, which represents the object precisely,
as well as a convenient Python file to re-create the pickle, shown below:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_python/example.py
   :caption: Example Python class
   :language: Python
   :linenos:

A Python-based system test environment can use the re-created :class:`.RegisterList` objects from
the FPGA release to perform register reads/writes on the correct registers addresses and
field indexes.
