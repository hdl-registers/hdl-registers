# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.register_modes import REGISTER_MODES


def test_dictionary_key_is_equal_to_shorthand():
    for key, mode in REGISTER_MODES.items():
        assert key == mode.shorthand
