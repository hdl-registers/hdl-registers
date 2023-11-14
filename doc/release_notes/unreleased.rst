Fixes

* Fix "multiple definition" bug in generated C header for a string constant.
* Decrease :class:`.RegisterList` hash calculation time by 40%.
  Improves performance of :meth:`.RegisterCodeGenerator.should_create`.


Added

* Add generation of register records with natively-typed members for each register
  field to :class:`.VhdlRecordPackageGenerator`.

* Add generation of a wrapper around :ref:`reg_file.axi_lite_reg_file` to
  :class:`.VhdlAxiLiteWrapperGenerator`.

  * Sets correct generics and uses the natively typed records from
    :class:`.VhdlRecordPackageGenerator` for its up/down register values.

* Add generation of simulation package for reading/writing registers via VUnit
  Verification Components to :class:`.VhdlSimulationPackageGenerator`.

  * Uses the natively typed records from
    :class:`.VhdlRecordPackageGenerator` for register values.


Breaking changes

* Rename VHDL field conversion function for enumerations from ``to_<field name>_slv`` to ``to_slv``.
* Rework code generator API for better performance and scalability.

  * Remove ``copy_source_definition`` method from :class:`.RegisterList`.
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
