Fixes

* Use ``double`` data type for generated C/C++ header floating-point constants.
  Matches the precision in the generated VHDL code.

Breaking changes

* Break up ``hdl_registers.Constant`` class into :class:`.BooleanConstant`,
  :class:`.FloatConstant`, :class:`.IntegerConstant` and :class:`.StringConstant`
  that are placed in new ``constant`` sub-package.

* Move :class:`.BitVector`, :class:`.Bit` and :class:`.RegisterField` classes
  and :py:mod:`.register_field_type` module from top-level to ``field`` sub-package.

* Move :class:`.HtmlTranslator`, :class:`.RegisterCGenerator`, :class:`.RegisterCodeGenerator`,
  :class:`.RegisterCppGenerator`, :class:`.RegisterHtmlGenerator`, :class:`.RegisterPythonGenerator`
  and :class:`.RegisterVhdlGenerator` classes from top-level to ``generator`` sub-package.

* Rename ``RegisterField.range`` to :meth:`.RegisterField.range_str`.

* Remove default value ``description=None`` for argument to :meth:`.RegisterList.add_constant`.

* Remove public method ``vhdl_typedef`` from :class:`.FieldType` class.
  This logic is instead moved to :class:`.RegisterVhdlGenerator`.

* Remove the largely unused "Value (hexadecimal)" constant information column from HTML generator.

* Remove textual descriptions of registers/arrays/fields/constants from generated C header.

Added

* Add support for unsigned bit vector constants via the :class:`.UnsignedVectorConstant` class.

* Add support for ranged integer register fields via the :class:`.Integer` class.

* Add support for enumeration register fields via the :class:`.Enumeration` class.
