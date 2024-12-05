Added

* Add runtime check that provided C++ bit field setter value is in range.

Fixes

* Fix error when converting small negative values (sfixed) to binary in
  :func:`.numerical_interpretation.to_unsigned_binary`.
