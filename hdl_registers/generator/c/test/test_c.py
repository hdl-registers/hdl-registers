# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from tsfpga.system_utils import read_file

from hdl_registers import HDL_REGISTERS_TESTS
from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.parser.toml import from_toml


def test_wmasked_register_has_mask_field(tmp_path):
    register_list = from_toml(name="caesar", toml_file=HDL_REGISTERS_TESTS / "regs_test.toml")
    c_code = read_file(
        CHeaderGenerator(register_list=register_list, output_folder=tmp_path).create()
    )
    assert "#define CAESAR_INSTRUCTION_MASK_SHIFT (16u)" in c_code
