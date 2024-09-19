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
from typing import TYPE_CHECKING, Any, Optional

# Third party libraries
from black import Mode, format_str

# First party libraries
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.field.numerical_interpretation import (
    Fixed,
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.register import Register

if TYPE_CHECKING:
    # First party libraries
    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register_array import RegisterArray


class PythonAccessorGenerator(RegisterCodeGenerator):
    """
    Generate a Python class to read/write/print register and field values on a target device.
    Field and register values are represented using their native Python types, for easy handling.
    Meaning, no manual type casting back and forth for the user.

    See the :ref:`generator_python` article for usage details.
    See also :class:`.PythonRegisterAccessorInterface`.

    Needs to have the result from the :class:`.PythonPickleGenerator` generator in the
    same output folder.
    """

    __version__ = "0.1.0"

    SHORT_DESCRIPTION = "Python accessor"

    COMMENT_START = "#"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}_accessor.py"

    def get_code(self, **kwargs: Any) -> str:
        """
        Get Python code for accessing register and field values.
        """
        class_name = f"{self.to_pascal_case(self.name)}Accessor"

        if self.register_list.register_objects:
            last_index = self.register_list.register_objects[-1].index
        else:
            last_index = -1

        register_access_methods = self._get_register_access_methods()
        register_value_types = self._get_register_value_types()

        result = f'''\
{self.header}
# Standard libraries
import pickle
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING
from termcolor import colored

# Third party libraries
from hdl_registers.field.numerical_interpretation import to_unsigned_binary
from tsfpga.math_utils import to_binary_nibble_string, to_hex_byte_string

if TYPE_CHECKING:
    # Third party libraries
    from hdl_registers.generator.python.register_accessor_interface import (
        PythonRegisterAccessorInterface,
    )
    from hdl_registers.register_list import RegisterList


THIS_DIR = Path(__file__).parent


class {class_name}:
    """
    Class to read/write registers and fields of the ``{self.name}`` register list.
    """

    def __init__(self, register_accessor: "PythonRegisterAccessorInterface"):
        """
        Arguments:
            register_accessor: Object that implements register access methods in your system.
                Must have the methods ``read_register`` and ``write_register``
                with the same interface and behavior as the interface class
                :class:`.PythonRegisterAccessorInterface`.
                It is highly recommended that your accessor class inherits from that class.
        """
        self._register_accessor = register_accessor

        pickle_path = THIS_DIR / "{self.name}.pickle"
        if not pickle_path.exists():
            raise FileNotFoundError(
                f"Could not find the pickle file {{pickle_path}}, "
                "make sure this artifact is generated."
            )

        with pickle_path.open("rb") as file_handle:
            self._register_list: "RegisterList" = pickle.load(file_handle)

    def _read_register(self, register_index: int) -> int:
        """
        Read a register value via the register accessor provided by the user.
        We perform sanity checks in both directions here, since this is the glue logic between
        two interfaces.
        """
        if not 0 <= register_index <= {last_index}:
            raise ValueError(
                f"Register index {{register_index}} out of range. This is likely an internal error."
            )

        register_value = self._register_accessor.read_register(
            register_list_name="{self.register_list.name}", register_address=4 * register_index
        )
        if not 0 <= register_value < 2 ** 32:
            raise ValueError(
                f'Register read value "{{register_value}}" from accessor is out of range.'
            )

        return register_value

    def _write_register(self, register_index: int, register_value: int) -> None:
        """
        Write a register value via the register accessor provided by the user.
        We perform sanity checks in both directions here, since this is the glue logic between
        two interfaces.
        """
        if not 0 <= register_index <= {last_index}:
            raise ValueError(
                f"Register index {{register_index}} out of range. This is likely an internal error."
            )

        if not 0 <= register_value < 2 ** 32:
            raise ValueError(
                f'Register write value "{{register_value}}" is out of range.'
            )

        self._register_accessor.write_register(
            register_list_name="{self.register_list.name}",
            register_address=4 * register_index,
            register_value=register_value
        )
{register_access_methods}\


def get_accessor(register_accessor: "PythonRegisterAccessorInterface") -> {class_name}:
    """
    Factory function to create an accessor object.
    """
    return {class_name}(register_accessor=register_accessor)


def _format_unsigned_number(value: int, width: int, include_decimal: bool=True) -> str:
        """
        Format a string representation of the provided ``value``.
        Suitable for printing field and register values.
        """
        result = ""
        if include_decimal:
            result += f"unsigned decimal {{value}}, "

        hex_string = to_hex_byte_string(value=value, result_width_bits=width)
        result += f"hexadecimal {{hex_string}}, "

        binary_string = to_binary_nibble_string(value=value, result_width_bits=width)
        result += f"binary {{binary_string}}"

        return result

{register_value_types}
'''
        return self._format_with_black(result)

    def _get_register_value_type_name(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        The name of the python type that represents the native Python value of a register.
        Either a built-in type (int) or a dataclass that we define in another place in the file.
        """
        if not register.fields:
            return "int"

        register_name = self.qualified_register_name(
            register=register, register_array=register_array
        )
        return f"{self.to_pascal_case(register_name)}Value"

    def _get_register_value_types(self) -> str:
        """
        Get all the classes needed to represent register values.
        One dataclass for each register that contains fields.
        """
        result = ""

        for register, register_array in self.iterate_registers():
            if not register.fields:
                continue

            result += self._get_register_value_type(
                register=register, register_array=register_array
            )

        return result

    def _get_register_value_type(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get class for register value for one specific register.
        Assumes that the register has fields.
        """
        class_name = self._get_register_value_type_name(
            register=register, register_array=register_array
        )
        register_description = self.register_description(
            register=register, register_array=register_array
        )
        result = f'''
@dataclass
class {class_name}:
    """
    Represents the field values of the {register_description}.
    Uses native Python types for easy handling.
    """
'''
        for field in register.fields:
            if isinstance(field, Enumeration):
                elements = [
                    f'{element.name.upper()} = "{element.name}"' for element in field.elements
                ]
                separator = "\n        "
                result += f'''
    class {self._get_field_python_type_name(field=field)}(Enum):
        """
        Enumeration elements for the ``{field.name}`` field.
        """
        {separator.join(elements)}

'''
        for field in register.fields:
            field_comment = self._get_field_type_and_range_comment(field=field)
            field_type = self._get_field_python_type_name(field=field)
            result += f"""\
    # {field_comment}
    {field.name}: {field_type}
"""
        result += '''
    def to_string(self, indentation: str="", no_color: bool = False) -> str:
        """
        Get a string of the field values, suitable for printing.

        Arguments:
            indentation: Optionally indent each field value line.
            no_color: Disable color output.
                Can also be achieved by setting the environment variable ``NO_COLOR`` to any value.
        """
        values = []

'''
        for field in register.fields:
            result += self._get_field_type_to_string_value(field=field)
            result += f"""\
        field_name = colored("{field.name}", color="light_cyan", no_color=no_color)
        values.append(f"{{indentation}}{{field_name}}: {{value}}")

"""

        result += '        return "\\n".join(values)'

        return result

    def _get_field_python_type_name(
        self, field: "RegisterField", global_type_name: Optional[str] = None
    ) -> str:
        """
        Get the Python type name for the native type that represents a field value.
        Is either a built-in type (e.g. int) or a type that we define in another place in the file.

        Arguments:
            global_type_name: When the field type is a custom one, the type class is declared within
                the dataclass of the register.
                When the field type is referenced within the register class, its local name can be
                used, but when we want to reference it outside of the register class, we need to
                know the name of the register value class also.
        """
        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, Fixed):
                return "float"

            return "int"

        if isinstance(field, Bit):
            return "int"

        if isinstance(field, Enumeration):
            local_name = self.to_pascal_case(field.name)

            if global_type_name is None:
                return local_name

            return f"{global_type_name}.{local_name}"

        if isinstance(field, Integer):
            return "int"

        raise ValueError(f"Unknown field {field}")

    @staticmethod
    def _get_field_type_and_range_comment(field: "RegisterField") -> str:
        """
        A string the describes the field.
        Suitable for descriptions in accessor methods.
        """
        if isinstance(field, BitVector):
            if field.numerical_interpretation.is_signed:
                sign_comment = "Signed"
            else:
                sign_comment = "Unsigned"

            range_comment = (
                f"Range: {field.numerical_interpretation.min_value} - "
                f"{field.numerical_interpretation.max_value}."
            )

            if isinstance(field.numerical_interpretation, (Signed, Unsigned)):
                return f"{sign_comment} bit vector. Width: {field.width}. {range_comment}"

            if isinstance(field.numerical_interpretation, (SignedFixedPoint, UnsignedFixedPoint)):
                integer_width = (
                    f"Integer width: {field.numerical_interpretation.integer_bit_width}."
                )
                fractional_width = (
                    f"Fractional width: {field.numerical_interpretation.fraction_bit_width}."
                )
                width_comment = f"{integer_width} {fractional_width} "
                return f"{sign_comment} fixed-point bit vector. {width_comment}{range_comment}"

            raise ValueError(f"Unknown field type {field}")

        if isinstance(field, Bit):
            return "Single bit. Range: 0-1."

        if isinstance(field, Enumeration):
            element_names = ", ".join([element.name.upper() for element in field.elements])
            return f"Enumeration. Possible values: {element_names}."

        if isinstance(field, Integer):
            if field.is_signed:
                sign_comment = "Signed"
            else:
                sign_comment = "Unsigned"
            return f"{sign_comment} integer. Range: {field.min_value} - {field.max_value}."

        raise ValueError(f"Unknown field {field}")

    def _get_field_type_to_string_value(self, field: "RegisterField") -> str:
        """
        Get Python code that casts a field value to a string suitable for printing.
        """
        field_value = f"self.{field.name}"

        if isinstance(field, Enumeration):
            field_type = self._get_field_python_type_name(field=field)
            return f"""
        enum_index = list(self.{field_type}).index({field_value})
        value = f"{{{field_value}.name}} ({{enum_index}})"
"""
        if isinstance(field, Integer):
            unsigned = (
                f"to_unsigned_binary(num_bits={field.width}, value={field_value}, is_signed=True)"
                if field.is_signed
                else field_value
            )

            return f"""
        unsigned_value = {unsigned}
        value_comment = _format_unsigned_number(
            value=unsigned_value, width={field.width}, include_decimal={field.is_signed}
        )
        value = f"{{{field_value}}} ({{value_comment}})"
"""
        if isinstance(field, Bit):
            return f"        value = str(self.{field.name})\n"

        if isinstance(field, BitVector):
            if isinstance(field.numerical_interpretation, Unsigned):
                return f"""
        value_comment = _format_unsigned_number(
            value={field_value}, width={field.width}, include_decimal=False
        )
        value = f"{{{field_value}}} ({{value_comment}})"
"""
            if isinstance(field.numerical_interpretation, Signed):
                return f"""
        unsigned_value = to_unsigned_binary(
            num_bits={field.width}, value={field_value}, is_signed=True
        )
        value_comment = _format_unsigned_number(
            value=unsigned_value, width={field.width}
        )
        value = f"{{{field_value}}} ({{value_comment}})"
"""

            if isinstance(field.numerical_interpretation, (UnsignedFixedPoint, SignedFixedPoint)):
                return f"""
        unsigned_value = to_unsigned_binary(
            num_bits={field.width},
            value={field_value},
            num_integer_bits={field.numerical_interpretation.integer_bit_width},
            num_fractional_bits={field.numerical_interpretation.fraction_bit_width},
            is_signed={field.numerical_interpretation.is_signed}
        )
        value_comment = _format_unsigned_number(
            value=unsigned_value, width={field.width}
        )
        value = f"{{{field_value}}} ({{value_comment}})"
"""

            raise ValueError(f"Unknown field type {field}")

        raise ValueError(f"Unknown field {field}")

    def _get_register_access_methods(self) -> str:
        """
        Get all the methods to read and write registers and fields.
        Will only include methods for registers that are accessible in either direction.
        """
        result = ""

        for register, register_array in self.iterate_registers():
            if register.mode.software_can_read:
                if register.fields:
                    result += self._get_register_read_as_class(
                        register=register, register_array=register_array
                    )
                else:
                    result += self._get_register_read_as_integer(
                        register=register, register_array=register_array
                    )

            if register.mode.software_can_write:
                if register.fields:
                    result += self._get_register_write_as_class(
                        register=register, register_array=register_array
                    )
                    result += self._get_fields_write(
                        register=register, register_array=register_array
                    )
                else:
                    result += self._get_register_write_as_integer(
                        register=register, register_array=register_array
                    )

        result += self._get_print_registers()

        return result

    def _get_register_read_as_class(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        For a register that has fields, the unsigned value read from the bus is converted to a
        custom class that represents the field values.
        """
        register_value_type_name = self._get_register_value_type_name(
            register=register, register_array=register_array
        )
        register_array_name = f'"{register_array.name}"' if register_array else "None"
        common = self._get_register_read_common(
            register=register,
            register_array=register_array,
            register_value_type_name=register_value_type_name,
        )
        result = f"""{common}\
        register = self._register_list.get_register(
            register_name="{register.name}", register_array_name={register_array_name}
        )
        return {register_value_type_name}(
"""
        for field_idx, field in enumerate(register.fields):
            get_value = f"register.fields[{field_idx}].get_value(register_value=value)"

            if isinstance(field, Enumeration):
                type_name = self._get_field_python_type_name(
                    field=field, global_type_name=register_value_type_name
                )
                get_value = f"{type_name}({get_value}.name)"

            result += f"{field.name}={get_value},"

        result += ")"
        return result

    def _get_register_read_as_integer(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        For registers without fields, the unsigned value read from the bus is simply passed on.
        """
        common = self._get_register_read_common(
            register=register,
            register_array=register_array,
            register_value_type_name="int",
            extra_docstring=(
                "        Return type is a plain unsigned integer "
                "since the register has no fields.\n"
            ),
        )
        return f"""{common}\
        return value
"""

    def _get_register_read_common(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        register_value_type_name: str,
        extra_docstring: str = "",
    ) -> str:
        """
        Common register read portions for both 'integer' and 'class'.
        """
        register_name = self._get_semi_qualified_register_name(
            register=register, register_array=register_array
        )
        register_description = self.register_description(
            register=register, register_array=register_array
        )

        array_index_argument = ", array_index: int" if register_array else ""
        index_variable = self._get_index_variable(register=register, register_array=register_array)
        array_index_documentation = (
            f"""
        Arguments:
            array_index: Register array iteration index (range 0-{register_array.length - 1}).
"""
            if register_array
            else ""
        )
        return f'''
    def read_{register_name}(self{array_index_argument}) -> "{register_value_type_name}":
        """
        Read the {register_description}.
{extra_docstring}\
{array_index_documentation}\
        """
{index_variable}\
        value = self._read_register(register_index=index)
'''

    def _get_register_write_as_class(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        For a register that has fields, the value to be written is provided as a custom class.
        This must be converted to an unsigned integer before writing to the bus.
        """
        register_value_type_name = self._get_register_value_type_name(
            register=register, register_array=register_array
        )
        register_array_name = f'"{register_array.name}"' if register_array else "None"
        common = self._get_register_write_common(
            register=register,
            register_array=register_array,
            register_value_type_name=register_value_type_name,
            register_value_docstring="Object with the field values that shall be written",
        )
        result = f"""{common}\
        register = self._register_list.get_register(
            register_name="{register.name}", register_array_name={register_array_name}
        )
        integer_value = 0
"""
        for field_idx, field in enumerate(register.fields):
            convert = f"integer_value += register.fields[{field_idx}].set_value(field_value="

            if isinstance(field, Enumeration):
                convert += (
                    f"register.fields[{field_idx}]."
                    f"get_element_by_name(register_value.{field.name}.value)"
                )
            else:
                convert += f"register_value.{field.name}"

            result += f"        {convert})\n"

        result += """        self._write_register(
    register_index=index, register_value=integer_value
)
"""
        return result

    def _get_register_write_as_integer(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        For a register without fields, the value to be written is provided as an unsigned
        integer that can be written straight away.
        """
        result = self._get_register_write_common(
            register=register,
            register_array=register_array,
            register_value_type_name="int",
            register_value_docstring=(
                "Value to be written.\n"
                "                Is a plain unsigned integer since the register has no fields"
            ),
        )

        result += """        self._write_register(
    register_index=index, register_value=register_value
)
"""
        return result

    def _get_register_write_common(
        self,
        register: "Register",
        register_array: Optional["RegisterArray"],
        register_value_type_name: str,
        register_value_docstring: str,
    ) -> str:
        """
        Common register write portions for both 'integer' and 'class'.
        """
        register_name = self._get_semi_qualified_register_name(
            register=register, register_array=register_array
        )
        register_description = self.register_description(
            register=register, register_array=register_array
        )

        array_index_argument = ", array_index: int" if register_array else ""
        index_variable = self._get_index_variable(register=register, register_array=register_array)
        array_index_documentation = (
            (
                "            array_index: Register array iteration "
                f"index (range 0-{register_array.length - 1}).\n"
            )
            if register_array
            else ""
        )
        return f'''
    def write_{register_name}(self, \
register_value: "{register_value_type_name}"{array_index_argument}) -> None:
        """
        Write the whole {register_description}.

        Arguments:
            register_value: {register_value_docstring}.
{array_index_documentation}\
        """
{index_variable}\
'''

    @staticmethod
    def _get_index_variable(register: "Register", register_array: Optional["RegisterArray"]) -> str:
        """
        Get Python code that extracts the register index from the register list.
        """
        register_array_name = f'"{register_array.name}"' if register_array else "None"
        array_index_value = "array_index" if register_array else "None"
        return f"""\
        index = self._register_list.get_register_index(
            register_name="{register.name}",
            register_array_name={register_array_name},
            register_array_index={array_index_value},
        )
"""

    def _get_fields_write(
        self, register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Get Python class methods for writing the values of each field in the register.
        Will either write the whole register or read-modify-write the register.
        """
        result = ""

        for field_idx, field in enumerate(register.fields):
            if self.field_setter_should_read_modify_write(register=register):
                result += self._get_field_read_modify_write(
                    field=field, register=register, register_array=register_array
                )
            else:
                result += self._get_field_write(
                    field_idx=field_idx,
                    field=field,
                    register=register,
                    register_array=register_array,
                )

        return result

    def _get_field_read_modify_write(
        self,
        field: "RegisterField",
        register: "Register",
        register_array: Optional["RegisterArray"],
    ) -> str:
        """
        Python class method to read-modify-write a register, updating the value of one field.
        """
        result = self._get_field_write_common(
            field=field,
            register=register,
            register_array=register_array,
            docstring=f"""\
Will read-modify-write the ``{register.name}`` register, setting the ``{field.name}`` field
        to the provided value, while leaving the other fields at their previous values.
""",
        )

        register_name = self._get_semi_qualified_register_name(
            register=register, register_array=register_array
        )
        array_index_association_plain = "array_index=array_index" if register_array else ""
        array_index_association_comma = ", array_index=array_index" if register_array else ""
        result += f"""\
        register_value = self.read_{register_name}({array_index_association_plain})
        register_value.{field.name} = field_value
        self.write_{register_name}(register_value=register_value{array_index_association_comma})
"""

        return result

    def _get_field_write(
        self,
        field_idx: int,
        field: "RegisterField",
        register: "Register",
        register_array: Optional["RegisterArray"],
    ) -> str:
        """
        Python class method to write a register, setting the value of one field only.
        """
        result = self._get_field_write_common(
            field=field,
            register=register,
            register_array=register_array,
            docstring=f"""\
Will write the ``{register.name}`` register, setting the ``{field.name}`` field to the
        provided value, and all other fields to their default values.
""",
        )

        index_variable = self._get_index_variable(register=register, register_array=register_array)
        register_array_name = f'"{register_array.name}"' if register_array else "None"
        result += f"""\
{index_variable}
        register = self._register_list.get_register(
            register_name="{register.name}", register_array_name={register_array_name}
        )
        register_value = 0
"""

        for iterate_field_idx in range(len(register.fields)):
            iterate_field = f"register.fields[{iterate_field_idx}]"
            result += "        register_value += "
            if iterate_field_idx == field_idx:
                if isinstance(field, Enumeration):
                    result += (
                        f"{iterate_field}.set_value({iterate_field}."
                        "get_element_by_name(field_value.value))"
                    )
                else:
                    result += f"{iterate_field}.set_value(field_value)"
            else:
                result += f"{iterate_field}.default_value_uint << {iterate_field}.base_index"

            result += "\n"

        result += """
        self._write_register(register_index=index, register_value=register_value)
        """

        return result

    def _get_field_write_common(
        self,
        field: "RegisterField",
        register: "Register",
        register_array: Optional["RegisterArray"],
        docstring: str,
    ) -> str:
        """
        Common portions for field write methods.
        """
        field_name = self._get_semi_qualified_field_name(
            field=field, register=register, register_array=register_array
        )
        field_value_type_name = self._get_field_python_type_name(
            field=field,
            global_type_name=self._get_register_value_type_name(
                register=register, register_array=register_array
            ),
        )
        field_description = self.field_description(
            register=register, field=field, register_array=register_array
        )
        field_comment = self._get_field_type_and_range_comment(field=field)

        array_index_argument = ", array_index: int" if register_array else ""
        array_index_documentation = (
            (
                "            array_index: Register array iteration "
                f"index (range 0-{register_array.length - 1}).\n"
            )
            if register_array
            else ""
        )
        return f'''
    def write_{field_name}(self, \
field_value: "{field_value_type_name}"{array_index_argument}) -> None:
        """
        Write the {field_description}.
        {docstring}\

        Arguments:
            field_value: The field value to be written.
                {field_comment}
{array_index_documentation}\
        """
'''

    @staticmethod
    def _get_semi_qualified_register_name(
        register: "Register", register_array: Optional["RegisterArray"]
    ) -> str:
        """
        Base name of register access methods.
        Name is a contrast to 'self.qualified_register_name'.
        """
        if register_array is None:
            return register.name

        return f"{register_array.name}_{register.name}"

    def _get_semi_qualified_field_name(
        self,
        field: "RegisterField",
        register: "Register",
        register_array: Optional["RegisterArray"],
    ) -> str:
        """
        Base name of field access methods.
        Name is a contrast to 'self.qualified_field_name'.
        """
        register_name = self._get_semi_qualified_register_name(
            register=register, register_array=register_array
        )

        return f"{register_name}_{field.name}"

    def _get_print_registers(self) -> str:
        """
        Python method to print all registers and their values.
        """
        result = '''
    def print_registers(self, no_color: bool=False) -> None:
        """
        Print all registers and their values to STDOUT.

        Arguments:
            no_color: Disable color output.
                Can also be achieved by setting the environment variable ``NO_COLOR`` to any value.
        """
'''

        for register_object in self.register_list.register_objects:
            if isinstance(register_object, Register):
                result += self._get_print_register(
                    is_readable=register_object.mode.software_can_read, register=register_object
                )
            else:
                for array_index in range(register_object.length):
                    for register in register_object.registers:
                        result += self._get_print_register(
                            is_readable=register.mode.software_can_read,
                            register=register,
                            register_array=register_object,
                            register_array_index=array_index,
                        )

        return result

    @staticmethod
    def _get_print_register(
        is_readable: bool,
        register: "Register",
        register_array: Optional["RegisterArray"] = None,
        register_array_index: Optional[int] = None,
    ) -> str:
        """
        Python code to print a single register and its field values.
        """
        if register_array is not None and register_array_index is not None:
            name = f"{register_array.name}[{register_array_index}].{register.name}"
            index = (
                register_array.get_start_index(array_index=register_array_index) + register.index
            )
            read = (
                f"self.read_{register_array.name}_{register.name}"
                f"(array_index={register_array_index})"
            )
        else:
            name = register.name
            index = register.index
            read = f"self.read_{register.name}()"

        heading = f"""\
print(
    colored("Register", color="light_yellow", no_color=no_color)
    + " '{name}' "
    + colored("." * {67 - len(name)}, color="dark_grey", no_color=no_color)
    + " (index {index}, address {4 * index}):"
)
"""

        if not is_readable:
            return f"""\
        {heading}\
        print("  Not readable.\\n")

"""

        read_value = f"register_value = {read}\n"
        if not register.fields:
            return f"""\
        {heading}\
        {read_value}\
        formatted_value = _format_unsigned_number(value=register_value, width=32)
        print(f"  {{formatted_value}}\\n")

"""

        return f"""\
        {heading}\
        {read_value}\
        print(register_value.to_string(indentation="  ", no_color=no_color))
        print()

"""

    def _format_with_black(self, code: str) -> str:
        """
        Format the code with the Black code formatter, so the result always looks perfect.
        Means that we can be a little more sloppy when we construct the generated code.
        But even then, it would be a huge pain to determine when to break and not break lines.
        So it's easier to just apply a stable and fast formatter.
        """
        # Not that this is NOT a public API:
        # * https://stackoverflow.com/questions/57652922
        # * https://github.com/psf/black/issues/779
        # The simple mode construction below will use the default settings for black
        # (magic trailing comma, etc) apart from the line length.
        # This is identical to how Python files in this project are formatted.
        # Should give a consistent look and feel.
        mode = Mode(line_length=100)
        return format_str(src_contents=code, mode=mode)
