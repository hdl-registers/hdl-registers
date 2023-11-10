# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Third party libraries
from tsfpga.system_utils import load_python_module

# First party libraries
from hdl_registers import HDL_REGISTERS_TEST
from hdl_registers.generator.python.python_class_generator import PythonClassGenerator
from hdl_registers.parser import from_toml


def test_recreating_register_list_object(tmp_path):
    register_list = from_toml(module_name="caesar", toml_file=HDL_REGISTERS_TEST / "regs_test.toml")
    PythonClassGenerator(register_list, tmp_path).create()

    test_recreated = load_python_module(tmp_path / "caesar.py").Caesar()
    assert repr(test_recreated) == repr(register_list)

    test_recreated = load_python_module(tmp_path / "caesar.py").get_register_list()
    assert repr(test_recreated) == repr(register_list)
