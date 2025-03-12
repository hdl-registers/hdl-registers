# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from hdl_registers.generator.c.reserved_keywords import RESERVED_C_KEYWORDS
from hdl_registers.generator.cpp.reserved_keywords import RESERVED_CPP_KEYWORDS
from hdl_registers.generator.html.reserved_keywords import RESERVED_HTML_KEYWORDS
from hdl_registers.generator.python.reserved_keywords import RESERVED_PYTHON_KEYWORDS

# All reserved keywords that shall yield an error if used for register data.
# Note that only the keywords from software generator languages are included here.
# E.g. VHDL and Verilog are not included.
# This is because an erroneous use of a reserved keyword in HDL code will be detected early
# when e.g. simulating or building.
# The reserved keyword mechanism is in place for detecting keyword usage that would give an error
# in the generated software code after e.g. a 1-hour FPGA build.
# That's where the mechanism makes sense and adds value.
# In general we want to keep the reserved keywords set as small as possible.
# The more language support the more reserved keywords we have to add, which is actually a problem.
RESERVED_KEYWORDS = (
    RESERVED_C_KEYWORDS | RESERVED_CPP_KEYWORDS | RESERVED_HTML_KEYWORDS | RESERVED_PYTHON_KEYWORDS
)
