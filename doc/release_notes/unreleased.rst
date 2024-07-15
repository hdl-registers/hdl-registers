Breaking changes

* Update data file (TOML, JSON, etc) format in way that is not compatible with old files.
  See :ref:`new_data_file_format`.
  Note that old files are automatically updated.
  This change enables:

  * Arbitrary ordering and grouping of registers and register arrays.

  * Arbitrary ordering and grouping of fields in a register.

* Rename :meth:`.RegisterList.get_register` argument ``name`` to ``register_name``.

* Remove :class:`.RegisterField` attributes ``range_str`` and ``default_value_str``.
  This information is now calculated internally in the HTML generator class.

* Rename :meth:`.Enumeration.set_default_value` argument ``value`` to the more correct ``name``.

* Rework register mode handling to use objects with properties instead of magic strings.

  * Change :meth:`.Register.__init__`, :meth:`.RegisterList.append_register`, and
    :meth:`.RegisterArray.append_register` arguments ``mode`` to be of type :class:`.RegisterMode`
    instead of ``str``.

  * Move :class:`.RegisterMode` to :mod:`.register_mode` and ``REGISTER_MODES``
    to :mod:`.register_modes`.

  * Rename :class:`.RegisterMode` property ``mode_readable`` to ``name``.

  * Remove :class:`.Register` properties ``is_bus_readable`` and ``is_bus_writeable`` in favor
    of :attr:`.Register.mode`.

  * Use :attr:`.Register.mode` instead of generator-specific properties/checkers
    in :class:`.VhdlGeneratorCommon`.

* Rework the system for numerical interpretation of bit vector field values.

  * Remove ``field_type`` member from :class:`.Bit`, :class:`.Enumeration`, and :class:`.Integer`.

  * Rename ``FieldType`` class to :class:`.NumericalInterpretation`.

  * Rename ``field_type`` member of :class:`.BitVector`
    to :attr:`.BitVector.numerical_interpretation`.

  * Rename ``field_type`` argument of :meth:`.BitVector.__init__` and
    :meth:`.Register.append_bit_vector` to ``numerical_interpretation``.

  * Remove ``min_value`` and ``max_value`` properties from :class:`.BitVector`.
    Use :attr:`.BitVector.numerical_interpretation` instead.

  * Remove ``bit_width`` argument from :meth:`.NumericalInterpretation.min_value`,
    :attr:`.NumericalInterpretation.max_value`,
    :meth:`.NumericalInterpretation.convert_from_unsigned_binary`,
    and :meth:`.NumericalInterpretation.convert_to_unsigned_binary`.
    Add ``bit_width`` argument to :meth:`.Unsigned.__init__` and :meth:`.Signed.__init__`.

  * Remove ``is_signed`` and ``max_binary_value`` properties of :class:`.RegisterField`.
    ``is_signed`` is still present for :class:`.Integer`.
    Bit vectors should use :attr:`.BitVector.numerical_interpretation`.
