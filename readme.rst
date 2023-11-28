.. image:: https://hdl-registers.com/logos/banner.png
  :alt: Project banner
  :align: center

|

.. |pic_website| image:: https://hdl-registers.com/badges/website.svg
  :alt: Website
  :target: https://hdl-registers.com

.. |pic_repository| image:: https://hdl-registers.com/badges/repository.svg
  :alt: Repository
  :target: https://gitlab.com/hdl_registers/hdl_registers

.. |pic_chat| image:: https://hdl-registers.com/badges/chat.svg
  :alt: Chat
  :target: https://app.gitter.im/#/room/#60a276916da03739847cca54:gitter.im

.. |pic_pip_install| image:: https://hdl-registers.com/badges/pip_install.svg
  :alt: pypi
  :target: https://pypi.org/project/hdl-registers/

.. |pic_license| image:: https://hdl-registers.com/badges/license.svg
  :alt: License
  :target: https://hdl-registers.com/license_information.html

.. |pic_python_line_coverage| image:: https://hdl-registers.com/badges/python_coverage.svg
  :alt: Python line coverage
  :target: https://hdl-registers.com/python_coverage_html

|pic_website| |pic_repository| |pic_chat| |pic_pip_install| |pic_license| |pic_python_line_coverage|

The hdl_registers project is an open-source HDL register code generator fast enough to run in
real time.
It makes FPGA/ASIC development more fun by automating a lot of time-consuming manual work.
It also minimizes the risk of bugs by removing the need for duplicate information.
`Read more <https://hdl-registers.com/rst/about/about.html>`_

**See documentation on the website**: https://hdl-registers.com

**See PyPI for installation details**: https://pypi.org/project/hdl-registers/

The following features are supported:

* Register fields

  * `Bit <https://hdl-registers.com/rst/field/field_bit.html>`_.
  * `Signed/unsigned fixed-point bit vector <https://hdl-registers.com/rst/field/field_bit_vector.html>`_.
  * `Enumeration <https://hdl-registers.com/rst/field/field_enumeration.html>`_.
  * `Positive/negative-range integer <https://hdl-registers.com/rst/field/field_integer.html>`_.

* `Register arrays <https://hdl-registers.com/rst/basic_feature/basic_feature_register_array.html>`_.
* `Default registers <https://hdl-registers.com/rst/basic_feature/basic_feature_default_registers.html>`_.
* `Register constants <https://hdl-registers.com/rst/constant/constant_overview.html>`_.

Registers can be defined using
a `TOML/JSON data file <https://hdl-registers.com/rst/user_guide/toml_format.html>`_
or the `Python API <https://hdl-registers.com/rst/user_guide/user_guide_python_api.html>`_.
The following code can be generated:

* `VHDL <https://hdl-registers.com/rst/generator/generator_vhdl.html>`_

  * AXI-Lite register file wrapper using native VHDL types for register fields.
  * Simulation support package.

* `C++ <https://hdl-registers.com/rst/generator/generator_cpp.html>`_

  * Abstract interface header for unit test mocking.
  * Class header.
  * Class implementation with setters and getters for registers and fields.

* `C header <https://hdl-registers.com/rst/generator/generator_c.html>`_
  with register addresses and field information.
* `HTML <https://hdl-registers.com/rst/generator/generator_html.html>`_
  website with documentation of registers and fields.

The tool can also be extended by
`writing your own code generator <https://hdl-registers.com/rst/extensions/extensions_custom_generator.html>`_
using a simple but powerful API.

This project is mature and used in many production environments.
The maintainers place high focus on quality, with everything having good unit test coverage and a
thought-out structure.
