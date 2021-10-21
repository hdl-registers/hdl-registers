# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project.
# https://tsfpga.com
# https://gitlab.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

import tsfpga
from tsfpga.system_utils import load_python_module
from tsfpga.registers.parser import from_toml


def test_recreating_register_list_object(tmp_path):
    toml_file = tsfpga.TSFPGA_EXAMPLE_MODULES / "artyz7" / "regs_artyz7.toml"
    artyz7_regs = from_toml("artyz7", toml_file)

    artyz7_regs.create_python_class(tmp_path)
    artyz7_recreated = load_python_module(tmp_path / "artyz7.py").Artyz7()

    assert repr(artyz7_recreated) == repr(artyz7_regs)
