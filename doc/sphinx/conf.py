# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

"""
Configuration file for the Sphinx documentation builder.
"""

# Standard libraries
import sys
from pathlib import Path

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH. pylint: disable=unused-import
import tools.tools_pythonpath  # noqa: F401

project = "hdl-registers"
copyright = "Lukas Vik"
author = "Lukas Vik"

extensions = [
    "sphinx_rtd_theme",
    "sphinx_sitemap",
    "sphinx_toolbox.collapse",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hdl_modules": ("https://hdl-modules.com", None),
    "tsfpga": ("https://tsfpga.com", None),
}

# Base URL for generated sitemap XML
html_baseurl = "https://hdl-registers.com/"

# Include robots.txt which points to sitemap
html_extra_path = ["robots.txt"]

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "prev_next_buttons_location": "both",
    "analytics_id": "G-GN3TVQGSHC",
    "logo_only": True,
}

html_logo = "hdl_registers_sphinx.png"

# These folders are copied to the documentation's HTML output
html_static_path = ["css"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    # A hack to get the table captions below the table.
    # Per instructions at
    # https://stackoverflow.com/questions/69845499/
    "docutils_table_caption_below.css",
]


# Make autodoc include __init__ class method.
# https://stackoverflow.com/a/5599712


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
