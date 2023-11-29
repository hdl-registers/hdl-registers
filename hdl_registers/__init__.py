# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path

# Local folder libraries
from .about import get_short_slogan

REPO_ROOT = Path(__file__).parent.parent.resolve()

HDL_REGISTERS_PATH = REPO_ROOT / "hdl_registers"
HDL_REGISTERS_DOC = REPO_ROOT / "doc"
HDL_REGISTERS_GENERATED = REPO_ROOT / "generated"
HDL_REGISTERS_TEST = HDL_REGISTERS_PATH / "test"
HDL_REGISTERS_TOOLS = REPO_ROOT / "tools"

__version__ = "4.1.1-dev2"
__doc__ = get_short_slogan()  # pylint: disable=redefined-builtin
