# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
HDL_REGISTERS_PATH = REPO_ROOT / "hdl_registers"
HDL_REGISTERS_DOC = REPO_ROOT / "doc"

__version__ = "1.0.5"
