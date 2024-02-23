# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.generator.reserved_keywords import RESERVED_KEYWORDS


def test_is_all_lowercase():
    # The check for reserved keywords is done with a lowercase argument, hence everything in the set
    # of reserved keywords must also be lowercase for this mechanism to work.
    for keyword in RESERVED_KEYWORDS:
        assert keyword.islower(), keyword
