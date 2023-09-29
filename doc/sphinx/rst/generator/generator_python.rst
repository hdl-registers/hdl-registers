.. _python_generator:

Python code generator
=====================

The Python code "generator" is an automated way of saving a :class:`.RegisterList`
object to a Python :py:mod:`pickle`.
It is not intended to be used during development, but bundling the Python class pickles when making
an FPGA release can be very useful.

Running the :meth:`.RegisterList.create_python_class` method will create a binary pickle, which
represents the object precisely, as well as a convenient Python file to re-create the pickle,
shown below:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/py/example.py
   :caption: Example Python class
   :language: Python

A Python-based system test environment can use the re-created :class:`.RegisterList` objects from
the FPGA release to perform register reads/writes on the correct registers addresses and
field indexes.
