# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------


# Third party libraries
import pytest
from tsfpga.system_utils import read_file

# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def default_accessor_py(generate_default_accessor) -> str:
    """
    Get the python code of the default accessor class.
    Can also be shared in the whole module since no data is changed.
    """
    tmp_session_path, _ = generate_default_accessor
    return read_file(tmp_session_path / "test_accessor.py")


def test_correct_methods_for_r_register(default_accessor_py):
    assert "def read_reg_r(" in default_accessor_py
    assert "def write_reg_r(" not in default_accessor_py
    assert "def write_reg_r_bit_aa0(" not in default_accessor_py


def test_correct_methods_for_w_register(default_accessor_py):
    assert "def read_reg_w(" not in default_accessor_py
    assert "def write_reg_w(" in default_accessor_py
    assert "def write_reg_w_bit_aa0(" in default_accessor_py


def test_correct_methods_for_r_w_register(default_accessor_py):
    assert "def read_reg_r_w(" in default_accessor_py
    assert "def write_reg_r_w(" in default_accessor_py
    assert "def write_reg_r_w_bit_aa0(" in default_accessor_py


def test_correct_methods_for_wpulse_register(default_accessor_py):
    assert "def read_reg_wpulse(" not in default_accessor_py
    assert "def write_reg_wpulse(" in default_accessor_py
    assert "def write_reg_wpulse_bit_aa0(" in default_accessor_py


def test_correct_methods_for_r_wpulse_register(default_accessor_py):
    assert "def read_reg_r_wpulse(" in default_accessor_py
    assert "def write_reg_r_wpulse(" in default_accessor_py
    assert "def write_reg_r_wpulse_bit_aa0(" in default_accessor_py
