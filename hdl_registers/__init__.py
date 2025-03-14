# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from pathlib import Path

from .about import get_short_slogan

REPO_ROOT = Path(__file__).parent.parent.resolve()

HDL_REGISTERS_PATH = REPO_ROOT / "hdl_registers"
HDL_REGISTERS_DOC = REPO_ROOT / "doc"
HDL_REGISTERS_GENERATED = REPO_ROOT / "generated"
HDL_REGISTERS_TESTS = REPO_ROOT / "tests"
HDL_REGISTERS_TOOLS = REPO_ROOT / "tools"

__version__ = "7.2.0"

# We have the slogan in one place only, instead of repeating it here in a proper docstring.
__doc__ = get_short_slogan()
