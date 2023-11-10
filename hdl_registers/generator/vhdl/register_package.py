# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# First party libraries
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.boolean_constant import BooleanConstant
from hdl_registers.constant.float_constant import FloatConstant
from hdl_registers.constant.integer_constant import IntegerConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.field.register_field import RegisterField
from hdl_registers.field.register_field_type import (
    Signed,
    SignedFixedPoint,
    Unsigned,
    UnsignedFixedPoint,
)
from hdl_registers.register import Register

# Local folder libraries
from .vhdl_generator_common import (
    BUS_ACCESS_DIRECTIONS,
    FABRIC_ACCESS_DIRECTIONS,
    VhdlGeneratorCommon,
)

# pylint: disable=too-many-lines


class VhdlRegisterPackageGenerator(VhdlGeneratorCommon):
    """
    Generate a VHDL package with register information.
    """

    SHORT_DESCRIPTION = "VHDL register package"

    @property
    def output_file(self):
        return self.output_folder / f"{self.name}_regs_pkg.vhd"

    def _constants(self):
        """
        A set of VHDL constants, corresponding to the provided register constants.
        """
        vhdl = """\
  -- ---------------------------------------------------------------------------
  -- Values of register constants.
"""

        for constant in self.iterate_constants():
            if isinstance(constant, BooleanConstant):
                type_declaration = "boolean"
                value = str(constant.value).lower()
            elif isinstance(constant, IntegerConstant):
                type_declaration = "integer"
                value = str(constant.value)
            elif isinstance(constant, FloatConstant):
                # At least 64 bits (IEEE 1076-2008, 5.2.5.1).
                type_declaration = "real"
                # Note that casting a Python float to string guarantees full precision in the
                # resulting string: https://stackoverflow.com/a/60026172
                value = str(constant.value)
            elif isinstance(constant, StringConstant):
                type_declaration = "string"
                value = f'"{constant.value}"'
            elif isinstance(constant, UnsignedVectorConstant):
                type_declaration = f"unsigned({constant.width} - 1 downto 0)"

                if constant.is_hexadecimal_not_binary:
                    # Underscore separator is allowed in VHDL when defining a hexadecimal SLV.
                    value = f'x"{constant.value}"'
                else:
                    # But not when defining a binary SLV.
                    value = f'"{constant.value_without_separator}"'
            else:
                raise ValueError(f"Got unexpected constant type. {constant}")

            vhdl += (
                "  constant "
                f"{self.name}_constant_{constant.name} : {type_declaration} := {value};\n"
            )

        vhdl += "\n"

        return vhdl

    @property
    def _register_range_type_name(self):
        """
        Name of the type which is the legal index range of registers.
        """
        return f"{self.name}_reg_range"

    def _register_range(self):
        """
        A VHDL type that defines the legal range of register indexes.
        """
        last_index = self.register_list.register_objects[-1].index
        vhdl = f"""\
  -- ---------------------------------------------------------------------------
  -- The valid range of register indexes.
  subtype {self._register_range_type_name} is natural range 0 to {last_index};

"""
        return vhdl

    def _array_constants(self):
        """
        A list of constants defining how many times each register array is repeated.
        """
        vhdl = ""
        for register_array in self.iterate_register_arrays():
            array_name = self.register_array_name(register_array=register_array)

            vhdl += f"""\
  -- Number of times the '{register_array.name}' register array is repeated.
  constant {array_name}_array_length : natural := {register_array.length};
  -- Range for indexing '{register_array.name}' register array repetitions.
  subtype {array_name}_range is natural range 0 to {register_array.length - 1};

"""

        return vhdl

    def _array_register_index_function_signature(self, register, register_array):
        """
        Signature for the function that returns a register index for the specified index in a
        register array.
        """
        array_name = self.register_array_name(register_array=register_array)
        vhdl = f"""\
  function {self.register_name(register, register_array)}(
    array_index : {array_name}_range
  ) return {self._register_range_type_name}"""
        return vhdl

    def _register_indexes(self):
        """
        A set of named constants for the register index of each register.
        """
        vhdl = "  -- Register indexes, within the list of registers.\n"

        for register, register_array in self.iterate_registers():
            if register_array is None:
                vhdl += (
                    f"  constant {self.register_name(register)} : natural := {register.index};\n"
                )
            else:
                vhdl += (
                    f"{self._array_register_index_function_signature(register, register_array)};\n"
                )

        vhdl += "\n"

        return vhdl

    def _register_map_head(self):
        """
        Get constants mapping the register indexes to register modes.
        """
        map_name = f"{self.name}_reg_map"

        vhdl = f"""\
  -- Declare 'reg_map' and 'regs_init' constants here but define them in body (deferred constants).
  -- So that functions have been elaborated when they are called.
  -- Needed for ModelSim compilation to pass.

  -- To be used as the 'regs' generic of 'axi_lite_reg_file.vhd'.
  constant {map_name} : reg_definition_vec_t({self._register_range_type_name});

  -- To be used for the 'regs_up' and 'regs_down' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.name}_regs_t is reg_vec_t({self._register_range_type_name});
  -- To be used as the 'default_values' generic of 'axi_lite_reg_file.vhd'.
  constant {self.name}_regs_init : {self.name}_regs_t;

  -- To be used for the 'reg_was_read' and 'reg_was_written' ports of 'axi_lite_reg_file.vhd'.
  subtype {self.name}_reg_was_accessed_t is \
std_ulogic_vector({self._register_range_type_name});

"""

        return vhdl

    def _field_declarations(self):
        """
        For every field in every register (plain or in array):

        * Bit index range
        * VHDL type
        * width constant
        * conversion function declarations to/from type and SLV
        """
        vhdl = ""

        for register, register_array in self.iterate_registers():
            if not register.fields:
                continue

            register_description = self.register_description(
                register=register, register_array=register_array
            )

            vhdl += f"""\
  -- -----------------------------------------------------------------------------
  -- Fields in the {register_description}.
"""

            for field in register.fields:
                field_name = self.field_name(
                    register=register, register_array=register_array, field=field
                )
                field_is_bit = isinstance(field, Bit)

                vhdl += f"  -- Range of the '{field.name}' field.\n"
                if field_is_bit:
                    # A bit field's "range" is simply an index, so the indexing a register SLV
                    # gives a std_logic value.
                    vhdl += f"  constant {field_name} : natural := {field.base_index};\n"
                else:
                    # For other fields its an actual range.
                    vhdl += f"""\
  subtype {field_name} is natural \
range {field.width + field.base_index - 1} downto {field.base_index};
  -- Width of the '{field.name}' field.
  constant {field_name}_width : positive := {field.width};
  -- Type for the '{field.name}' field.
{self._field_type_declaration(field=field, field_name=field_name)}
"""

                vhdl += f"""\
  -- Default value of the '{field.name}' field.
  {self._field_init_value(field=field, field_name=field_name)}
{self._field_conversion_function_declarations(field=field, field_name=field_name)}
"""

        return vhdl

    def _field_type_declaration(self, field: RegisterField, field_name: str):
        """
        Get a type declaration for the native VHDL type that corresponds to the field's type.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        if isinstance(field, BitVector):
            if isinstance(field.field_type, Unsigned):
                return f"  subtype {field_name}_t is u_unsigned({field.width - 1} downto 0);"

            if isinstance(field.field_type, Signed):
                return f"  subtype {field_name}_t is u_signed({field.width - 1} downto 0);"

            if isinstance(field.field_type, UnsignedFixedPoint):
                return (
                    f"  subtype {field_name}_t is ufixed("
                    f"{field.field_type.max_bit_index} downto {field.field_type.min_bit_index});"
                )

            if isinstance(field.field_type, SignedFixedPoint):
                return (
                    f"  subtype {field_name}_t is sfixed("
                    f"{field.field_type.max_bit_index} downto {field.field_type.min_bit_index});"
                )

            raise TypeError(f'Got unexpected bit vector type for field: "{field}".')

        if isinstance(field, Enumeration):
            # Enum element names in VHDL are exported to the surrounding scope, causing huge
            # risk of name clashes.
            # At the same time, we want the elements to have somewhat concise names so they are
            # easy to work with.
            # Compromise by prefixing the element names with the field name.
            element_names = [f"{field.name}_{element.name}" for element in field.elements]
            elements = ",\n    ".join(element_names)
            return f"""\
  type {field_name}_t is (
    {elements}
  );\
