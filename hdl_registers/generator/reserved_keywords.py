# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.generator.c.reserved_keywords import RESERVED_C_KEYWORDS
from hdl_registers.generator.cpp.reserved_keywords import RESERVED_CPP_KEYWORDS
from hdl_registers.generator.html.reserved_keywords import RESERVED_HTML_KEYWORDS
from hdl_registers.generator.python.reserved_keywords import RESERVED_PYTHON_KEYWORDS
from hdl_registers.generator.vhdl.reserved_keywords import RESERVED_VHDL_KEYWORDS

# All reserved keywords from all target languages.
RESERVED_KEYWORDS = (
    RESERVED_C_KEYWORDS
    | RESERVED_CPP_KEYWORDS
    | RESERVED_HTML_KEYWORDS
    | RESERVED_PYTHON_KEYWORDS
    | RESERVED_VHDL_KEYWORDS
)
