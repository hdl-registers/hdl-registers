# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

"""
Import this file to have the default paths of some third party packages added to PYTHONPATH.
"""

# Standard libraries
import sys
from pathlib import Path

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install.

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Paths e.g.
# repo/hdl-registers/hdl-registers
# repo/tsfpga/tsfpga
PATH_TO_TSFPGA = REPO_ROOT.parent.parent.resolve() / "tsfpga" / "tsfpga"
sys.path.insert(0, str(PATH_TO_TSFPGA))

# Paths e.g.
# repo/hdl-registers/hdl-registers
# repo/hdl-modules/hdl-modules
PATH_TO_HDL_MODULES = REPO_ROOT.parent.parent.resolve() / "hdl-modules" / "hdl-modules"
sys.path.insert(0, str(PATH_TO_HDL_MODULES))

# Paths e.g.
# repo/hdl-registers/hdl-registers
# repo/vunit/vunit
PATH_TO_VUNIT = REPO_ROOT.parent.parent.resolve() / "vunit" / "vunit"
sys.path.insert(0, str(PATH_TO_VUNIT))
