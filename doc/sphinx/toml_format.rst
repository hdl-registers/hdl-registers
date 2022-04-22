.. _toml_format:

.toml data file format
======================

The register TOML parser reads a ``.toml`` file and constructs a :class:`.RegisterList` object.
It is important that the TOML is formatted correctly and has the necessary fields.
The register TOML parser will warn if there are any error in the TOML, such as missing fields,
unknown fields, wrong data types for fields, etc.

The parser is implemented in the :class:`.RegisterParser` class and :func:`.from_toml` function.

Below is a compilation of all the TOML properties that are available.
Comments describe what attributes are optional and which are required.

.. literalinclude:: files/regs_example.toml
   :caption: Register TOML format rules.
   :language: toml

See the other articles for an insight into the code that can be from this definition file.
