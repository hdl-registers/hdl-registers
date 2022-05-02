Added

* Add field setters and getters to :class:`.RegisterCppGenerator`.

Breaking changes

* Remove the field ``_mask`` and ``_shift`` public constants from the generated C++
  interface header. These are not needed now that setters and getters are available.
