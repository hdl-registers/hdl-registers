Breaking changes

* Rework generated C++ API to use C++ ``struct`` with field values instead of raw ``uint32_t``.

  * ``get/set_<register>`` method now returns/takes a ``struct`` with field values.
  * ``get/set_<field>`` method work just as before.
  * ``get_<field>_from_value`` method is removed.

* Represent :class:`.Bit` field values as ``bool`` in generated C++ API.
