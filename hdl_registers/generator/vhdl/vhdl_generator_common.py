# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from typing import TYPE_CHECKING, Iterator, Optional, Union

# First party libraries
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.generator.register_code_generator_helpers import RegisterCodeGeneratorHelpers

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
    Keep track of and test the bus access direction.
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


class VhdlGeneratorCommon(RegisterCodeGenerator, RegisterCodeGeneratorHelpers):
    """
    Common methods for generation of VHDL code.
    """

    COMMENT_START = "--"

    def register_name(
        self, register: "Register", register_array: Optional["RegisterArray"] = None
    ) -> str:
        """
        Get the qualified register name, e.g. "<module name>_<register name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        if register_array is None:
            return f"{self.name}_{register.name}"

        return f"{self.name}_{register_array.name}_{register.name}"

    def register_array_name(self, register_array: "RegisterArray") -> str:
        """
        Get the qualified register array name.
        To be used where the scope requires it, i.e. outside of records.
        """
        return f"{self.name}_{register_array.name}"

    def field_name(
        self,
        register: "Register",
        field: "RegisterField",
        register_array: Optional["RegisterArray"] = None,
    ) -> str:
        """
        Get the qualified field name, e.g. "<module name>_<register name>_<field_name>".
        To be used where the scope requires it, i.e. outside of records.
        """
        register_name = self.register_name(register=register, register_array=register_array)
        return f"{register_name}_{field.name}"

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
            field: A field.
            field_name: The field's qualified name.
            value: The name of the variable/constant that holds the field's natively typed value.
        """
        if isinstance(field, Bit):
            return value

        if isinstance(field, BitVector):
            return f"std_logic_vector({value})"

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

        field_name = self.field_name(register=register, register_array=register_array, field=field)
        return f"{field_name}_t"

    def has_any_bus_accessible_register(self, direction: BusAccessDirection) -> bool:
        """
        Return True if the register list contains any register, plain or in array, that is
        bus-accessible in the given direction.
        """
        for register, _ in self.iterate_registers():
            if direction.register_is_accessible(register=register):
                return True

        return False

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
    ) -> Iterator[tuple["Register", Union[None, "RegisterArray"]]]:
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
