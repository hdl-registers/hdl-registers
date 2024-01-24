# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Reserved keywords in the HTML programming language.
# HTML does not really have reserved keywords in the same way as the other generator languages.
# https://wansazlinasaruddin.com/html-reserved-words-html-elements
# But we keep this file and dictionary anyway, to be consistent with the other generator languages.
# Perhaps in the future add JavaScript reserved keywords here, if we do more fancy thing in the
# generated HTML?
RESERVED_HTML_KEYWORDS: set[str] = set()
