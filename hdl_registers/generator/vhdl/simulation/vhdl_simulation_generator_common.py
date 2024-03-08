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
    from hdl_registers.register import Register
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

    def reg_index_constant(
        self, register: "Register", register_array: Optional["RegisterArray"] = None
    ) -> str:
        """
        Get a 'reg_index' constant declaration, for the index of the supplied register.
        If the register is in an array, the constant calculation depends on a 'array_index'
        being present in the VHDL.

        Is suitable for implementation of register/field access procedures.
        """
        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
        reg_index = (
            f"{register_name}(array_index=>array_index)" if register_array else register_name
        )

        return f"    constant reg_index : {self.name}_reg_range := {reg_index};\n"

    @staticmethod
    def reg_address_constant() -> str:
        """
        Get a 'reg_address' constant declaration, for the byte address of the current register.
        Depends on the 'reg_index' and 'base_address' constants being present in the VHDL.

        Is suitable for implementation of register/field access procedures.
        """
        return (
            "    constant reg_address : addr_t := base_address + "
            "to_unsigned(4 * reg_index, addr_width);\n"
        )

    @staticmethod
    def get_register_array_message(
        register_array: Optional["RegisterArray"],
    ) -> str:
        """
        Status message for register array information.
        Suitable for error printouts.

        If the register we are working on is in a register array,  the 'array_index' value must
        be available as an integer in VHDL.
        """
        if register_array:
            register_array_message = (
                f" within the '{register_array.name}["
                '" & to_string(array_index) & "]\' register array'
            )
        else:
            register_array_message = ""

        return f"""\
    constant register_array_message : string := "{register_array_message}";
"""

    @staticmethod
    def get_base_address_message() -> str:
        """
        Status message for base address information.
        Suitable for error printouts.

        Depends on a 'base_address' value being available as an 'unsigned' in VHDL.
        """
        return """\
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
        """
        Get the compounded status message.
        Suitable for error printouts.

        Depends on a 'base_message' string being present in VHDL, as well as a 'message' string
        from user which might be empty.
        """
        return """\
    function get_message return string is
    begin
      if message = "" then
        return base_message;
      end if;

      return base_message & " " & message & ".";
    end function;
"""
