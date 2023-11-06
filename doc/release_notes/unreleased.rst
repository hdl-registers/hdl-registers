Added

* Add register record generation to :class:`.RegisterVhdlGenerator` via
  :meth:`.RegisterList.create_vhdl_package`.

  * For each register, plain or in array, a record with correctly-typed members for each
    register field.
  * For each register array, a correctly-ranged array of records for the registers in that array.
  * Combined record with all the registers and register arrays.
    One each for registers in the up direction and in the down direction.
  * Constants with default values for all of the above types.
  * Conversion functions to/from ``std_logic_vector`` representation for all of the above types.

* Add generation of a wrapper around :ref:`reg_file.axi_lite_reg_file` to
  :class:`.RegisterVhdlGeneratorAxiLite` via :meth:`.RegisterList.create_vhdl_package`.

  * Sets correct generics and has the easy-to-use records above for its register values up
    and down.

Breaking changes

* Rename VHDL field conversion function for enumerations from ``to_<field name>_slv`` to ``to_slv``.

Fixes

* Fix "multiple definition" bug in generated C header for a string constant.
