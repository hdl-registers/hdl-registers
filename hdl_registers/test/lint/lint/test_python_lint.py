# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

from tsfpga.git_utils import find_git_files
from tsfpga.test.lint.test_python_lint import run_black, run_flake8_lint, run_pylint

from hdl_registers import REPO_ROOT, HDL_REGISTERS_DOC


def _files_to_test():
    # Exclude doc folder, since conf.py used by sphinx does not conform
    return [
        str(path)
        for path in find_git_files(
            directory=REPO_ROOT,
            exclude_directories=[HDL_REGISTERS_DOC],
            file_endings_include="py",
        )
    ]


def test_pylint():
    run_pylint(_files_to_test())


def test_flake8_lint():
    run_flake8_lint(_files_to_test())


def test_black_formatting():
    run_black(_files_to_test())
