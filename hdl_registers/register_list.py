# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import copy
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

# Local folder libraries
from .constant.bit_vector_constant import UnsignedVector, UnsignedVectorConstant
from .constant.boolean_constant import BooleanConstant
from .constant.float_constant import FloatConstant
from .constant.integer_constant import IntegerConstant
from .constant.string_constant import StringConstant
from .register import Register
from .register_array import RegisterArray
from .register_mode import RegisterMode

if TYPE_CHECKING:
    # Local folder libraries
    from .constant.constant import Constant


class RegisterList:
    """
    Used to handle the registers of a module. Also known as a register map.
    """

    def __init__(self, name: str, source_definition_file: Optional[Path] = None):
        """
        Arguments:
            name: The name of this register list.
                Typically the name of the module that uses it.
            source_definition_file: The source file that defined this register list.
                Will be displayed in generated source code and documentation for traceability.

                Can be set to ``None`` if this information does not make sense in the current
                use case.
        """
        self.name = name
        self.source_definition_file = source_definition_file

        self.register_objects: list[Union[Register, RegisterArray]] = []
        self.constants: list["Constant"] = []

    @classmethod
    def from_default_registers(
        cls, name: str, source_definition_file: Path, default_registers: list[Register]
    ) -> "RegisterList":
        """
        Factory method. Create a ``RegisterList`` object from a plain list of registers.

        Arguments:
            name: The name of this register list.
            source_definition_file: The source file that defined this register list.
                Will be displayed in generated source code and documentation for traceability.

                Can be set to ``None`` if this information does not make sense in the current
                use case.
            default_registers: These registers will be inserted at the beginning of the
                register list.
        """
        # Before proceeding, perform a basic sanity check.
        # If the indexes are not correct, that will cause problems with the default registers
        # as well as all upcoming registers.
        for list_idx, register in enumerate(default_registers):
            if register.index != list_idx:
                message = (
                    f'Default register index mismatch for "{register.name}". '
                    f'Got "{register.index}", expected "{list_idx}".'
                )
                raise ValueError(message)

        register_list = cls(name=name, source_definition_file=source_definition_file)
        register_list.register_objects = copy.deepcopy(default_registers)  # type: ignore[arg-type]

        return register_list

    def append_register(self, name: str, mode: "RegisterMode", description: str) -> Register:
        """
        Append a register to this register list.

        Arguments:
            name: The name of the register.
            mode: A mode that decides the behavior of the register.
                See https://hdl-registers.com/rst/basic_feature/basic_feature_register_modes.html
                for more information about the different modes.
            description: Textual register description.
        Return:
            The register object that was created.
        """
        if self.register_objects:
            index = self.register_objects[-1].index + 1
        else:
            index = 0

        register = Register(name, index, mode, description)
        self.register_objects.append(register)

        return register

    def append_register_array(self, name: str, length: int, description: str) -> RegisterArray:
        """
        Append a register array to this list.

        Arguments:
            name: The name of the register array.
            length: The number of times the register sequence shall be repeated.
            description: Textual description of the register array.
        Return:
            The register array object that was created.
        """
        if self.register_objects:
            base_index = self.register_objects[-1].index + 1
        else:
            base_index = 0
        register_array = RegisterArray(
            name=name, base_index=base_index, length=length, description=description
        )

        self.register_objects.append(register_array)
        return register_array

    def get_register(
        self, register_name: str, register_array_name: Optional[str] = None
    ) -> Register:
        """
        Get a register from this list.
        Will raise exception if no register matches.

        If ``register_array_name`` is specified, this method will search for registers within
        that array.
        If it is not specified, the method will only search for plain registers (not registers
        in any arrays).

        Arguments:
            register_name: The name of the register.
            register_array_name: If the register is within a register array, this is the name of
                the array.
        Return:
            The register.
        """
        if register_array_name is not None:
            register_array = self.get_register_array(name=register_array_name)
            return register_array.get_register(name=register_name)

        for register_object in self.register_objects:
            if isinstance(register_object, Register) and register_object.name == register_name:
                return register_object

        raise ValueError(
            f'Could not find register "{register_name}" within register list "{self.name}"'
        )

    def get_register_array(self, name: str) -> RegisterArray:
        """
        Get a register array from this list. Will raise exception if no register array matches.

        Arguments:
            name: The name of the register array.
        Return:
            The register array.
        """
        for register_object in self.register_objects:
            if isinstance(register_object, RegisterArray) and register_object.name == name:
                return register_object

        raise ValueError(
            f'Could not find register array "{name}" within register list "{self.name}"'
        )

    def get_register_index(
        self,
        register_name: str,
        register_array_name: Optional[str] = None,
        register_array_index: Optional[int] = None,
    ) -> int:
        """
        Get the zero-based index within the register list for the specified register.

        Arguments:
            register_name: The name of the register.
            register_array_name: If the register is within a register array, the name of the array
                must be specified.
            register_array_index: If the register is within a register array, the array iteration
                index must be specified.

        Return:
            The index.
        """
        if register_array_name is None or register_array_index is None:
            # Target is plain register
            register = self.get_register(register_name=register_name)

            return register.index

        # Target is in register array
        register_array = self.get_register_array(name=register_array_name)
        register_array_start_index = register_array.get_start_index(
            array_index=register_array_index
        )

        register = register_array.get_register(name=register_name)
        register_index = register.index

        return register_array_start_index + register_index

    def add_constant(
        self,
        name: str,
        value: Union[bool, float, int, str, UnsignedVector],
        description: str,
    ) -> "Constant":
        """
        Add a constant. Will be available in the generated packages and headers.
        Will automatically determine the type of the constant based on the type of the
        ``value`` argument.

        Arguments:
            name: The name of the constant.
            value: The constant value.
            description: Textual description for the constant.
        Return:
            The constant object that was created.
        """
        # Note that this is a sub-type of 'int', hence it must be before the check below.
        if isinstance(value, bool):
            constant: "Constant" = BooleanConstant(name=name, value=value, description=description)

        elif isinstance(value, int):
            constant = IntegerConstant(name=name, value=value, description=description)

        elif isinstance(value, float):
            constant = FloatConstant(name=name, value=value, description=description)

        # Note that this is a sub-type of 'str', hence it must be before the check below.
        elif isinstance(value, UnsignedVector):
            constant = UnsignedVectorConstant(name=name, value=value, description=description)

        elif isinstance(value, str):
            constant = StringConstant(name=name, value=value, description=description)

        else:
            message = f'Error while parsing constant "{name}": Unknown type "{type(value)}".'
            raise TypeError(message)

        self.constants.append(constant)
        return constant

    def get_constant(self, name: str) -> "Constant":
        """
        Get a constant from this list. Will raise exception if no constant matches.

        Arguments:
            name: The name of the constant.
        Return:
            The constant.
        """
        for constant in self.constants:
            if constant.name == name:
                return constant

        raise ValueError(f'Could not find constant "{name}" within register list "{self.name}"')

    @property
    def object_hash(self) -> str:
        """
        Get a hash of this object representation.
        SHA1 is the fastest method according to e.g.
        http://atodorov.org/blog/2013/02/05/performance-test-md5-sha1-sha256-sha512/
        Result is a lowercase hexadecimal string.
        """
        return hashlib.sha1(repr(self).encode()).hexdigest()

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(\
name={self.name},\
source_definition_file={repr(self.source_definition_file)},\
register_objects={','.join([repr(register_object) for register_object in self.register_objects])},\
constants={','.join([repr(constant) for constant in self.constants])},\
)"""
