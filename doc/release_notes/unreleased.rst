Fixes

* Fix bug where :meth:`.RegisterField.get_value` and :meth:`.RegisterField.set_value` would crash
  for negative-range integer fields.
* Fix "multiple definition" bug in generated C header for a string constant.
* Fix C++ field setters on registers of mode ``w``, ``wpulse`` and ``r_wpulse`` not taking into
  account non-zero default values of other fields.
* Decrease :meth:`.RegisterList.object_hash` calculation time by 40%.
  Improves performance of :meth:`.RegisterCodeGenerator.should_create`.
* Improve TOML parsing performance by a factor of ~8 by switching to ``rtoml`` instead of
  ``tomli`` package.


Added

* Add support for parsing JSON and YAML data files, see :ref:`here <toml_format>`.

* Add generation of register records with natively-typed members for each register
  field to :class:`.VhdlRecordPackageGenerator`.

* Add generation of simulation support package to :class:`.VhdlSimulationReadWritePackageGenerator`.

  * Uses VUnit Verification Components for bus operations.

  * Uses the natively typed records from :class:`.VhdlRecordPackageGenerator` for values.

  * Generates the following procedures:

    * Read/write for each register.

    * Read/write for each field.

* Add generation of simulation support package to :class:`.VhdlSimulationWaitUntilPackageGenerator`.

  * Uses VUnit Verification Components for bus operations.

  * Uses the natively typed records from :class:`.VhdlRecordPackageGenerator` for values.

  * Generates the following procedures:

    * Wait until register equals for each register.

    * Wait until field equals for each register.

* Add generation of a wrapper around :ref:`reg_file.axi_lite_reg_file` to
  :class:`.VhdlAxiLiteWrapperGenerator`.

  * Sets correct generics and uses the natively typed records from
    :class:`.VhdlRecordPackageGenerator` for its up/down register values.

* Add checks to :meth:`.Integer.get_value` and :meth:`.Integer.set_value` that values are within
  the configured range of the field.


Breaking changes

* Move :class:`.RegisterParser` to sub-package ``hdl_registers.parser``.
  Break out :func:`.from_toml` to separate Python module :mod:`hdl_registers.parser.toml`.
* Rename ``module_name`` argument of :class:`.RegisterParser` and :func:`.from_toml` to ``name``.
* Rename VHDL field conversion function for enumerations from ``to_<field name>_slv`` to ``to_slv``.
* Remove C++ interface header constant ``<register array name>_array_length``.
  Information is instead available as an
  attribute ``fpga_regs::<module name>::<register array name>::array_length``.
* Rework code generator API for better performance and scalability.

  * Remove public members ``copy_source_definition``, ``generated_info``, ``generated_source_info``
    from :class:`.RegisterList`.
  * Remove ``create_vhdl_package`` method from :class:`.RegisterList`.
    Move ``hdl_registers.register_vhdl_generator.RegisterVhdlGenerator`` class to
    :class:`.VhdlRegisterPackageGenerator` and update API.
    See :ref:`generator_vhdl` for usage details.
  * Remove ``create_c_header`` method from :class:`.RegisterList`.
    Move ``hdl_registers.register_c_generator.RegisterCGenerator`` class to
    :class:`.CHeaderGenerator` and update API.
    See :ref:`generator_c` for usage details.
  * Remove ``create_cpp_interface``, ``create_cpp_header`` and
    ``create_cpp_implementation`` methods from :class:`.RegisterList`.
    Move ``hdl_registers.register_cpp_generator.RegisterCppGenerator`` class to
    :class:`.CppInterfaceGenerator`, :class:`.CppHeaderGenerator`,
    and :class:`.CppImplementationGenerator`, and update API.
    See :ref:`generator_cpp` for usage details.
  * Remove ``create_html_page``, ``create_html_register_table`` and
    ``create_html_constant_table`` methods from :class:`.RegisterList`.
    Move ``hdl_registers.register_html_generator.RegisterHtmlGenerator`` class to
    :class:`.HtmlPageGenerator`, :class:`.HtmlRegisterTableGenerator`,
    and :class:`.HtmlConstantTableGenerator`, and update API.
    See :ref:`generator_html` for usage details.
  * Remove ``create_python_class`` method from :class:`.RegisterList`.
    Move ``hdl_registers.register_python_generator.RegisterPythonGenerator`` class to
    :class:`.PythonClassGenerator` and update API.
    See :ref:`generator_python` for usage details.
