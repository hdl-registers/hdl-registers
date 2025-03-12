# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------
# Works with any VHDL simulator supported by VUnit. Tested with GHDL and ModelSim.
# --------------------------------------------------------------------------------------------------

import sys
from os import environ
from pathlib import Path
from xml.etree import ElementTree  # noqa: ICN001

import pytest

THIS_DIR = Path(__file__).parent.resolve()
REPO_ROOT = THIS_DIR.parent.parent.parent.parent.resolve()
sys.path.append(str(REPO_ROOT))

# Add path for default location of tsfpga to PYTHONPATH.
sys.path.append(str((REPO_ROOT.parent.parent / "tsfpga" / "tsfpga").resolve()))

# ruff: noqa: E402

from tsfpga.examples.example_env import get_hdl_modules
from tsfpga.system_utils import create_directory
from vunit import VUnit

from hdl_registers import HDL_REGISTERS_DOC, HDL_REGISTERS_GENERATED, HDL_REGISTERS_TESTS
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.generator.vhdl.test.test_register_vhdl_generator import (
    generate_all_vhdl_artifacts,
    generate_strange_register_maps,
)
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_modes import REGISTER_MODES

COUNTER_EXAMPLE_FOLDER = HDL_REGISTERS_DOC / "sphinx" / "rst" / "generator" / "example_counter"


