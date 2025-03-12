# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from tsfpga.git_utils import find_git_files
from tsfpga.test.lint.file_format_lint import (
    check_file_ends_with_newline,
    check_file_for_carriage_return,
    check_file_for_line_length,
    check_file_for_tab_character,
    check_file_for_trailing_whitespace,
    open_file_with_encoding,
)

from hdl_registers import HDL_REGISTERS_DOC, HDL_REGISTERS_TESTS, HDL_REGISTERS_TOOLS, REPO_ROOT


def test_all_checked_in_files_are_properly_encoded():
    """
    To avoid problems with different editors and different file encodings, all checked in files
    should contain only ASCII characters.
    """
    for file_path in files_to_test():
        open_file_with_encoding(file_path)


def test_all_checked_in_files_end_with_newline():
    r"""
    All checked in files should end with a UNIX style line break (\n).
    Otherwise UNIX doesn't consider them actual text files.
    """
    # VSCode JSON auto formatter removes newline.
    excludes = [
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "user_guide" / "json" / "toml_format.json",
        HDL_REGISTERS_TOOLS / "benchmark" / "corsair" / "corsair_regs.json",
    ]

    test_ok = True
    for file_path in files_to_test(excludes=excludes):
        test_ok &= check_file_ends_with_newline(file_path)

    assert test_ok


def test_no_checked_in_files_contain_tabs():
    """
    To avoid problems with files looking different in different editors, no checked in files may
    contain TAB characters.
    """
    test_ok = True
    for file_path in files_to_test():
        test_ok &= check_file_for_tab_character(file_path)

    assert test_ok


def test_no_checked_in_files_contain_carriage_return():
    r"""
    All checked in files should use UNIX style line breaks (\n not \r\n). Some Linux editors and
    tools will display or interpret the \r as something other than a line break.
    """
    test_ok = True
    for file_path in files_to_test():
        test_ok &= check_file_for_carriage_return(file_path)

    assert test_ok


def test_no_checked_in_files_contain_trailing_whitespace():
    """
    Trailing whitespace is not allowed. Some motivation here:
    https://softwareengineering.stackexchange.com/questions/121555
    """
    test_ok = True
    for file_path in files_to_test():
        test_ok &= check_file_for_trailing_whitespace(file_path)

    assert test_ok


def test_no_checked_in_files_have_too_long_lines():
    test_ok = True
    excludes = [
        # Can not break long commands on Windows.
        REPO_ROOT / ".github" / "workflows" / "ci.yml",
        # We list the license text exactly as the original, with no line breaks.
        REPO_ROOT / "license.txt",
        # Impossible to break RST syntax.
        REPO_ROOT / "readme.rst",
        HDL_REGISTERS_DOC
        / "sphinx"
        / "rst"
        / "basic_feature"
        / "basic_feature_default_registers.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "about" / "about.rst",
        HDL_REGISTERS_DOC
        / "sphinx"
        / "rst"
        / "api_reference"
        / "hdl_registers.generator.systemverilog.axi_lite.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "basic_feature" / "basic_feature_register_array.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "basic_feature" / "basic_feature_register_modes.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "constant" / "constant_bit_vector.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "constant" / "constant_boolean.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "constant" / "constant_float.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "constant" / "constant_integer.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "constant" / "constant_string.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "extensions" / "extensions_custom_generator.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "field" / "field_bit_vector.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "field" / "field_bit.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "field" / "field_enumeration.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "field" / "field_integer.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "generator_c.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "generator_cpp.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "generator_html.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "generator_python.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "generator_systemverilog.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "generator_vhdl.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "user_guide" / "getting_started.rst",
        HDL_REGISTERS_DOC / "sphinx" / "rst" / "user_guide" / "user_guide_python_api.rst",
        HDL_REGISTERS_TESTS / "functional" / "gcc" / "c" / "test_registers.c",
        HDL_REGISTERS_TESTS / "functional" / "gcc" / "cpp" / "test_registers.cpp",
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
