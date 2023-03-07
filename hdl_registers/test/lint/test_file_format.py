# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
from tsfpga.git_utils import find_git_files
from tsfpga.test.lint.test_file_format import (
    check_file_ends_with_newline,
    check_file_for_carriage_return,
    check_file_for_line_length,
    check_file_for_tab_character,
    check_file_for_trailing_whitespace,
    open_file_with_encoding,
)

# First party libraries
from hdl_registers import HDL_REGISTERS_DOC, REPO_ROOT


def test_all_checked_in_files_are_properly_encoded():
    """
    To avoid problems with different editors and different file encodings, all checked in files
    should contain only ASCII characters.
    """
    for file in files_to_test():
        open_file_with_encoding(file)


def test_all_checked_in_files_end_with_newline():
    """
    All checked in files should end with a UNIX style line break (\n).
    Otherwise UNIX doesn't consider them actual text files.
    """
    test_ok = True
    for file in files_to_test():
        test_ok &= check_file_ends_with_newline(file)
    assert test_ok


def test_no_checked_in_files_contain_tabs():
    """
    To avoid problems with files looking different in different editors, no checked in files may
    contain TAB characters.
    """
    test_ok = True
    for file in files_to_test():
        test_ok &= check_file_for_tab_character(file)
    assert test_ok


def test_no_checked_in_files_contain_carriage_return():
    """
    All checked in files should use UNIX style line breaks (\n not \r\n). Some Linux editors and
    tools will display or interpret the \r as something other than a line break.
    """
    test_ok = True
    for file in files_to_test():
        test_ok &= check_file_for_carriage_return(file)
    assert test_ok


def test_no_checked_in_files_contain_trailing_whitespace():
    """
    Trailing whitespace is not allowed. Some motivation here:
    https://softwareengineering.stackexchange.com/questions/121555
    """
    test_ok = True
    for file in files_to_test():
        test_ok &= check_file_for_trailing_whitespace(file)
    assert test_ok


def test_no_checked_in_files_have_too_long_lines():
    test_ok = True
    excludes = [
        # YAML format seems hard to break lines in
        REPO_ROOT / ".gitlab-ci.yml",
        # We list the license text exactly as the original, with no line breaks
        REPO_ROOT / "license.txt",
        # Impossible to break RST syntax
        REPO_ROOT / "readme.rst",
        HDL_REGISTERS_DOC / "sphinx" / "html_generator.rst",
    ]
    for file_path in files_to_test(excludes=excludes):
        test_ok &= check_file_for_line_length(file_path=file_path)

    assert test_ok


def files_to_test(excludes=None):
    excludes = [] if excludes is None else excludes
    # Do not test binary image files
    return find_git_files(
        directory=REPO_ROOT,
        exclude_directories=excludes,
        file_endings_avoid=("png", "svg"),
    )
