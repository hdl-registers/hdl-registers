.. _toml_format:

.toml data file format
======================

The register TOML parser reads a ``.toml`` file and constructs a :class:`.RegisterList` object.
It is important that the TOML is formatted correctly and has the necessary properties.
The register TOML parser will warn if there are any errors in the TOML, such as missing properties,
unknown properties, wrong data type for properties, etc.

The parser is implemented in the :class:`.RegisterParser` class and :func:`.from_toml` function.


Format
------

Below is an example of a typical TOML file.
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


Why TOML?
---------

The `TOML <https://toml.io/>`__ file format (short for "Tom's Obvious Minimal Language") is a
configuration file format that is easy to both read and write.
Compared to XML, YAML and JSON, which would be the most obvious alternatives, it has the
following advantages that are relevant when handling FPGA registers:

* Supports comments in file.
* Supports hexadecimal and binary integer values, with optional underscore separator.
* Clear and readable handling of multiline strings.
* Fewer control characters compared to XML and JSON.
* Very fast Python parser available.

Furthermore, while readability can be considered subjective, the TOML format is indeed quite
Obvious and easy to read.
