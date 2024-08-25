# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator, Optional

# First party libraries
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.field.numerical_interpretation import Fixed, Signed, Unsigned
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.register_mode import HardwareAccessDirection, SoftwareAccessDirection

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class VhdlGeneratorCommon(RegisterCodeGenerator):
    """
    Common methods for generation of VHDL code.
    """

    COMMENT_START = "--"

    @staticmethod
    def field_to_slv_function_name(field: "RegisterField", field_name: str) -> str:
        """
        Name of the function that converts the field's native VHDL representation to SLV.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        if isinstance(field, Integer):
            # All integer field values will be sub-type of VHDL integer.
            # If many of these functions have the same name "to_slv", that will be a name clash.
            # Hence we need to qualify the function name.
            return f"to_{field_name}_slv"

        if isinstance(field, Enumeration):
            # For the enumeration field on the other hand, the type is unambiguous.
            return "to_slv"

        raise TypeError(f"Field {field} does not have a conversion function.")

    def field_to_slv(self, field: "RegisterField", field_name: str, value: str) -> str:
        """
        Get a VHDL snippet that converts a value of the given field to SLV.
        Via e.g. a function call or a cast.

        Arguments:
            field: The field.
            field_name: The field's qualified name.
            value: The name of the variable/constant that holds the field's natively typed value.
        """
        if isinstance(field, Bit):
            return value

        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, (Signed, Unsigned)):
                # Plain unsigned/signed vector is a subtype of std_logic_vector.
                # Hence we can just cast it.
                return f"std_logic_vector({value})"

            if isinstance(field.numerical_interpretation, Fixed):
                # Casting function built into ieee.fixed_pkg.
                return f"to_slv({value})"

            raise ValueError(f"Unknown bit vector field: {field}")

        if isinstance(field, (Enumeration, Integer)):
            # Our own conversion functions.
            to_slv = self.field_to_slv_function_name(field=field, field_name=field_name)
            return f"{to_slv}({value})"

        raise ValueError(f"Unknown field: {field}")

    def field_type_name(
        self,
        register: "Register",
        field: "RegisterField",
        register_array: Optional["RegisterArray"] = None,
    ) -> str:
        """
        Get the native VHDL type name that will represent the value of the supplied field.
        """
        if isinstance(field, Bit):
            return "std_ulogic"

        if isinstance(field, (BitVector, Enumeration, Integer)):
            field_name = self.qualified_field_name(
                register=register, register_array=register_array, field=field
            )
            return f"{field_name}_t"

        raise ValueError(f"Unknown field: {field}")

    def has_any_software_accessible_register(self, direction: SoftwareAccessDirection) -> bool:
        """
        Return True if the register list contains any register, plain or in array, that is
        software-accessible in the given direction.
        """
        for register, _ in self.iterate_registers():
            if register.mode.is_software_accessible(direction=direction):
                return True

        return False

    def iterate_software_accessible_registers(
        self, direction: SoftwareAccessDirection
    ) -> Iterator[tuple["Register", Optional["RegisterArray"]]]:
        """
        Iterate all registers in the register list, plain or in array, that are software-accessible
        in the given direction.
        """
        for register, register_array in self.iterate_registers():
            if register.mode.is_software_accessible(direction=direction):
                yield register, register_array

    def iterate_software_accessible_plain_registers(
        self, direction: SoftwareAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all plain registers in the register list that are software-accessible in the
        given direction.
        """
        for register in self.iterate_plain_registers():
            if register.mode.is_software_accessible(direction=direction):
                yield register

    def iterate_software_accessible_array_registers(
        self, register_array: "RegisterArray", direction: SoftwareAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all registers in the register array that are software-accessible in the
        given direction.
        """
        for register in register_array.registers:
            if register.mode.is_software_accessible(direction=direction):
                yield register

    def iterate_software_accessible_register_arrays(
        self, direction: SoftwareAccessDirection
    ) -> Iterator["RegisterArray"]:
        """
        Iterate all register arrays in the register list that contain at least one register that
        is software-accessible in the given direction.
        """
        for register_array in self.iterate_register_arrays():
            accessible_registers = list(
                self.iterate_software_accessible_array_registers(
                    register_array=register_array, direction=direction
                )
            )
            if accessible_registers:
                yield register_array

    def has_any_hardware_accessible_register(self, direction: HardwareAccessDirection) -> bool:
        """
        Return True if the register list contains at least one register, plain or in array, with a
        mode where hardware accesses the value in the given direction.
        """
        for register, _ in self.iterate_registers():
            if register.mode.is_hardware_accessible(direction=direction):
                return True

        return False

    def iterate_hardware_accessible_registers(
        self, direction: HardwareAccessDirection
    ) -> Iterator[tuple["Register", Optional["RegisterArray"]]]:
        """
        Iterate all registers in the register list, plain or in array, that are hardware-accessible
        in the given direction.
        """
        for register, register_array in self.iterate_registers():
            if register.mode.is_hardware_accessible(direction=direction):
                yield register, register_array

    def iterate_hardware_accessible_plain_registers(
        self, direction: HardwareAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all plain registers in the register list that are hardware-accessible in the
        given direction.
        """
        for register in self.iterate_plain_registers():
            if register.mode.is_hardware_accessible(direction=direction):
                yield register

    def iterate_hardware_accessible_array_registers(
        self, register_array: "RegisterArray", direction: HardwareAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all registers in the register array that are hardware-accessible in the
        given direction.
        """
        for register in register_array.registers:
            if register.mode.is_hardware_accessible(direction=direction):
                yield register

    def iterate_hardware_accessible_register_arrays(
        self, direction: HardwareAccessDirection
    ) -> Iterator["RegisterArray"]:
        """
        Iterate all register arrays in the register list that contain at least one register that
        is hardware-accessible in the given direction.
        """
        for register_array in self.iterate_register_arrays():
            accessible_registers = list(
                self.iterate_hardware_accessible_array_registers(
                    register_array=register_array, direction=direction
                )
            )
            if accessible_registers:
                yield register_array

    def _create_if_there_are_registers_otherwise_delete_file(self, **kwargs: Any) -> Path:
        """
        Create the code artifact only if the register list actually has any registers.
        Convenient to call in generators where no registers would result in the generated file being
        an empty shell.

        If, for example, the user has a register list with only constants we do not want
        to flood the file system with unnecessary files.

        If the artifact file exists from a previous run, we delete it since we do not want stray
        files laying around and we do not want to give the false impression that this file is being
        actively generated.
        """
        if self.register_list.register_objects:
            return super().create(**kwargs)

        if self.output_file.exists():
            # Will not work if it is a directory, but if it is then that is a major user error
            # and we kinda want to back out.
            self.output_file.unlink()

        # Return the path to the output file, which at this point does not exist.
        # But do it anyway just to be consistent with the other generators.
        return self.output_file
