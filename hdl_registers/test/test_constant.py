# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from tsfpga.registers.constant import Constant


def test_repr():
    # Check that repr is an actual representation, not just "X object at 0xABCDEF"
    assert "apa" in repr(Constant(name="apa", value=0))

    # Different name
    assert repr(Constant(name="apa", value=0)) != repr(Constant(name="hest", value=0))

    # Different value
    assert repr(Constant(name="apa", value=0)) != repr(Constant(name="apa", value=1))

    # Different description
    assert repr(Constant(name="apa", value=0, description="Blah")) != repr(
        Constant(name="apa", value=0, description="Gaah")
    )
