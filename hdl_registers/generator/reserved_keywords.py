# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.generator.c.reserved_keywords import RESERVED_KEYWORDS as C_RESERVED_KEYWORDS
from hdl_registers.generator.cpp.reserved_keywords import RESERVED_KEYWORDS as CPP_RESERVED_KEYWORDS
from hdl_registers.generator.html.reserved_keywords import (
    RESERVED_KEYWORDS as HTML_RESERVED_KEYWORDS,
)
from hdl_registers.generator.python.reserved_keywords import (
    RESERVED_KEYWORDS as PYTHON_RESERVED_KEYWORDS,
)
from hdl_registers.generator.vhdl.reserved_keywords import (
    RESERVED_KEYWORDS as VHDL_RESERVED_KEYWORDS,
)

# All reserved keywords from all target languages.
RESERVED_KEYWORDS = (
    C_RESERVED_KEYWORDS
    | CPP_RESERVED_KEYWORDS
    | HTML_RESERVED_KEYWORDS
    | PYTHON_RESERVED_KEYWORDS
    | VHDL_RESERVED_KEYWORDS
)
