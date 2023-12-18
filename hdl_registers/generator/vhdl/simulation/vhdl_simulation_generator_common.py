# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import TYPE_CHECKING, Optional

# First party libraries
from hdl_registers.generator.vhdl.vhdl_generator_common import VhdlGeneratorCommon

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.register_array import RegisterArray


class VhdlSimulationGeneratorCommon(VhdlGeneratorCommon):
    """
    Common methods for generation of VHDL simulation code.
    """

    def get_array_index_port(self, register_array: Optional["RegisterArray"]) -> str:
        """
        Get the array index port declaration.
        Suitable for VHDL procedure/function signatures that can read registers in arrays.
        """
        if register_array:
            array_name = self.qualified_register_array_name(register_array=register_array)
            return f"    array_index : in {array_name}_range;\n"

        return ""

    @staticmethod
    def get_array_index_association(register_array: Optional["RegisterArray"]) -> str:
        """
        Get the array index association.
        Suitable when associating the array index port to a read/write procedure call.
        """
        if register_array:
            return "      array_index => array_index,\n"

        return ""

    @staticmethod
    def get_register_array_and_base_address_message(
        register_array: Optional["RegisterArray"],
    ) -> str:
        if register_array:
            register_array_message = (
                f" within the '{register_array.name}["
                '" & to_string(array_index) & "]\' register array'
            )
        else:
            register_array_message = ""

        return f"""\
    constant register_array_message : string := "{register_array_message}";
    function base_address_message return string is
    begin
      if base_address /= 0 then
        return " (at base address " & hex_image(std_logic_vector(base_address)) & ")";
      end if;

      return "";
    end function;
"""

    @staticmethod
    def get_message() -> str:
        return """\
    function get_message return string is
    begin
      if message = "" then
        return base_message;
      end if;

      return base_message & " " & message & ".";
    end function;
"""
