# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator


class RegisterVhdlGeneratorCommon(RegisterCodeGenerator):
    """
    Common methods for generation of VHDL code.
    """

    def __init__(self, module_name: str, generated_info: list[str]):
        """
        Arguments:
            module_name: The name of the register map.
            generated_info: Will be placed in the file headers.
        """
        self.module_name = module_name
        self.generated_info = generated_info

    @staticmethod
    def _comment(comment, indent=0) -> str:
        """
        Get a single-line comment with the correct leading comment character.
        """
        indentation = " " * indent
        return f"{indentation}-- {comment}\n"

    def _header(self) -> str:
        """
        Get file header formatted as a comment block.
        """
        return self._comment_block(text="\n".join(self.generated_info), indent=0)

    def _register_name(self, register, register_array=None) -> str:
        """
        Get the qualified register name, e.g. "<module name>_<register name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        if register_array is None:
            return f"{self.module_name}_{register.name}"
        return f"{self.module_name}_{register_array.name}_{register.name}"

    def _register_array_name(self, register_array) -> str:
        """
        Get the qualified register array name.
        To be used where the scope requires it, i.e. outside of records.
        """
        return f"{self.module_name}_{register_array.name}"

    def _field_name(self, register, register_array, field) -> str:
        """
        Get the qualified field name, e.g. "<module name>_<register name>_<field_name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        register_name = self._register_name(register=register, register_array=register_array)
        return f"{register_name}_{field.name}"

    @staticmethod
    def _register_comment(register, register_array=None) -> str:
        """
        Get a comment describing the register.
        """
        result = f"'{register.name}' register"

        if register_array is None:
            return result

        return f"{result} within the '{register_array.name}' register array"

    @staticmethod
    def _register_mode_has_up(mode: str) -> bool:
        """
        Return True if the provided register mode is one where fabric provides a value
        to the bus.

        Analogous the ``reg_file.reg_file_pkg.is_fabric_gives_value_type`` VHDL function.
        """
        return mode in ["r", "r_wpulse"]

    def _has_any_up_registers(self, register_objects) -> bool:
        """
        Return True if the register list contains any register of a mode where fabric provides
        a value to the bus.
        """
        for register, _ in self._iterate_registers(register_objects=register_objects):
            if self._register_mode_has_up(mode=register.mode):
                return True

        return False

    def _has_any_bus_readable_registers(self, register_objects) -> bool:
        """
        Return True if the register list contains any register that is bus-readable.
        """
        for register, _ in self._iterate_registers(register_objects=register_objects):
            if register.is_bus_readable:
                return True

        return False

    @staticmethod
    def _register_mode_has_down(mode: str) -> bool:
        """
        Return True if the provided register mode is one where the bus provides a value to
        the fabric.

        Note that this is NOT an inversion of :meth:`._register_mode_has_up`.
        """
        return mode in ["w", "r_w", "wpulse", "r_wpulse"]

    def _has_any_down_registers(self, register_objects) -> bool:
        """
        Return True if the register list contains any register of a mode where bus provides
        a value to the fabric.
        """
        for register, _ in self._iterate_registers(register_objects=register_objects):
            if self._register_mode_has_down(mode=register.mode):
                return True

        return False

    def _has_any_bus_writable_registers(self, register_objects) -> bool:
        """
        Return True if the register list contains any registers that is bus-writable.

        Note that this is NOT the same thing as having a register of a 'down' mode.
        """
        for register, _ in self._iterate_registers(register_objects=register_objects):
            if register.is_bus_writeable:
                return True

        return False
