Breaking changes

* Rework generated C++ API to use C++ ``struct`` with field values instead of raw ``uint32_t``.
  See :ref:`generator_cpp` for usage details.

  * ``get/set_<register>`` method now returns/takes a ``struct`` with field values.

    * New alternative method ``get/set_<register>_raw`` returns/takes a raw
      ``uint32_t`` register value instead of the casted structure.

  * ``get/set_<field>`` method work just as before.
  * ``get_<field>_from_value`` method is removed.

* Represent :class:`.Bit` field values as ``bool`` in generated C++ API.
