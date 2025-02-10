# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import sys

from tsfpga.system_utils import run_command

from hdl_registers import REPO_ROOT


def _run_ruff(command: list[str]):
    run_command([sys.executable, "-m", "ruff", *command], cwd=REPO_ROOT)


def test_ruff_check():
    _run_ruff(command=["check"])


def test_ruff_format():
    _run_ruff(command=["format", "--check", "--diff"])
