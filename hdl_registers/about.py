# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------


def get_slogan():
    return (
        "The hdl_registers project is a HDL register generator "
        "fast enough to be run in real time."
    )


def get_readme_rst(include_website_link):
    """
    Get the complete README.rst (to be used on website and in PyPI release).
    RST file inclusion in README.rst does not work on gitlab unfortunately, hence this
    cumbersome handling where the README is duplicated in two places.

    Arguments:
        include_website_link (bool): Include a link to the website in README.
    """

    extra_rst = (
        "**See documentation on the website**: https://hdl-registers.com\n"
        if include_website_link
        else ""
    )

    readme_rst = f"""\
About ``hdl_registers``
=======================

|pic_website| |pic_gitlab| |pic_gitter| |pic_pip_install| |pic_license| |pic_python_line_coverage|

.. |pic_website| image:: https://hdl-registers.com/badges/website.svg
  :alt: Website
  :target: https://hdl-registers.com

.. |pic_gitlab| image:: https://hdl-registers.com/badges/gitlab.svg
  :alt: Gitlab
  :target: https://gitlab.com/tsfpga/hdl_registers

.. |pic_gitter| image:: https://badges.gitter.im/owner/repo.png
  :alt: Gitter
  :target: https://gitter.im/tsfpga/tsfpga

.. |pic_pip_install| image:: https://hdl-registers.com/badges/pip_install.svg
  :alt: pypi
  :target: https://pypi.org/project/hdl-registers/

.. |pic_license| image:: https://hdl-registers.com/badges/license.svg
  :alt: License
  :target: https://hdl-registers.com/license_information.html

.. |pic_python_line_coverage| image:: https://hdl-registers.com/badges/python_coverage.svg
  :alt: Python line coverage
  :target: https://hdl-registers.com/python_coverage_html

{get_slogan()}

{extra_rst}
TBC...
"""

    return readme_rst
