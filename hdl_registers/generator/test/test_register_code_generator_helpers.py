# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------


# First party libraries
from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers


def test_to_pascal_case():
    assert RegisterCodeGeneratorHelpers.to_pascal_case("test") == "Test"
    assert RegisterCodeGeneratorHelpers.to_pascal_case("test_two") == "TestTwo"