def test_running_simulation(tmp_path):
    """
    Run the testbench .vhd files that are next to this file.
    Contains assertions on types and type conversions.
    Shows that the files can be compiled and that the information is correct.
    """
    vunit_out_path = tmp_path
    generated_register_path = vunit_out_path / "generated_register"

    # Remove any previously-generated register files before the test.
    for vhd_file in generated_register_path.glob("*.vhd"):
        vhd_file.unlink()

    generate_toml_registers(output_path=generated_register_path)
    generate_strange_register_maps(output_path=generated_register_path)
    generate_doc_registers(output_path=generated_register_path)

    def run(args: list[str], exit_code: int, xml_report_path: Path) -> None:
        argv = [
            "--minimal",
            "--num-threads",
            "10",
            "--output-path",
            str(vunit_out_path),
            "--xunit-xml",
            str(xml_report_path),
            *args,
        ]
        vunit_proj = VUnit.from_argv(argv=argv)
        vunit_proj.add_verification_components()
        vunit_proj.add_vhdl_builtins()

        library = vunit_proj.add_library(library_name="example")

        for vhd_file in THIS_DIR.glob("*.vhd"):
            library.add_source_file(vhd_file)

        for vhd_file in COUNTER_EXAMPLE_FOLDER.glob("*.vhd"):
            library.add_source_file(vhd_file)

        for vhd_file in generated_register_path.glob("*.vhd"):
            library.add_source_file(vhd_file)

        for module in get_hdl_modules(names_avoid={"hard_fifo"}):
            vunit_library = vunit_proj.add_library(library_name=module.library_name)
            for hdl_file in module.get_simulation_files(include_tests=False):
                vunit_library.add_source_file(hdl_file.path)

        with pytest.raises(SystemExit) as exception_info:
            vunit_proj.main()
        assert exception_info.value.code == exit_code

    # All these tests should pass.
    run(
        args=["--without-attribute", ".expected_failure"],
        exit_code=0,
        xml_report_path=vunit_out_path / "passing.xml",
    )

    # All these should fail.
    run(
        args=["--with-attribute", ".expected_failure"],
        exit_code=1,
        xml_report_path=vunit_out_path / "failing.xml",
    )

    tb_check = "example.tb_check_pkg."
    tb_integration = "example.tb_integration."
    tb_register_package = "example.tb_register_package."
    tb_wait_until = "example.tb_wait_until_equals."

    out_of_range = (
        "is out of range"
        if environ.get("VUNIT_SIMULATOR") == "modelsim"
        else "ghdl:error: bound check failure"
    )

    check_failed_tests(
        xml_report_file=vunit_out_path / "failing.xml",
        test_outputs={
            f"{tb_check}test_check_register_equal_fail_0": (
                "ERROR - Checking the 'first' register within the 'dummies[1]' register array. "
                "- Got -----------------101100010000000. Expected -----------------011001100100001."
            ),
            f"{tb_check}test_check_register_equal_fail_1": (
                "Checking the 'current_timestamp' register (at base address x\"00050000\"). "
                "Alarming error!. - Got 0000_0000_0000_0000_0000_0000_0000_0000 (0). "
                "Expected 0000_0000_0000_0000_0000_0000_0000_1110 (14)."
            ),
            f"{tb_check}test_check_register_equal_fail_2": (
                "ERROR - Checking the 'current_timestamp' register. - Got 0. Expected 44."
            ),
            f"{tb_check}test_check_equal_fail_for_array_register_field_at_a_base_address": (
                "ERROR - Checking the 'array_bit_vector' field in the 'first' register within "
                "the 'dummies[1]' register array (at base address x\"00050000\"). "
                "Custom message here. - Got 0_1100 (12). Expected 1_1001 (25)"
            ),
            f"{tb_check}test_check_equal_fail_for_array_register_field": (
                "ERROR - Checking the 'array_bit_a' field in the 'first' register within "
                "the 'dummies[1]' register array. - Got 1. Expected 0."
            ),
            f"{tb_check}test_check_equal_fail_for_bit_field": (
                "ERROR - Checking the 'plain_bit_a' field in the 'conf' "
                "register. - Got 0. Expected 1."
            ),
            f"{tb_check}test_check_equal_fail_for_bit_vector_field_at_a_base_address": (
                "ERROR - Checking the 'plain_bit_vector' field in the 'conf' "
                'register (at base address x"00050000"). - Got 0011 (3). Expected 1100 (12).'
            ),
            f"{tb_check}test_check_equal_fail_for_enumeration_field": (
                "ERROR - Checking the 'plain_enumeration' field in the 'conf' "
                "register. - Got plain_enumeration_third. Expected plain_enumeration_fifth."
            ),
            f"{tb_check}test_check_equal_fail_for_integer_field": (
                "ERROR - Checking the 'plain_integer' field in the 'conf' "
                "register. - Got 66. Expected -33."
            ),
            f"{tb_check}test_check_equal_fail_for_sfixed_field": (
                "ERROR - Checking the 'sfixed0' field in the 'field_test' "
                "register. - Got 111.111 (-0.125000). Expected 101.010 (-2.750000)."
            ),
            f"{tb_check}test_check_equal_fail_for_ufixed_field": (
                "ERROR - Checking the 'ufixed0' field in the 'field_test' "
                "register. Custom message here. - Got 111111.11 (63.750000). "
                "Expected 101010.10 (42.500000)."
            ),
            # ------------------------------------------------------------
            f"{tb_integration}test_reading_write_only_register_should_fail": (
                "FAILURE - rresp - Got AXI response SLVERR(10) expected OKAY(00)"
            ),
            f"{tb_integration}test_writing_read_only_register_should_fail": (
                "FAILURE - bresp - Got AXI response SLVERR(10) expected OKAY(00)"
            ),
            # ------------------------------------------------------------
            f"{tb_register_package}test_enumeration_out_of_range": out_of_range,
            f"{tb_register_package}test_integer_from_slv_out_of_range": out_of_range,
            f"{tb_register_package}test_integer_to_slv_out_of_range": out_of_range,
            # ------------------------------------------------------------
            f"{tb_wait_until}test_wait_until_array_field_equals_timeout_with_base_address": (
                "FAILURE - Timeout while waiting for the 'array_integer' field in the 'first' "
                "register within the 'dummies[1]' register array (at base address x\"00050000\") "
                "to equal the given value: -------------------------0100001. Extra printout "
                "that can be set!."
            ),
            f"{tb_wait_until}test_wait_until_array_field_equals_timeout": (
                "FAILURE - Timeout while waiting for the 'array_integer' field in the 'first' "
                "register within the 'dummies[1]' register array to equal the given "
                "value: -------------------------0100001. Extra printout that can be set!."
            ),
            f"{tb_wait_until}test_wait_until_array_register_equals_timeout": (
                "FAILURE - Timeout while waiting for the 'first' register within the 'dummies[1]' "
                "register array to equal the given "
                "value: -----------------011001100100001. Extra printout that can be set!."
            ),
            f"{tb_wait_until}test_wait_until_plain_field_equals_timeout_with_message": (
                "FAILURE - Timeout while waiting for the 'plain_integer' field in the "
                "'conf' register to equal the given "
                "value: -------------------11011111-----. Extra printout that can be set!."
            ),
            f"{tb_wait_until}test_wait_until_plain_field_equals_timeout": (
                "FAILURE - Timeout while waiting for the 'plain_integer' field in the "
                "'conf' register to equal the given value: -------------------11011111-----."
            ),
            f"{tb_wait_until}test_wait_until_plain_register_equals_timeout": (
                "FAILURE - Timeout while waiting for the 'conf' register to equal the given "
                "value: ---------------01001101111111001."
            ),
        },
    )


