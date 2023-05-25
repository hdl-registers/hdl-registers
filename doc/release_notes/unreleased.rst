Breaking changes

* Break ``hdl_registers.constant.Constant`` class into :class:`.BooleanConstant`,
  :class:`.FloatConstant`, :class:`.IntegerConstant` and :class:`.StringConstant`.

* Remove the largely unused "Value (hexadecimal)" constant information column from HTML generator.

Added

* Add support for unsigned bit vector constants via the :class:`.UnsignedVectorConstant` class.
