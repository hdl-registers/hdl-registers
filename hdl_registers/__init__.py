# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
HDL_REGISTERS_PATH = REPO_ROOT / "hdl_registers"
HDL_REGISTERS_DOC = REPO_ROOT / "doc"

__version__ = "1.0.5"
