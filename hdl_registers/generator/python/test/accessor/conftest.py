# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import Union

# Third party libraries
import pytest
from tsfpga.system_utils import load_python_module

# First party libraries
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.generator.python.accessor import PythonAccessorGenerator
from hdl_registers.generator.python.pickle import PythonPickleGenerator
from hdl_registers.register_array import RegisterArray
from hdl_registers.register_list import RegisterList
from hdl_registers.register_mode import RegisterMode
from hdl_registers.register_modes import REGISTER_MODES

# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def tmp_session_path(tmp_path_factory: pytest.TempdirFactory) -> Path:
    """
    tmp_path that is common for all test runs in this session.
    Unlike the default tmp_path fixture, which is function scoped.
    https://stackoverflow.com/questions/70779045
    https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmp-path-factory-fixture
    """
    return tmp_path_factory.mktemp("temp")


@pytest.fixture(scope="session")
def generate_default_accessor(tmp_session_path):
    """
    Since all the tests use the same register list, we can save a lot of time by generating the
    Python code artifact only once.
    We run a huge amount of tests for the accessor, and the file generation takes 0.5-1 second,
    so the gain is significant.
    """
    register_list = RegisterList(name="test")

    add_test_registers(register_list_or_array=register_list)
    add_empty_registers(register_list_or_array=register_list)
    add_single_field_registers(register_list_or_array=register_list)

    register_array = register_list.append_register_array(
        name="reg_array_a", length=3, description=""
    )
    add_test_registers(register_list_or_array=register_array)
    add_empty_registers(register_list_or_array=register_array)
    add_single_field_registers(register_list_or_array=register_array)

    PythonPickleGenerator(register_list=register_list, output_folder=tmp_session_path).create()
    PythonAccessorGenerator(register_list=register_list, output_folder=tmp_session_path).create()

    python_module = load_python_module(tmp_session_path / "test_accessor.py")

    return tmp_session_path, python_module


def add_test_registers(register_list_or_array: Union[RegisterList, RegisterArray]) -> None:
    for mode in REGISTER_MODES.values():
        setup_test_register(register_list_or_array=register_list_or_array, mode=mode)


def setup_test_register(
    register_list_or_array: Union[RegisterList, RegisterArray], mode: RegisterMode
) -> None:
    register = register_list_or_array.append_register(
        f"reg_{mode.shorthand}", mode=mode, description=""
    )

    register.append_bit(name="bit_aa0", description="", default_value="0")
    register.append_bit(name="bit_aa1", description="", default_value="1")

    register.append_bit_vector(
        name="unsigned_aa",
        description="",
        width=4,
        default_value="0101",
        numerical_interpretation=Unsigned(bit_width=4),
    )
    register.append_bit_vector(
        name="signed_aa",
        description="",
        width=4,
        default_value="1010",
        numerical_interpretation=Signed(bit_width=4),
    )
    register.append_bit_vector(
        name="ufixed_aa",
        description="",
        width=4,
        default_value="0110",
        numerical_interpretation=UnsignedFixedPoint(1, -2),
    )
    register.append_bit_vector(
        name="sfixed_aa",
        description="",
        width=4,
        default_value="1001",
        numerical_interpretation=SignedFixedPoint(0, -3),
    )

    register.append_enumeration(
        name="enumeration_aa",
        description="",
        elements=dict(element_aa0="", element_aa1="", element_aa2=""),
        default_value="element_aa1",
    )

    register.append_integer(
        name="uint_aa", description="", min_value=0, max_value=10, default_value=5
    )
    register.append_integer(
        name="sint_aa", description="", min_value=-10, max_value=10, default_value=2
    )


def add_empty_registers(register_list_or_array: Union[RegisterList, RegisterArray]) -> None:
    for mode in REGISTER_MODES.values():
        register_list_or_array.append_register(
            name=f"empty_{mode.shorthand}", mode=mode, description=""
        )


def add_single_field_registers(register_list_or_array: Union[RegisterList, RegisterArray]) -> None:
    register = register_list_or_array.append_register(
        "single_w_bit", mode=REGISTER_MODES["w"], description=""
    )
    register.append_bit(name="bit_bb", description="", default_value="1")

    register = register_list_or_array.append_register(
        "single_w_unsigned", mode=REGISTER_MODES["w"], description=""
    )
    register.append_bit_vector(
        name="unsigned_bb",
        description="",
        width=4,
        default_value="1011",
        numerical_interpretation=Unsigned(bit_width=4),
    )

    register = register_list_or_array.append_register(
        "single_r_w_sfixed", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(
        name="sfixed_bb",
        description="",
        width=4,
        default_value="1100",
        numerical_interpretation=SignedFixedPoint(1, -2),
    )

    register = register_list_or_array.append_register(
        "single_wpulse_enumeration", mode=REGISTER_MODES["wpulse"], description=""
    )
    register.append_enumeration(
        name="enumeration_bb",
        description="",
        elements=dict(element_bb0="", element_bb1="", element_bb2=""),
        default_value="element_bb2",
    )

    register = register_list_or_array.append_register(
        "single_r_wpulse_uint", mode=REGISTER_MODES["r_wpulse"], description=""
    )
    register.append_integer(
        name="uint_bb", description="", min_value=10, max_value=15, default_value=15
    )