"""

        if isinstance(field, Integer):
            return (
                f"  subtype {field_name}_t is integer "
                f"range {field.min_value} to {field.max_value};"
            )

        raise TypeError(f'Got unexpected type for field: "{field}".')

    def _field_init_value(self, field: RegisterField, field_name: str):
        """
        Get an init value constant for the field.
        Uses the native VHDL type that corresponds to the field's type.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        result = f"constant {field_name}_init :"

        if isinstance(field, Bit):
            return f"{result} std_ulogic := '{field.default_value}';"

        if isinstance(field, BitVector):
            return f'{result} {field_name}_t := "{field.default_value}";'

        if isinstance(field, Enumeration):
            return f"{result} {field_name}_t := {field.name}_{field.default_value.name};"

        if isinstance(field, Integer):
            return f"{result} {field_name}_t := {field.default_value};"

        raise TypeError(f'Got unexpected type for field: "{field}".')

    def _field_conversion_function_declarations(self, field: RegisterField, field_name: str):
        """
        Function declarations for functions that convert the field's native VHDL representation
        to/from SLV.

        Arguments:
            field: A field.
            field_name: The field's qualified name.
        """
        if isinstance(field, (Bit, BitVector)):
            return ""

        if isinstance(field, (Enumeration, Integer)):
            to_slv_name = self._field_to_slv_function_name(field=field, field_name=field_name)

            return f"""\
  -- Type for the '{field.name}' field as an SLV.
  subtype {field_name}_slv_t is std_ulogic_vector({field.width - 1} downto 0);
  -- Cast a '{field.name}' field value to SLV.
  function {to_slv_name}(data : {field_name}_t) return {field_name}_slv_t;
  -- Get a '{field.name}' field value from a register value.
  function to_{field_name}(data : reg_t) return {field_name}_t;
"""

        raise TypeError(f'Got unexpected type for field: "{field}".')

    @staticmethod
    def _field_to_slv_function_name(field, field_name):
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

    def _register_field_records(self):
        """
        For every register (plain or in array) that has at least on field:

        * Record with members for each field that are of the correct native VHDL type.
        * Default value constant for the above record.
        * Function to convert the above record to SLV.
        * Function to convert a register SLV to the above record.
        """
        vhdl = """\
  -- -----------------------------------------------------------------------------
  -- Record with correctly-typed members for each field in each register.
"""

        for register, register_array in self.iterate_registers():
            if not register.fields:
                continue

            register_name = self.register_name(register=register, register_array=register_array)
            register_description = self.register_description(
                register=register, register_array=register_array
            )

            record = ""
            init = []

            for field in register.fields:
                field_name = self.field_name(
                    register=register, register_array=register_array, field=field
                )
                init.append(f"{field.name} => {field_name}_init")

                if isinstance(field, Bit):
                    record += f"    {field.name} : std_ulogic;\n"
                else:
                    record += f"    {field.name} : {field_name}_t;\n"

            init_str = "    " + ",\n    ".join(init)

            vhdl += f"""\
  -- Fields in the {register_description} as a record.
  type {register_name}_t is record
{record}\
  end record;
  -- Default value for the {register_description} as a record.
  constant {register_name}_init : {register_name}_t := (
{init_str}
  );
  -- Convert a record of the {register_description} to SLV.
  function to_slv(data : {register_name}_t) return reg_t;
  -- Convert an SLV register value to the record for the {register_description}.
  function to_{register_name}(data : reg_t) return {register_name}_t;

"""

        return vhdl

    def _register_records(self):
        """
        Get two records,
        * One with all the registers that are in the 'up' direction.
        * One with all the registers that are in the 'down' direction.

        Along with conversion function declarations to/from SLV.

        In order to create the above records, we have to create partial-array records for each
        register array.
        One record for 'up' and one for 'down', with all registers in the array that are in
        that direction.
        """
        vhdl = ""

        direction = FABRIC_ACCESS_DIRECTIONS["up"]

        if self.has_any_fabric_accessible_register(direction=direction):
            vhdl += self._array_field_records(direction=direction)
            vhdl += self._get_register_record(direction=direction)
            vhdl += f"""\
  -- Convert record with everything in the '{direction.name}' direction to SLV register list.
  function to_slv(data : {self.name}_regs_{direction.name}_t) return {self.name}_regs_t;

"""

        direction = FABRIC_ACCESS_DIRECTIONS["down"]

        if self.has_any_fabric_accessible_register(direction=direction):
            vhdl += self._array_field_records(direction=direction)
            vhdl += self._get_register_record(direction=direction)
            vhdl += f"""\
  -- Convert SLV register list to record with everything in the '{direction.name}' direction.
  function to_{self.name}_regs_{direction.name}(data : {self.name}_regs_t) \
return {self.name}_regs_{direction.name}_t;

"""

        return vhdl

    def _array_field_records(self, direction):
        """
        For every register array that has at least one register in the specified direction:

        * Record with members for each register in the array that is in the specified direction.
        * Default value constant for the above record.
        * VHDL vector type of the above record, ranged per the range of the register array.

        This function assumes that the register map has registers in the given direction.
        """
        vhdl = ""

        for array in self.iterate_fabric_accessible_register_arrays(direction=direction):
            array_name = self.register_array_name(register_array=array)
            vhdl += f"""\
  -- Registers of the '{array.name}' array that are in the '{direction.name}' direction.
  type {array_name}_{direction.name}_t is record
"""

            vhdl_array_init = []
            for register in self.iterate_fabric_accessible_array_registers(
                register_array=array, direction=direction
            ):
                vhdl += self._record_member_declaration_for_register(
                    register=register, register_array=array
                )

                register_name = self.register_name(register=register, register_array=array)
                init = f"{register_name}_init" if register.fields else "(others => '0')"
                vhdl_array_init.append(f"{register.name} => {init}")

            init = "    " + ",\n    ".join(vhdl_array_init)
            vhdl += f"""\
  end record;
  -- Default value of the above record.
  constant {array_name}_{direction.name}_init : {array_name}_{direction.name}_t := (
{init}
  );
  -- VHDL array of the above record, ranged per the length of the '{array.name}' \
register array.
  type {array_name}_{direction.name}_vec_t is array (0 to {array.length - 1}) of \
{array_name}_{direction.name}_t;

"""

        heading = f"""\
  -- -----------------------------------------------------------------------------
  -- Below is a record with correctly typed and ranged members for all registers, register arrays
  -- and fields that are in the '{direction.name}' direction.
"""
        if vhdl:
            heading += f"""\
  -- But first, records for the registers of each register array the are in \
the '{direction.name}' direction.
"""

        return f"{heading}{vhdl}"

    def _get_register_record(self, direction):
        """
        Get the record that contains all registers and arrays in the specified direction.
        Also default value constant for this record.

        This function assumes that the register map has registers in the given direction.
        """
        record_init = []
        vhdl = f"""\
  -- Record with everything in the '{direction.name}' direction.
  type {self.name}_regs_{direction.name}_t is record
"""

        for array in self.iterate_bus_accessible_register_arrays(direction=direction):
            array_name = self.register_array_name(register_array=array)

            vhdl += f"    {array.name} : {array_name}_{direction.name}_vec_t;\n"
            record_init.append(f"{array.name} => (others => {array_name}_{direction.name}_init)")

        for register in self.iterate_bus_accessible_plain_registers(direction=direction):
            vhdl += self._record_member_declaration_for_register(register=register)

            if register.fields:
                register_name = self.register_name(register=register)
                record_init.append(f"{register.name} => {register_name}_init")
            else:
                record_init.append(f"{register.name} => (others => '0')")

        init = "    " + ",\n    ".join(record_init)

        return f"""\
{vhdl}
  end record;
  -- Default value of the above record.
  constant {self.name}_regs_{direction.name}_init : \
{self.name}_regs_{direction.name}_t := (
{init}
  );
"""

    def _record_member_declaration_for_register(self, register, register_array=None):
        """
        Get the record member declaration line for a register that shall be part of the record.
        """
        register_name = self.register_name(register=register, register_array=register_array)

        if register.fields:
            return f"    {register.name} : {register_name}_t;\n"

        return f"    {register.name} : reg_t;\n"

    def _register_was_accessed(self):
        """
        Get record for 'reg_was_read' and 'reg_was_written' ports.
        Should include only the registers that are actually readable/writeable.
        """
        vhdl = ""

        for direction in BUS_ACCESS_DIRECTIONS.values():
            if self.has_any_bus_accessible_register(direction=direction):
                vhdl += self._register_was_accessed_record(direction=direction)

        return vhdl

    def _register_was_accessed_record(self, direction):
        """
        Get the record for 'reg_was_read' or 'reg_was_written'.
        """
        vhdl = f"""\
  -- ---------------------------------------------------------------------------
  -- Below is a record with a status bit for each {direction.name_adjective} register in the \
register map.
  -- It can be used for the 'reg_was_{direction.name_past}' port of a register file wrapper.
"""

        for array in self.iterate_bus_accessible_register_arrays(direction=direction):
            array_name = self.register_array_name(register_array=array)
            vhdl += f"""\
  -- One status bit for each {direction.name_adjective} register in the '{array.name}' \
register array.
  type {array_name}_was_{direction.name_past}_t is record
"""

            for register in self.iterate_bus_accessible_array_registers(
                register_array=array, direction=direction
            ):
                vhdl += f"    {register.name} : std_ulogic;\n"

            vhdl += f"""\
  end record;
  -- Default value of the above record.
  constant {array_name}_was_{direction.name_past}_init : {array_name}_was_{direction.name_past}_t \
:= (others => '0');
  -- Vector of the above record, ranged per the length of the '{array.name}' \
register array.
  type {array_name}_was_{direction.name_past}_vec_t is array (0 to {array.length - 1}) \
of {array_name}_was_{direction.name_past}_t;

"""

        vhdl += f"""\
  -- Combined status mask record for all {direction.name_adjective} register.
  type {self.name}_reg_was_{direction.name_past}_t is record
"""

        array_init = []
        for array in self.iterate_bus_accessible_register_arrays(direction=direction):
            array_name = self.register_array_name(register_array=array)

            vhdl += f"    {array.name} : {array_name}_was_{direction.name_past}_vec_t;\n"
            array_init.append(
                f"{array.name} => (others => {array_name}_was_{direction.name_past}_init)"
            )

        has_at_least_one_register = False
        for register in self.iterate_bus_accessible_plain_registers(direction=direction):
            vhdl += f"    {register.name} : std_ulogic;\n"
            has_at_least_one_register = True

        init_arrays = ("    " + ",\n    ".join(array_init)) if array_init else ""
        init_registers = "    others => '0'" if has_at_least_one_register else ""
        separator = ",\n" if (init_arrays and init_registers) else ""

        vhdl += f"""\
  end record;
  -- Default value for the above record.
  constant {self.name}_reg_was_{direction.name_past}_init : \
{self.name}_reg_was_{direction.name_past}_t := (
{init_arrays}{separator}{init_registers}
  );
  -- Convert an SLV 'reg_was_{direction.name_past}' from generic register file to the record above.
  function to_{self.name}_reg_was_{direction.name_past}(
    data : {self.name}_reg_was_accessed_t
  ) return {self.name}_reg_was_{direction.name_past}_t;

"""

        return vhdl

    def _array_index_function_implementations(self):
        """
        Implementation for the functions that return a register index for the specified index in a
        register array.
        """
        vhdl = ""
        for register_array in self.iterate_register_arrays():
            num_registers = len(register_array.registers)
            for register in register_array.registers:
                vhdl += f"""\
{self._array_register_index_function_signature(register, register_array)} is
  begin
    return {register_array.base_index} + array_index * {num_registers} + {register.index};
  end function;

"""

        return vhdl

    def _register_map_body(self):
        """
        Get the body of the register map definition constants.
        """
        map_name = f"{self.name}_reg_map"
        range_name = f"{self.name}_reg_range"

        register_definitions = []
        default_values = []
        vhdl_array_index = 0
        for register_object in self.iterate_register_objects():
            if isinstance(register_object, Register):
                idx = self.register_name(register_object)
                opening = f"{vhdl_array_index} => "

                register_definitions.append(
                    f"{opening}(idx => {idx}, reg_type => {register_object.mode})"
                )
                default_values.append(f'{opening}"{register_object.default_value:032b}"')

                vhdl_array_index = vhdl_array_index + 1

            else:
                for array_index in range(register_object.length):
                    for register in register_object.registers:
                        idx = f"{self.register_name(register, register_object)}({array_index})"
                        opening = f"{vhdl_array_index} => "

                        register_definitions.append(
                            f"{opening}(idx => {idx}, reg_type => {register.mode})"
                        )
                        default_values.append(f'{opening}"{register.default_value:032b}"')

                        vhdl_array_index = vhdl_array_index + 1

        array_element_separator = ",\n    "
        vhdl = f"""\
  constant {map_name} : reg_definition_vec_t({range_name}) := (
    {array_element_separator.join(register_definitions)}
  );

  constant {self.name}_regs_init : {self.name}_regs_t := (
    {array_element_separator.join(default_values)}
  );

"""

        return vhdl

    def _field_conversion_implementations(self):
        """
        Implementation of functions that convert a register field's native VHDL representation
        to/from SLV.
        """
        vhdl = ""

        for register, register_array in self.iterate_registers():
            for field in register.fields:
                if isinstance(field, (Bit, BitVector)):
                    # Skip all field types that do not have any functions that need to
                    # be implemented.
                    continue

                name = self.field_name(
                    register=register, register_array=register_array, field=field
                )
                to_slv_name = self._field_to_slv_function_name(field=field, field_name=name)

                if isinstance(field, Enumeration):
                    to_slv = f"""\
    constant data_int : natural := {name}_t'pos(data);
    constant result : {name}_slv_t := std_ulogic_vector(
      to_unsigned(data_int, {name}_width)
    );
"""
                    from_slv = f"""\
    constant field_slv : {name}_slv_t := data({name});
    constant field_int : natural := to_integer(unsigned(field_slv));
    constant result : {name}_t := {name}_t'val(field_int);
"""
                elif isinstance(field, Integer):
                    vector_type = "signed" if field.is_signed else "unsigned"
                    to_slv = f"""\
    constant result : {name}_slv_t := std_ulogic_vector(to_{vector_type}(data, {name}_width));
"""
                    from_slv = f"""\
    constant result : integer := to_integer({vector_type}(data({name})));
"""
                else:
                    raise TypeError(f'Got unexpected field type: "{field}".')

                vhdl += f"""\
  function {to_slv_name}(data : {name}_t) return {name}_slv_t is
{to_slv}\
  begin
    return result;
  end function;

  function to_{name}(data : reg_t) return {name}_t is
{from_slv}\
  begin
    return result;
  end function;

"""

        return vhdl

    def _register_field_record_conversion_implementations(self):
        """
        Implementation of functions that convert a register record with native field types
        to/from SLV.
        """
        vhdl = ""

        def _get_functions(register, register_array=None):
            register_name = self.register_name(register=register, register_array=register_array)

            to_slv = ""
            to_record = ""

            for field in register.fields:
                field_name = self.field_name(
                    register=register, register_array=register_array, field=field
                )

                if isinstance(field, Bit):
                    to_slv += f"    result({field_name}) := data.{field.name};\n"
                    to_record += f"    result.{field.name} := data({field_name});\n"

                elif isinstance(field, BitVector):
                    to_slv += f"    result({field_name}) := std_logic_vector(data.{field.name});\n"
                    to_record += f"    result.{field.name} := {field_name}_t(data({field_name}));\n"

                elif isinstance(field, (Enumeration, Integer)):
                    to_slv_function_name = self._field_to_slv_function_name(
                        field=field, field_name=field_name
                    )
                    to_slv += (
                        f"    result({field_name}) := {to_slv_function_name}(data.{field.name});\n"
                    )

                    to_record += f"    result.{field.name} := to_{field_name}(data);\n"

                else:
                    raise TypeError(f'Got unexpected field type: "{field}".')

            return f"""\
  function to_slv(data : {register_name}_t) return reg_t is
    variable result : reg_t := (others => '0');
  begin
{to_slv}
    return result;
  end function;

  function to_{register_name}(data : reg_t) return {register_name}_t is
    variable result : {register_name}_t := {register_name}_init;
  begin
{to_record}
    return result;
  end function;

"""

        for register, register_array in self.iterate_registers():
            if register.fields:
                vhdl += _get_functions(register=register, register_array=register_array)

        return vhdl

    def _register_record_conversion_implementations(self):
        """
        Conversion function implementations to/from SLV for the records containing all
        registers and arrays in 'up'/'down' direction.
        """
        vhdl = ""

        if self.has_any_fabric_accessible_register(direction=FABRIC_ACCESS_DIRECTIONS["up"]):
            vhdl += self._register_record_up_to_slv()

        if self.has_any_fabric_accessible_register(direction=FABRIC_ACCESS_DIRECTIONS["down"]):
            vhdl += self._get_registers_down_to_record_function()

        return vhdl

    def _register_record_up_to_slv(self):
        """
        Conversion function implementation for converting a record of all the 'up' registers
        to a register SLV list.

        This function assumes that the register map has registers in the given direction.
        """
        to_slv = ""

        for register, register_array in self.iterate_fabric_accessible_registers(
            direction=FABRIC_ACCESS_DIRECTIONS["up"]
        ):
            register_name = self.register_name(register=register, register_array=register_array)

            if register_array is None:
                result = f"    result({register_name})"
                record = f"data.{register.name}"

                if register.fields:
                    to_slv += f"{result} := to_slv({record});\n"
                else:
                    to_slv += f"{result} := {record};\n"

            else:
                for array_idx in range(register_array.length):
                    result = f"    result({register_name}({array_idx}))"
                    record = f"data.{register_array.name}({array_idx}).{register.name}"

                    if register.fields:
                        to_slv += f"{result} := to_slv({record});\n"
                    else:
                        to_slv += f"{result} := {record};\n"

        return f"""\
  function to_slv(data : {self.name}_regs_up_t) return {self.name}_regs_t is
    variable result : {self.name}_regs_t := {self.name}_regs_init;
  begin
{to_slv}
    return result;
  end function;

"""

    def _get_registers_down_to_record_function(self):
        """
        Conversion function implementation for converting all the 'down' registers
        in a register SLV list to record.

        This function assumes that the register map has registers in the given direction.
        """
        to_record = ""

        for register, register_array in self.iterate_fabric_accessible_registers(
            direction=FABRIC_ACCESS_DIRECTIONS["down"]
        ):
            register_name = self.register_name(register=register, register_array=register_array)

            if register_array is None:
                result = f"    result.{register.name}"
                data = f"data({register_name})"

                if register.fields:
                    to_record += f"{result} := to_{register_name}({data});\n"
                else:
                    to_record += f"{result} := {data};\n"

            else:
                for array_idx in range(register_array.length):
                    result = f"    result.{register_array.name}({array_idx}).{register.name}"
                    data = f"data({register_name}({array_idx}))"

                    if register.fields:
                        to_record += f"{result} := to_{register_name}({data});\n"
                    else:
                        to_record += f"{result} := {data};\n"

        return f"""\
  function to_{self.name}_regs_down(data : {self.name}_regs_t) return \
{self.name}_regs_down_t is
    variable result : {self.name}_regs_down_t := {self.name}_regs_down_init;
  begin
{to_record}
    return result;
  end function;

"""

    def _register_was_accessed_conversion_implementations(self):
        """
        Get conversion functions from SLV 'reg_was_read'/'reg_was_written' to record types.
        """
        vhdl = ""

        for direction in BUS_ACCESS_DIRECTIONS.values():
            if self.has_any_bus_accessible_register(direction=direction):
                vhdl += self._register_was_accessed_conversion_implementation(direction=direction)

        return vhdl

    def _register_was_accessed_conversion_implementation(self, direction):
        """
        Get a conversion function  from SLV 'reg_was_read'/'reg_was_written' to record type.
        """
        vhdl = f"""\
  function to_{self.name}_reg_was_{direction.name_past}(
    data : {self.name}_reg_was_accessed_t
  ) return {self.name}_reg_was_{direction.name_past}_t is
    variable result : {self.name}_reg_was_{direction.name_past}_t := \
{self.name}_reg_was_{direction.name_past}_init;
  begin
"""

        for register in self.iterate_bus_accessible_plain_registers(direction=direction):
            register_name = self.register_name(register=register)
            vhdl += f"    result.{register.name} := data({register_name});\n"

        for array in self.iterate_register_arrays():
            for register in self.iterate_bus_accessible_array_registers(
                register_array=array, direction=direction
            ):
                register_name = self.register_name(register=register, register_array=array)

                for array_index in range(array.length):
                    vhdl += (
                        f"    result.{array.name}({array_index}).{register.name} := "
                        f"data({register_name}(array_index=>{array_index}));\n"
                    )

        return f"""\
{vhdl}
    return result;
  end function;

"""

    def get_code(self, **kwargs):
        """
        Get a complete VHDL package with register and constant information.

        Arguments:
            register_objects: Registers and register arrays to be included.
            constants: Constants to be included.

        Returns:
            str: VHDL code.
        """
        pkg_name = f"{self.name}_regs_pkg"

        vhdl = f"""\
{self.header}
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.fixed_pkg.all;

library reg_file;
use reg_file.reg_file_pkg.all;


package {pkg_name} is

"""
        if self.register_list.constants:
            vhdl += self._constants()

        if self.register_list.register_objects:
            vhdl += f"""\
{self._register_range()}\
{self._array_constants()}\
{self._register_indexes()}\
{self._register_map_head()}\
{self._field_declarations()}\
{self._register_field_records()}\
{self._register_records()}\
{self._register_was_accessed()}\
"""

        vhdl += "end package;\n"

        if self.register_list.register_objects:
            vhdl += f"""
package body {pkg_name} is

{self._array_index_function_implementations()}\
{self._register_map_body()}\
{self._field_conversion_implementations()}\
{self._register_field_record_conversion_implementations()}\
{self._register_record_conversion_implementations()}\
{self._register_was_accessed_conversion_implementations()}\
end package body;
"""

        return vhdl
