Breaking changes

* Rework generated C++ API to use C++ ``struct`` with field values instead of raw ``uint32_t``.
  See :ref:`generator_cpp` for usage details.

  * ``get/set_<register>`` methods now return/take a ``struct`` with field values.

    * New alternative methods ``get/set_<register>_raw`` return/take a raw
      ``uint32_t`` register value instead of the casted structure.

  * ``get/set_<field>`` methods work just as before.
  * ``get_<field>_from_value`` methods are removed.

* Represent :class:`.Bit` field values as ``bool`` in generated C++ API.

* Represent :class:`.BitVector` field values with numerical interpretation :class:`.Signed`
  as ``int32_t`` in generated C++ API.
  Also :class:`.UnsignedFixedPoint` and :class:`.SignedFixedPoint` as ``float``/``double``.

Breaking internal API changes

* Move :class:`.Register` properties ``utilized_width`` and ``default_value`` to
  :meth:`.RegisterCodeGeneratorHelpers.register_utilized_width`
  and :meth:`.RegisterCodeGeneratorHelpers.register_default_value_uint`.
