Field overview
==============

Each register can be filled with many different fields of different types and interpretations.
See the menu sidebar for details on each of the field types we support.

Adding a field to a register in Python by running e.g. :meth:`.Register.append_enumeration` on
a :class:`.Register` object.
Or in a TOML data file e.g. :ref:`like this <field_enumeration_toml>`.
See the page for each field type for more details about both Python API and TOML format.

Obviously there is a limit to how many fields you can add to a register.
If your fields add up to more than 32 bits of width, an error will be reported.

Note that for some fields, like :ref:`bit vector <field_bit_vector>`, the width is specified
directly by the user, whereas for others like :ref:`enumeration <field_enumeration>` it is
calculated by the tool.
