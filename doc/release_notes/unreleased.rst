Added

* Add custom assertion macro call for C++ runtime checks.
  Adds the possibility of user-defined handling of errors.
  See :ref:`cpp_assertion_macros`.

Breaking changes

* The user must now implement an ``assertion_handler`` function and pass it as a constructor
  argument to the generated C++ class.
  See :ref:`cpp_assertion_macros`.
