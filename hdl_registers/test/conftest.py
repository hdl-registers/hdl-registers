# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to be run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

import sys

from pathlib import Path

# Many tests use helper methods from tsfpga.
# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.parent
PATH_TO_TSFPGA = REPO_ROOT.parent.parent.resolve() / "tsfpga" / "tsfpga"
sys.path.insert(0, str(PATH_TO_TSFPGA))

# pylint: disable=unused-import
from tsfpga.test.conftest import fixture_tmp_path  # noqa: F401
