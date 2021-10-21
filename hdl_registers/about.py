# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

from tsfpga.system_utils import create_file, read_file

import hdl_registers


def get_slogan():
    return (
        "The hdl_registers project is a HDL register generator fast enough to be run in real time."
    )


def get_readme_rst(include_website_link, verify=True):
    """
    Get the complete README.rst (to be used on website and in PyPI release).

    Also possible to verify that readme.rst in the project root is identical.
    RST file inclusion in README.rst does not work on gitlab unfortunately, hence this
    cumbersome handling where the README is duplicated in two places.

    Arguments:
        include_website_link (bool): Include a link to the website in README.
        verify (bool): Verify that the readme.rst in repo root (which is shown on gitlab)
            corresponds to the string produced by this function.
    """

    def get_rst(include_link):
        extra_rst = (
            "**See documentation on the website**: https://hdl-modules.com\n"
            if include_link
            else ""
        )
        readme_rst = f"""\
About ``hdl_registers``
=======================

|pic_website| |pic_gitlab| |pic_gitter| |pic_license|

.. |pic_website| image:: https://hdl-registers.com/badges/website.svg
  :alt: Website
  :target: https://hdl-registers.com

.. |pic_gitlab| image:: https://hdl-registers.com/badges/gitlab.svg
  :alt: Gitlab
  :target: https://gitlab.com/tsfpga/hdl_registers

.. |pic_gitter| image:: https://badges.gitter.im/owner/repo.png
  :alt: Gitter
  :target: https://gitter.im/tsfpga/tsfpga

.. |pic_license| image:: https://hdl-registers.com/badges/license.svg
  :alt: License
  :target: https://hdl-registers.com/license_information.html

{get_slogan()}
{extra_rst}

TBC...
"""

        return readme_rst

    if verify:
        readme_rst = get_rst(include_link=True)
        if read_file(hdl_registers.REPO_ROOT / "readme.rst") != readme_rst:
            file_path = hdl_registers.HDL_REGISTERS_GENERATED / "sphinx" / "readme.rst", readme_rst
            create_file(file_path)
            assert (
                False
            ), f"readme.rst in repo root not correct. Compare to reference in python: {file_path}"

    return get_rst(include_link=include_website_link)
