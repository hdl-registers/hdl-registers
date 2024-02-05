Added

* Add generation of simulation support package that checks field values to
  :class:`.VhdlSimulationCheckPackageGenerator`.

  * Uses VUnit Verification Components for bus operations.

  * Generates a ``check_equal`` procedure for each field in each readable register.

  * Use native VHDL type for value representation.