def generate_toml_registers(output_path):
    register_list = from_toml(
        name="caesar",
        toml_file=HDL_REGISTERS_TESTS / "regs_test.toml",
    )

    # Add some bit vector fields with types.
    # This is not supported by the TOML parser at this point, so we do it manually.
    register = register_list.append_register(
        name="field_test", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(
        name="u0",
        description="",
        width=2,
        default_value="11",
        numerical_interpretation=Unsigned(bit_width=2),
    )

    register.append_bit_vector(
        name="s0",
        description="",
        width=2,
        default_value="11",
        numerical_interpretation=Signed(bit_width=2),
    )
    register.append_bit_vector(
        name="ufixed0",
        description="",
        width=8,
        default_value="1" * 8,
        numerical_interpretation=UnsignedFixedPoint(5, -2),
    )
    register.append_bit_vector(
        name="sfixed0",
        description="",
        width=6,
        default_value="1" * 6,
        numerical_interpretation=SignedFixedPoint(2, -3),
    )

    generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)


def generate_doc_registers(output_path):
    register_list = from_toml(
        name="counter", toml_file=COUNTER_EXAMPLE_FOLDER / "regs_counter.toml"
    )

    generate_all_vhdl_artifacts(register_list=register_list, output_folder=output_path)


def check_failed_tests(xml_report_file: Path, test_outputs: dict[str, str]) -> None:
    """
    Check an XML report from VUnit that it
    * contains only the expected tests,
    * all tests failed, and
    * the test output is the expected.
    """
    tree = ElementTree.parse(xml_report_file)  # noqa: S314
    root = tree.getroot()

    num_tests = int(root.attrib["tests"])
    assert num_tests == len(test_outputs)

    xml_test_outputs = {}
    for test in root.iter("testcase"):
        test_name = f"{test.attrib['classname']}.{test.attrib['name']}"

        assert test.find("failure") is not None, f"Test {test_name} did not fail."

        xml_test_outputs[test_name] = test.find("system-out").text

    got_names = set(xml_test_outputs.keys())
    expected_names = set(test_outputs.keys())
    assert got_names == expected_names, f"Test case name difference: {got_names ^ expected_names}"

    for test_name, expected_output in test_outputs.items():
        got_output = xml_test_outputs[test_name]
        if expected_output not in got_output:
            raise AssertionError(
                f"\nTest {test_name}. Got:\n{got_output}\nExpected:\n{expected_output}"
            )


if __name__ == "__main__":
    # This file is primarily meant to be run with the 'pytest' runner, but it can also be run
    # manually as a script.
    test_running_simulation(
        tmp_path=create_directory(HDL_REGISTERS_GENERATED / "vunit_out", empty=False)
    )
