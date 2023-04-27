.. _toml_format:

.toml data file format
======================

The register TOML parser reads a ``.toml`` file and constructs a :class:`.RegisterList` object.
It is important that the TOML is formatted correctly and has the necessary fields.
The register TOML parser will warn if there are any error in the TOML, such as missing fields,
unknown fields, wrong data types for fields, etc.

The parser is implemented in the :class:`.RegisterParser` class and :func:`.from_toml` function.

Format
------

Below is a compilation of all the TOML properties that are available.
Comments describe what attributes are optional and which are required.

.. literalinclude:: files/regs_example.toml
   :caption: Register TOML format rules.
   :language: toml
   :linenos:

See the other articles for an insight into the code that can be generated from this definition file.


Why TOML?
---------

The `TOML <https://toml.io/>`__ file format (short for Tom's Obvious Minimal Language) is a
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
