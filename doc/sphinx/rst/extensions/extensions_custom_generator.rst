.. _extensions_custom_generator:

Writing a custom code generator
===============================

The register code generator API in hdl-registers is carefully designed to be very extensible.
Writing and using your own custom code generator is very simple.

The key is to inherit the :class:`.RegisterCodeGenerator` class, as seen in the example below.


Example
-------

The example below is a simple "code" generator that will dump the names of each register to a
text file.

.. literalinclude:: py/extensions_custom_generator.py
   :caption: Example of a custom code generator.
   :language: Python
   :linenos:
   :lines: 10-

The ``COMMENT_START``, ``SHORT_DESCRIPTION`` and ``output_file`` class properties are abstract
in the super class, and MUST hence be implemented in the subclass.
The same is true, naturally, for the ``get_code`` method which is where all the code
generation happens.

The generator class inheriting from :class:`.RegisterCodeGenerator` means that it has the public
methods :meth:`.RegisterCodeGenerator.create`, :meth:`.RegisterCodeGenerator.create_if_needed`
and :meth:`.RegisterCodeGenerator.header` just like the standard hdl-registers generators.

If the custom generator also inherits from :class:`.RegisterCodeGeneratorHelpers`,
it has access to some useful functions for constructing the generated code.
Used in the example above is :meth:`.RegisterCodeGeneratorHelpers.iterate_registers`.

Running the example script above will yield the following result file:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/extensions/extensions_custom_generator/caesar_registers.txt
   :caption: Result text file from custom code generator.
   :language: text

Note that the header uses the ``COMMENT_START`` character to start each line.
This header is used by :meth:`.RegisterCodeGenerator.create_if_needed` to determine if a re-generate
of the file is necessary.

Running the script above yields the following shell printout:

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/extensions/extensions_custom_generator/stdout.txt
   :caption: Shell output when running custom code generator.
   :language: text

Note that the "text list" part of the printout is the ``SHORT_DESCRIPTION`` property of our
generator class above.
The file name is of course also given by ``output_file`` of our generator class.


Contributions
-------------

If you write a high-quality code generator you are more than welcome to contribute it to the
hdl-registers project.
Please open an `issue <https://github.com/hdl-registers/hdl-registers/issues>`__
or a `pull request <https://github.com/hdl-registers/hdl-registers/pulls>`__.


Performance
-----------

Since code generation is usually quite slow, there is a mechanism in place for speeding up the
process and giving a better user experience.
For code generation that is time-critical, such as generating a register package before a user
simulation run, it is recommended to call the
:meth:`.RegisterCodeGenerator.create_if_needed` method.
This method will only re-create the artifact if some register definition has changed or a tool
version is bumped.
Hence using this method as opposed to :meth:`.RegisterCodeGenerator.create` saves a lot of time,
especially in a large project.


Code templating engine
----------------------

The code generation in a custom code generator can be done either using plain Python, as in the
example above, or using an engine such as `Jinja <https://jinja.palletsprojects.com/>`__.
This is completely up to the user.
The custom code generator is pure Python and you are free to be as fancy/creative as you want.


Custom arguments
----------------

The :meth:`.RegisterCodeGenerator.create`, :meth:`.RegisterCodeGenerator.create_if_needed`
and :meth:`.RegisterCodeGenerator.get_code` all have a ``**kwargs`` argument available.
If you want to send further information/arguments to the code generator for some exotic feature,
this makes it possible.
