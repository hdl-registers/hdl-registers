# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------


# First party libraries
from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers


def test_to_pascal_case():
    assert RegisterCodeGeneratorHelpers.to_pascal_case("test") == "Test"
    assert RegisterCodeGeneratorHelpers.to_pascal_case("test_two") == "TestTwo"
