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
from tsfpga.system_utils import load_python_module

# First party libraries
from hdl_registers.generator.python.accessor import PythonAccessorGenerator
from hdl_registers.generator.python.pickle import PythonPickleGenerator
from hdl_registers.register_list import RegisterList


def test_generate_with_no_registers(tmp_path):
    register_list = RegisterList(name="test")

    PythonPickleGenerator(register_list=register_list, output_folder=tmp_path).create()
    PythonAccessorGenerator(register_list=register_list, output_folder=tmp_path).create()

    python_module = load_python_module(tmp_path / "test_accessor.py")
    python_module.get_accessor(register_accessor=None)


def test_create_accessor_without_pickle_should_raise_exception(tmp_path):
    register_list = RegisterList(name="test")

    PythonAccessorGenerator(register_list=register_list, output_folder=tmp_path).create()

    python_module = load_python_module(tmp_path / "test_accessor.py")
    with pytest.raises(FileNotFoundError) as exception_info:
        python_module.get_accessor(register_accessor=None)
    assert str(exception_info.value) == (
        f"Could not find the pickle file {tmp_path / 'test.pickle'}, "
        "make sure this artifact is generated."
    )
