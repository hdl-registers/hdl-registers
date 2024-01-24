# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------


def get_short_slogan() -> str:
    """
    Short slogan used e.g. on pypi.org.
    Note that there seems to be an upper limit of 98 characters when rendering the slogan
    on pypi.org.

    Note that this slogan should be the same as the one used in the readme and on the website below.
    The difference is capitalization and whether the project name is included.
    """
    result = "An open-source HDL register interface code generator fast enough to run in real time"
    return result


def get_readme_rst(
    include_extra_for_github: bool = False,
    include_extra_for_website: bool = False,
    include_extra_for_pypi: bool = False,
) -> str:
    """
    Get the complete README.rst (to be used on website and in PyPI release).
    RST file inclusion in README.rst does not work on GitHub unfortunately, hence this
    cumbersome handling where the README is duplicated in two places.

    The arguments control some extra text that is included. This is mainly links to the
    other places where you can find information on the project (website, GitHub, PyPI).

    Arguments:
        include_extra_for_github (bool): Include the extra text that shall be included in the
            GitHub README.
        include_extra_for_website (bool): Include the extra text that shall be included in the
            website main page.
        include_extra_for_pypi (bool): Include the extra text that shall be included in the
            PyPI release README.
    """
    if include_extra_for_github:
        readme_rst = ""
        extra_rst = """\
**See documentation on the website**: https://hdl-registers.com

"""
    elif include_extra_for_website:
        # The website needs the initial heading, in order for the landing page to get
        # the correct title.
        # The others do not need this initial heading, it just makes the GitHub/PyPI page
        # more clunky.
        readme_rst = """\
About hdl-registers
===================

"""
        extra_rst = """\
To install the Python package, see :ref:`installation`.
To check out the source code go to the
`GitHub page <https://github.com/hdl-registers/hdl-registers>`__. \
"""
    elif include_extra_for_pypi:
        readme_rst = ""
        extra_rst = """\
**See documentation on the website**: https://hdl-registers.com

**Check out the source code on GitHub**: https://github.com/hdl-registers/hdl-registers

"""
    else:
        readme_rst = ""
        extra_rst = ""

    readme_rst += f"""\
.. image:: https://hdl-registers.com/logos/banner.png
  :alt: Project banner
  :align: center

|

.. |pic_website| image:: https://hdl-registers.com/badges/website.svg
  :alt: Website
  :target: https://hdl-registers.com

.. |pic_repository| image:: https://hdl-registers.com/badges/repository.svg
  :alt: Repository
  :target: https://github.com/hdl-registers/hdl-registers

.. |pic_chat| image:: https://hdl-registers.com/badges/chat.svg
  :alt: Chat
  :target: https://github.com/hdl-registers/hdl-registers/discussions

.. |pic_pip_install| image:: https://hdl-registers.com/badges/pip_install.svg
  :alt: pypi
  :target: https://pypi.org/project/hdl-registers/

.. |pic_license| image:: https://hdl-registers.com/badges/license.svg
  :alt: License
  :target: https://hdl-registers.com/rst/about/license_information.html

.. |pic_ci_status| image:: https://github.com/hdl-registers/hdl-registers/actions/workflows/ci.yml/\
badge.svg?branch=main
  :alt: CI status
  :target: https://github.com/hdl-registers/hdl-registers/actions/workflows/ci.yml

.. |pic_python_line_coverage| image:: https://hdl-registers.com/badges/python_coverage.svg
  :alt: Python line coverage
  :target: https://hdl-registers.com/python_coverage_html

|pic_website| |pic_repository| |pic_pip_install| |pic_license| |pic_chat| |pic_ci_status|
|pic_python_line_coverage|

The hdl-registers project is an open-source HDL register interface code generator fast enough to run
in real time.
It makes FPGA/ASIC development more fun by automating a lot of time-consuming manual work.
It also minimizes the risk of bugs by removing the need for duplicate information.
`Read more <https://hdl-registers.com/rst/about/about.html>`_

{extra_rst}The following features are supported:

* Register fields

  * `Bit <https://hdl-registers.com/rst/field/field_bit.html>`_.
  * `Signed/unsigned fixed-point bit vector \
<https://hdl-registers.com/rst/field/field_bit_vector.html>`_.
  * `Enumeration <https://hdl-registers.com/rst/field/field_enumeration.html>`_.
  * `Positive/negative-range integer <https://hdl-registers.com/rst/field/field_integer.html>`_.

* `Register arrays \
<https://hdl-registers.com/rst/basic_feature/basic_feature_register_array.html>`_.
* `Default registers \
<https://hdl-registers.com/rst/basic_feature/basic_feature_default_registers.html>`_.
* `Register constants <https://hdl-registers.com/rst/constant/constant_overview.html>`_.

Registers can be defined using
a `TOML/JSON/YAML data file <https://hdl-registers.com/rst/user_guide/toml_format.html>`_
or the `Python API <https://hdl-registers.com/rst/user_guide/user_guide_python_api.html>`_.
The following code can be generated:

* `VHDL <https://hdl-registers.com/rst/generator/generator_vhdl.html>`_

  * AXI-Lite register file wrapper using records and native VHDL types for values.
  * Support packages for compact and efficient simulation.

* `C++ <https://hdl-registers.com/rst/generator/generator_cpp.html>`_

  * Complete class with setters and getters for registers and fields.
  * Includes an abstract interface header for unit test mocking.

* `C header <https://hdl-registers.com/rst/generator/generator_c.html>`_
  with register addresses and field information.
* `HTML <https://hdl-registers.com/rst/generator/generator_html.html>`_
  website with documentation of registers and fields.

The tool can also be extended by
`writing your own code generator \
<https://hdl-registers.com/rst/extensions/extensions_custom_generator.html>`_
using a simple but powerful API.

This project is mature and used in many production environments.
The maintainers place high focus on quality, with everything having good unit test coverage and a
thought-out structure.
"""

    return readme_rst
