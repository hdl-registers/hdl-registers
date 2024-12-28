Added

* Add custom assertion macro call for C++ runtime checks.
  Adds the possibility of user-defined handling of errors.
  See :ref:`cpp_assertion_macros`.

Breaking changes

* The user must now implement an ``assertion_handler`` function and pass it as a constructor
  argument to the generated C++ class.
  See :ref:`cpp_assertion_macros`.

Changes

* The :meth:`.RegisterCodeGenerator.create` method now includes the header lines in the generated
  code on its own.
  No need to call :meth:`.RegisterCodeGenerator.header` in :meth:`.RegisterCodeGenerator.get_code`
  in custom generators anymore.
