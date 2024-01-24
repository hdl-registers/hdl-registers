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
from hdl_registers.field.register_field_type import Fixed, Signed, Unsigned
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class BusAccessDirection:
    """
    Keep track of and test the bus access direction.
    """

    def __init__(self, read_or_write: str):
        if read_or_write not in ["read", "write"]:
            raise ValueError(f"Unknown bus access direction name: {read_or_write}")

        self.name = read_or_write

        self.is_read_not_write = read_or_write == "read"
        self.name_past = "read" if self.is_read_not_write else "written"

    @property
    def name_adjective(self) -> str:
        """
        Return "readable" or "writeable".
        """
        return f"{self.name}able"

    def register_is_accessible(self, register: "Register") -> bool:
        """
        Return True if the supplied register is accessible in this direction.
        """
        if self.is_read_not_write:
            return register.is_bus_readable

        return register.is_bus_writeable


class FabricAccessDirection:
    """
    Keep track of and test the fabric access direction.
    """

    def __init__(self, up_or_down: str):
        if up_or_down not in ["up", "down"]:
            raise ValueError(f"Unknown fabric access direction name: {up_or_down}")

        self.name = up_or_down
        self.is_up_not_down = up_or_down == "up"

    def register_is_accessible(self, register: "Register") -> bool:
        """
        Return True if the supplied register is accessible in this direction.
        """
        if self.is_up_not_down:
            # Modes where fabric provides a value to the bus.
            # Analogous the 'reg_file.reg_file_pkg.is_fabric_gives_value_type' VHDL function.
            return register.mode in ["r", "r_wpulse"]

        # Modes where the bus provides a value to the fabric.
        # Analogous the 'reg_file.reg_file_pkg.is_write_type' VHDL function.
        return register.mode in ["w", "r_w", "wpulse", "r_wpulse"]


# The valid bus access directions.
BUS_ACCESS_DIRECTIONS = dict(
    read=BusAccessDirection(read_or_write="read"), write=BusAccessDirection(read_or_write="write")
)

# The valid fabric access directions.
FABRIC_ACCESS_DIRECTIONS = dict(
    up=FabricAccessDirection(up_or_down="up"), down=FabricAccessDirection(up_or_down="down")
)


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
            if isinstance(field.field_type, (Signed, Unsigned)):
                # Plain unsigned/signed vector is a subtype of std_logic_vector.
                # Hence we can just cast it.
                return f"std_logic_vector({value})"

            if isinstance(field.field_type, Fixed):
                # Casting function built into ieee.fixed_pkg.
                return f"to_slv({value})"

            raise ValueError(f"Unknown bit vector field: {field}")

        # Our own conversion function.
        to_slv = self.field_to_slv_function_name(field=field, field_name=field_name)
        return f"{to_slv}({value})"

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

        field_name = self.qualified_field_name(
            register=register, register_array=register_array, field=field
        )
        return f"{field_name}_t"

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

    def has_any_bus_accessible_register(self, direction: BusAccessDirection) -> bool:
        """
        Return True if the register list contains any register, plain or in array, that is
        bus-accessible in the given direction.
        """
        for register, _ in self.iterate_registers():
            if direction.register_is_accessible(register=register):
                return True

        return False

    def iterate_bus_accessible_registers(
        self, direction: BusAccessDirection
    ) -> Iterator[tuple["Register", Optional["RegisterArray"]]]:
        """
        Iterate all registers in the register list, plain or in array, that are bus-accessible in
        the given direction.
        """
        for register, register_array in self.iterate_registers():
            if direction.register_is_accessible(register=register):
                yield register, register_array

    def iterate_bus_accessible_plain_registers(
        self, direction: BusAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all plain registers in the register list that are bus-accessible in the
        given direction.
        """
        for register in self.iterate_plain_registers():
            if direction.register_is_accessible(register=register):
                yield register

    def iterate_bus_accessible_array_registers(
        self, register_array: "RegisterArray", direction: BusAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all registers in the register array that are bus-accessible in the given direction.
        """
        for register in register_array.registers:
            if direction.register_is_accessible(register=register):
                yield register

    def iterate_bus_accessible_register_arrays(
        self, direction: BusAccessDirection
    ) -> Iterator["RegisterArray"]:
        """
        Iterate all register arrays in the register list that contain at least one register that
        is bus-accessible in the given direction.
        """
        for register_array in self.iterate_register_arrays():
            accessible_registers = list(
                self.iterate_bus_accessible_array_registers(
                    register_array=register_array, direction=direction
                )
            )
            if accessible_registers:
                yield register_array

    def has_any_fabric_accessible_register(self, direction: FabricAccessDirection) -> bool:
        """
        Return True if the register list contains at least one register, plain or in array, with a
        mode where fabric accesses the value in the given direction.
        """
        for register, _ in self.iterate_registers():
            if direction.register_is_accessible(register=register):
                return True

        return False

    def iterate_fabric_accessible_registers(
        self, direction: FabricAccessDirection
    ) -> Iterator[tuple["Register", Optional["RegisterArray"]]]:
        """
        Iterate all registers in the register list, plain or in array, that are fabric-accessible in
        the given direction.
        """
        for register, register_array in self.iterate_registers():
            if direction.register_is_accessible(register=register):
                yield register, register_array

    def iterate_fabric_accessible_plain_registers(
        self, direction: FabricAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all plain registers in the register list that are fabric-accessible in the
        given direction.
        """
        for register in self.iterate_plain_registers():
            if direction.register_is_accessible(register=register):
                yield register

    def iterate_fabric_accessible_array_registers(
        self, register_array: "RegisterArray", direction: FabricAccessDirection
    ) -> Iterator["Register"]:
        """
        Iterate all registers in the register array that are fabric-accessible in the
        given direction.
        """
        for register in register_array.registers:
            if direction.register_is_accessible(register=register):
                yield register

    def iterate_fabric_accessible_register_arrays(
        self, direction: FabricAccessDirection
    ) -> Iterator["RegisterArray"]:
        """
        Iterate all register arrays in the register list that contain at least one register that
        is fabric-accessible in the given direction.
        """
        for register_array in self.iterate_register_arrays():
            accessible_registers = list(
                self.iterate_fabric_accessible_array_registers(
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
