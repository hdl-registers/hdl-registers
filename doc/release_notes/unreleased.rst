Breaking changes

* Break up ``hdl_registers.Constant`` class into :class:`.BooleanConstant`,
  :class:`.FloatConstant`, :class:`.IntegerConstant` and :class:`.StringConstant`
  that are placed in new ``constant`` sub-package.

* Move :class:`.BitVector`, :class:`.Bit`, :class:`.RegisterField`, classes
  and :py:mod:`.register_field_type` module from top-level to ``field`` sub-package.

* Move :class:`.HtmlTranslator`, :class:`.RegisterCGenerator`, :class:`.RegisterCodeGenerator`,
  :class:`.RegisterCppGenerator`, :class:`.RegisterHtmlGenerator`, :class:`.RegisterPythonGenerator`
  and :class:`.RegisterVhdlGenerator` classes from top-level to ``generator`` sub-package.

* Remove the largely unused "Value (hexadecimal)" constant information column from HTML generator.

* Rename ``RegisterField.range`` to :meth:`.RegisterField.range_str`.

Added

* Add support for unsigned bit vector constants via the :class:`.UnsignedVectorConstant` class.
