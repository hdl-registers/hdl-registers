# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Reserved keywords in the Python programming language.
# Should include everything up until Python 3.12.
# From https://docs.python.org/3/reference/lexical_analysis.html#keywords
# Note that they shall all be lowercase here in this set.
RESERVED_PYTHON_KEYWORDS = {
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "false",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "none",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "true",
    "try",
    "while",
    "with",
    "yield",
}
