# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to be run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

"""
Configuration file for the Sphinx documentation builder.
"""

from pathlib import Path
import sys

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))
PATH_TO_TSFPGA = REPO_ROOT.parent.parent.resolve() / "tsfpga" / "tsfpga"
sys.path.insert(0, str(PATH_TO_TSFPGA))

project = "hdl_registers"
copyright = "Lukas Vik"
author = "Lukas Vik"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.graphviz",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "sphinx_sitemap",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hdl_modules": ("https://hdl-modules.com", None),
    "tsfpga": ("https://tsfpga.com", None),
}

# Base URL for generated sitemap XML
html_baseurl = "https://hdl-registers.com"

# Include robots.txt which points to sitemap
html_extra_path = ["robots.txt"]

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "prev_next_buttons_location": "both",
}


# Make autodoc include __init__ class method.
# https://stackoverflow.com/a/5599712


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
