.. _toml_format:

Working with data files
=======================

The register parser reads a data file and constructs a :class:`.RegisterList` object.
It is important that the data file is formatted correctly and has the necessary properties.
The register parser will warn if there are any errors in the data, such as missing properties,
unknown properties, wrong data type for properties, etc.

The register parser is implemented in the :class:`.RegisterParser` class.
It can be called with the :func:`.from_toml`, :func:`.from_json` and :func:`.from_yaml` functions.


.. _why_toml:

Why TOML?
---------

The TOML data file format is highly recommended for specifying your registers.

It is a configuration file format that is easy to both read and write.
Compared to XML, YAML and JSON, which would be the most obvious alternatives, it has the
following advantages that are relevant when handling FPGA registers:

* Supports comments in file.
* Supports hexadecimal and binary integer values, with optional underscore separator.
* Clear and readable handling of multiline strings.
* Duplicate key is an error.
* Fewer control characters compared to XML and JSON.
* Very fast Python parser available.

Furthermore, while readability can be considered subjective, the TOML format is considered quite
obvious and easy to read.



.. _toml_formatting:

TOML Format
-----------

Below is an example of a typical TOML file, which can be parsed with a call to :func:`.from_toml`.
It sets up:

1. Two registers with different :ref:`modes <basic_feature_register_modes>`.

   a. One of which contains a :ref:`bit field <field_bit>` and
      an :ref:`enumeration field <field_enumeration>`.

2. A :ref:`register array <basic_feature_register_array>` with two registers and fields.
3. An :ref:`integer constant <constant_integer>` and a :ref:`float constant <constant_float>`.

See the menu sidebar for details about how to set up the different fields, constants, etc.

Also, see the "generator" articles for insight into the code that can be generated from this
definition file.
For example, the human-readable documentation from the data below can be seen in
the :ref:`generator_html` article.

.. literalinclude:: toml/toml_format.toml
  :caption: Register TOML format example.
  :language: toml
  :linenos:



Using JSON data file
--------------------

The TOML format is highly recommended due to the benefits it offers, listed above.
Also all the examples on this website are using TOML.
However, the tool also supports using JSON data files if that is desired.

In this case you need to construct your JSON data on the exact format as the
:ref:`TOML format <toml_formatting>` above and then parse it with a call to :func:`.from_json`.

Below is an example JSON snippet that sets up some register data:

.. literalinclude:: json/toml_format.json
  :caption: Register JSON format example.
  :language: json
  :linenos:



Using YAML data file
--------------------

The TOML format is highly recommended due to the benefits it offers, listed above.
Also all the examples on this website are using TOML.
However, the tool also supports using YAML data files if that is desired.

In this case you need to construct your YAML data on the exact format as the
:ref:`TOML format <toml_formatting>` above and then parse it with a call to :func:`.from_yaml`.

Below is an example YAML snippet that sets up some register data:

.. literalinclude:: yaml/toml_format.yaml
  :caption: Register YAML format example.
  :language: yaml
  :linenos:



Other data file formats
-----------------------

The TOML format is highly recommended due to the benefits it offers, listed above.
We also officially support parsing JSON and YAML, see above.
However, if you want to parse some other exotic data file format then that is also possible.

The parser functions, e.g. :func:`.from_toml`, are just very thin wrappers around the
:class:`.RegisterParser` class.
The :class:`.RegisterParser` class takes register data as a Python dictionary and returns the
high-level object :class:`.RegisterList`.
So in order to implement your own parser, simply read or construct the data as Python dictionary
in the exact format as described :ref:`above <toml_formatting>` and pass it
to :class:`.RegisterParser`.

If you write a parser that you think others might have use for, please consider contributing to
this project by creating an `issue <https://github.com/hdl-registers/hdl-registers/issues>`__
or a `pull request <https://github.com/hdl-registers/hdl-registers/pulls>`__.
