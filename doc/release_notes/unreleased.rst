Added

* Add custom assertion macro call for C++ runtime checks.
  Adds the possibility of user-defined handling of errors.
  See :ref:`cpp_assertion_macros`.

Breaking changes

* The C++ user must now implement the ``register_getter_assert_fail``,
  ``register_setter_assert_fail`` and ``register_array_index_assert_fail``
  functions (or set a ``#define``).
  See :ref:`cpp_assertion_macros`.
