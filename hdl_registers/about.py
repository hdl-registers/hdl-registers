# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

REPOSITORY_URL = "https://github.com/hdl-registers/hdl-registers"
WEBSITE_URL = "https://hdl-registers.com"


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
        extra_rst = f"""\
**See documentation on the website**: {WEBSITE_URL}

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
        extra_rst = f"""\
To install the Python package, see :ref:`installation`.
To check out the source code go to the
`GitHub page <{REPOSITORY_URL}>`__. \
"""
    elif include_extra_for_pypi:
        readme_rst = ""
        extra_rst = f"""\
**See documentation on the website**: {WEBSITE_URL}

**Check out the source code on GitHub**: {REPOSITORY_URL}

"""
    else:
        readme_rst = ""
        extra_rst = ""

    readme_rst += f"""\
.. image:: {WEBSITE_URL}/logos/banner.png
  :alt: Project banner
  :align: center

|

.. |pic_website| image:: {WEBSITE_URL}/badges/website.svg
  :alt: Website
  :target: {WEBSITE_URL}

.. |pic_repository| image:: {WEBSITE_URL}/badges/repository.svg
  :alt: Repository
  :target: {REPOSITORY_URL}

.. |pic_chat| image:: {WEBSITE_URL}/badges/chat.svg
  :alt: Chat
  :target: {REPOSITORY_URL}/discussions

.. |pic_pip_install| image:: {WEBSITE_URL}/badges/pip_install.svg
  :alt: pypi
  :target: https://pypi.org/project/hdl-registers/

.. |pic_license| image:: {WEBSITE_URL}/badges/license.svg
  :alt: License
  :target: {WEBSITE_URL}/rst/about/license_information.html

.. |pic_ci_status| image:: {REPOSITORY_URL}/actions/workflows/ci.yml/\
badge.svg?branch=main
  :alt: CI status
  :target: {REPOSITORY_URL}/actions/workflows/ci.yml

.. |pic_python_line_coverage| image:: {WEBSITE_URL}/badges/python_coverage.svg
  :alt: Python line coverage
  :target: {WEBSITE_URL}/python_coverage_html

|pic_website| |pic_repository| |pic_pip_install| |pic_license| |pic_chat| |pic_ci_status|
|pic_python_line_coverage|

The hdl-registers project is an open-source HDL register interface code generator fast enough to run
in real time.
It makes FPGA/ASIC development more fun by automating a lot of time-consuming manual work.
It also minimizes the risk of bugs by removing the need for duplicate information.
`Read more <{WEBSITE_URL}/rst/about/about.html>`_

{extra_rst}The following features are supported:

* Register fields

  * `Bit <{WEBSITE_URL}/rst/field/field_bit.html>`_.
  * `Signed/unsigned fixed-point bit vector <{WEBSITE_URL}/rst/field/field_bit_vector.html>`_.
  * `Enumeration <{WEBSITE_URL}/rst/field/field_enumeration.html>`_.
  * `Positive/negative-range integer <{WEBSITE_URL}/rst/field/field_integer.html>`_.

* `Register arrays <{WEBSITE_URL}/rst/basic_feature/basic_feature_register_array.html>`_.
* `Default registers <{WEBSITE_URL}/rst/basic_feature/basic_feature_default_registers.html>`_.
* `Register constants <{WEBSITE_URL}/rst/constant/constant_overview.html>`_.

Registers can be defined using
a `TOML/JSON/YAML data file <{WEBSITE_URL}/rst/user_guide/toml_format.html>`_
or the `Python API <{WEBSITE_URL}/rst/user_guide/user_guide_python_api.html>`_.
The following code can be generated:

* `VHDL <{WEBSITE_URL}/rst/generator/generator_vhdl.html>`_

  * AXI-Lite register file wrapper using records and native VHDL types for values.
  * Simulation support packages for compact read/write/wait/checking of register and field values.

* `C++ <{WEBSITE_URL}/rst/generator/generator_cpp.html>`_

  * Complete class with setters and getters for registers and fields.
  * Includes an abstract interface header for unit test mocking.

* `C header <{WEBSITE_URL}/rst/generator/generator_c.html>`_
  with register addresses and field information.

* `HTML <{WEBSITE_URL}/rst/generator/generator_html.html>`_
  website with documentation of registers and fields.

* `Python <{WEBSITE_URL}/rst/generator/generator_python.html>`_
  class with methods to read/write/print each register and field on a target device.

The tool can also be extended by
`writing your own code generator <{WEBSITE_URL}/rst/extensions/extensions_custom_generator.html>`_
using a simple but powerful API.

This project is mature and used in many production environments.
The maintainers place high focus on quality, with everything having good unit test coverage and a
thought-out structure.
"""

    return readme_rst
