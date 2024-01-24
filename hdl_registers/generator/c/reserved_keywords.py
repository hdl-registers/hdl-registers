# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Reserved keywords in the C programming language.
# Should include everything up until C23.
# From https://en.cppreference.com/w/c/keyword
# Note that they shall all be lowercase here in this set.
RESERVED_C_KEYWORDS = {
    "alignas",
    "alignof",
    "auto",
    "bool",
    "break",
    "case",
    "char",
    "const",
    "constexpr",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "false",
    "float",
    "for",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "nullptr",
    "register",
    "restrict",
    "return",
    "short",
    "signed",
    "sizeof",
    "static_assert",
    "static",
    "struct",
    "switch",
    "thread_local",
    "true",
    "typedef",
    "typeof_unqual",
    "typeof",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while",
}
