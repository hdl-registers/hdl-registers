# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING

from hdl_registers.field.bit_vector import BitVector
from hdl_registers.register_modes import REGISTER_MODES

from .register_code_generator import RegisterCodeGenerator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register


class SoftwareCodeGenerator(RegisterCodeGenerator):
    """
    Base class for all generators that generate code for a software languages (C/C++/Python).
    Also for documentation generators that create documentation for the software interface.
    This class contains helper methods that are common for these.
    """

    def get_implied_fields(self, register: Register) -> Iterable[RegisterField]:
        """
        All 'masked'-mode registers shall have a ``mask`` field at the correct location and with
        the correct width.
        When generating code for the fields in a register, add this method call result to the
        list of fields.

        This method should typically be called from software-language generators, where the user
        should set the value of each field as well as the mask when writing.
        This method should typically NOT be called from hardware-language generators.
        The ``mask`` is not handled as just another field there, it is done with a special handling.
        """
        if register.mode != REGISTER_MODES["wmasked"]:
            return []

        mask_base_index = register.fields_width
        utilized_width = self.register_utilized_width(register=register)

        return [
            BitVector(
                name="mask",
                base_index=mask_base_index,
                description="""\
Write-enable mask for the payload of this masked register.
Each bit in this field corresponds to a bit in the payload field(s).
When this register is written, only the payload bits that have their corresponding mask bit asserted
will have their write-value set in hardware.
""",
                width=utilized_width,
                default_value=0,
            )
        ]

    def should_have_field_accessors(self, register: Register) -> bool:
        """
        All 'masked'-mode registers shall have a ``mask`` field at the correct location and with
        the correct width.
        When generating code for the fields in a register, add this method call result to the
        list of fields.

        This method should typically be called from software-language generators, where the user
        should set the value of each field as well as the mask when writing.
        This method should typically NOT be called from hardware-language generators.
        The ``mask`` is not handled as just another field there, it is done with a special handling.
        """
        return register.mode != REGISTER_MODES["wmasked"]
