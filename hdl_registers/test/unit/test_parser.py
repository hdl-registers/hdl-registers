# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import unittest

# Third party libraries
import pytest
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers.constant.bit_vector_constant import UnsignedVectorConstant
from hdl_registers.constant.string_constant import StringConstant
from hdl_registers.parser import from_toml, load_toml_file
from hdl_registers.register import Register


def test_load_nonexistent_toml_file_should_raise_exception(tmp_path):
    toml_path = tmp_path / "apa.toml"
    with pytest.raises(FileNotFoundError) as exception_info:
        load_toml_file(toml_file=toml_path)
    assert str(exception_info.value) == f"Requested TOML file does not exist: {toml_path}"


def test_register_array_without_register_should_raise_exception(tmp_path):
    toml_file = create_file(
        tmp_path / "regs.toml",
        """
[register_array.dummy_array]

array_length = 2
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(module_name="", toml_file=toml_file)
    assert str(exception_info.value) == (
        f'Register array "dummy_array" in {toml_file} does not have '
        'the required "register" property.'
    )


def test_bit_vector_without_width_should_raise_exception(tmp_path):
    toml_file = create_file(
        tmp_path / "regs.toml",
        """
[register.test_reg]
mode = "w"

bit_vector.test_bit_vector.default_value = "0"
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(module_name="", toml_file=toml_file)
    assert str(exception_info.value) == (
        f'Field "test_bit_vector" in register "test_reg" in {toml_file} does not have '
        'the required "width" property.'
    )


def test_enumeration_without_elements_should_raise_exception(tmp_path):
    toml_file = create_file(
        tmp_path / "regs.toml",
        """
[register.test_reg]
mode = "w"

enumeration.test.description = ""
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(module_name="", toml_file=toml_file)
    assert str(exception_info.value) == (
        f'Field "test" in register "test_reg" in {toml_file} does not have the required '
        '"element" property.'
    )


def test_integer_without_max_value_should_raise_exception(tmp_path):
    toml_file = create_file(
        tmp_path / "regs.toml",
        """
[register.test_reg]
mode = "w"

integer.test_integer.min_value = 3
""",
    )

    with pytest.raises(ValueError) as exception_info:
        from_toml(module_name="", toml_file=toml_file)
    assert str(exception_info.value) == (
        f'Field "test_integer" in register "test_reg" in {toml_file} does not have '
        'the required "max_value" property.'
    )


def get_test_default_registers():
    registers = [
        Register("config", 0, "r_w", "Configuration register."),
    ]
    return registers


# pylint: disable=too-many-public-methods
@pytest.mark.usefixtures("fixture_tmp_path")
class TestRegisterParser(unittest.TestCase):
    tmp_path = None

    module_name = "sensor"
    toml_data = """\

################################################################################
[register.data]

mode = "w"


################################################################################
[register.status]

mode = "r_w"
description = "Status register"

[register.status.bit.bad]

description = "Bad things happen"

[register.status.bit.not_good]

description = ""
default_value = "1"

[register.status.enumeration.direction]

description = "The direction mode"
default_value = "input"

element.passthrough = ""
element.input = ""
element.output = "use in output mode"

[register.status.bit_vector.interrupts]

width = 4
description = "Many interrupts"
default_value = "0110"

[register.status.integer.count]

description = "The number of things"
min_value = -5
max_value = 15


################################################################################
[register_array.configuration]

array_length = 3
description = "A register array"

# ------------------------------------------------------------------------------
[register_array.configuration.register.input_settings]

description = "Input configuration"
mode = "r_w"

[register_array.configuration.register.input_settings.bit.enable]

description = "Enable things"
default_value = "1"

[register_array.configuration.register.input_settings.integer.number]

description = "Configure number"
max_value = 3
default_value = 1

[register_array.configuration.register.input_settings.bit.disable]

description = ""
default_value = "0"

[register_array.configuration.register.input_settings.enumeration.size]

element.small = ""
element.large = ""


# ------------------------------------------------------------------------------
[register_array.configuration.register.output_settings]

mode = "w"

[register_array.configuration.register.output_settings.bit_vector.data]

width=16
description = "Some data"
default_value="0000000000000011"


################################################################################
"""

    def setUp(self):
        self.toml_file = create_file(self.tmp_path / "sensor_regs.toml", self.toml_data)

    def create_toml_file_with_extras(self, toml_extras):
        data = self.toml_data + toml_extras
        create_file(self.toml_file, data)

    def test_order_of_registers_and_fields(self):  # pylint: disable=too-many-statements
        registers = from_toml(self.module_name, self.toml_file).register_objects

        assert registers[0].name == "data"
        assert registers[0].mode == "w"
        assert registers[0].index == 0
        assert registers[0].description == ""
        assert registers[0].default_value == 0
        assert registers[0].fields == []

        assert registers[1].name == "status"
        assert registers[1].mode == "r_w"
        assert registers[1].index == 1
        assert registers[1].description == "Status register"

        # Bit fields
        assert registers[1].fields[0].name == "bad"
        assert registers[1].fields[0].description == "Bad things happen"
        assert registers[1].fields[0].default_value == "0"

        assert registers[1].fields[1].name == "not_good"
        assert registers[1].fields[1].description == ""
        assert registers[1].fields[1].default_value == "1"
        # Bit vector fields
        assert registers[1].fields[2].name == "interrupts"
        assert registers[1].fields[2].description == "Many interrupts"
        assert registers[1].fields[2].width == 4
        assert registers[1].fields[2].default_value == "0110"

        # Enumeration fields
        assert registers[1].fields[3].name == "direction"
        assert registers[1].fields[3].description == "The direction mode"
        assert registers[1].fields[3].width == 2
        assert registers[1].fields[3].default_value.name == "input"
        assert registers[1].fields[3].elements[0].name == "passthrough"
        assert registers[1].fields[3].elements[2].name == "output"
        assert registers[1].fields[3].elements[2].description == "use in output mode"

        # Integer fields
        assert registers[1].fields[4].name == "count"
        assert registers[1].fields[4].description == "The number of things"
        assert registers[1].fields[4].width == 5
        assert registers[1].fields[4].min_value == -5
        assert registers[1].fields[4].max_value == 15
        assert registers[1].fields[4].default_value == -5

        assert registers[1].default_value == (
            # Bits
            0 * 2**0
            + 1 * 2**1
            # Bit vector
            + 6 * 2**2
            # Enum
            + 1 * 2**6
            # Integer, negative value converted to positive
            + 0b11011 * 2**8
        )

        assert registers[2].name == "configuration"
        assert registers[2].length == 3
        assert registers[2].description == "A register array"
        assert registers[2].index == 2 + 2 * 3 - 1
        assert len(registers[2].registers) == 2

        assert registers[2].registers[0].name == "input_settings"
        assert registers[2].registers[0].mode == "r_w"
        assert registers[2].registers[0].index == 0
        assert registers[2].registers[0].description == "Input configuration"
        assert registers[2].registers[0].fields[0].name == "enable"
        assert registers[2].registers[0].fields[0].description == "Enable things"
        assert registers[2].registers[0].fields[0].default_value == "1"
        assert registers[2].registers[0].fields[1].name == "disable"
        assert registers[2].registers[0].fields[1].description == ""
        assert registers[2].registers[0].fields[1].default_value == "0"
        assert registers[2].registers[0].fields[2].name == "size"
        assert registers[2].registers[0].fields[2].default_value.name == "small"
        assert registers[2].registers[0].fields[3].name == "number"
        assert registers[2].registers[0].fields[3].description == "Configure number"
        assert registers[2].registers[0].fields[3].default_value == 1
        assert registers[2].registers[0].default_value == (
            # First bit
            1 * 2**0
            # Integer
            + 1 * 2**3
        )

        assert registers[2].registers[1].name == "output_settings"
        assert registers[2].registers[1].mode == "w"
        assert registers[2].registers[1].index == 1
        assert registers[2].registers[1].description == ""
        assert registers[2].registers[1].default_value == 3
        assert registers[2].registers[1].fields[0].name == "data"
        assert registers[2].registers[1].fields[0].description == "Some data"
        assert registers[2].registers[1].fields[0].width == 16
        assert registers[2].registers[1].fields[0].default_value == "0000000000000011"

    def test_default_registers(self):
        default_registers = get_test_default_registers()
        num_default_registers = len(default_registers)
        toml_registers = from_toml(self.module_name, self.toml_file, default_registers)

        # The registers from this test are appended at the end
        assert toml_registers.get_register("data").index == num_default_registers
        assert toml_registers.get_register("status").index == num_default_registers + 1

    def test_load_dirty_toml_file_should_raise_exception(self):
        self.create_toml_file_with_extras("apa")

        with pytest.raises(ValueError) as exception_info:
            load_toml_file(self.toml_file)
        assert str(exception_info.value).startswith(
            f"Error while parsing TOML file {self.toml_file}:\nExpected '=' after a key"
        )

    def test_plain_register_with_array_length_attribute_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.apa]

mode = "r_w"
array_length = 4
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert str(exception_info.value) == (
            f'Error while parsing register "apa" in {self.toml_file}: '
            'Unknown key "array_length".'
        )

    def test_register_array_but_no_array_length_attribute_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register_array.apa]

[register_array.apa.register.hest]

mode = "r_w"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert str(exception_info.value) == (
            f'Register array "apa" in {self.toml_file} does not have '
            'the required "array_length" property.'
        )

    def test_register_in_array_with_no_mode_attribute_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register_array.apa]

array_length = 2

[register_array.apa.register.hest]

description = "nothing"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert str(exception_info.value) == (
            f'Register "hest" within array "apa" in {self.toml_file} does not have '
            'the required "mode" property.'
        )

    def test_register_with_no_mode_field_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.apa]

description = "w"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Register "apa" in {self.toml_file} does not have the required "mode" property.'
        )

    def test_two_registers_with_same_name_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.status]

mode = "w"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        expected = (
            f"Error while parsing TOML file {self.toml_file}:\n"
            "Cannot declare ('register', 'status') twice"
        )
        assert str(exception_info.value).startswith(expected)

    def test_two_bits_with_same_name_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.test_reg]

mode = "w"

[register.test_reg.bit.test_bit]

description = "Declaration 1"

[register.test_reg.bit.test_bit]

description = "Declaration 2"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)

        expected = (
            f"Error while parsing TOML file {self.toml_file}:\n"
            "Cannot declare ('register', 'test_reg', 'bit', 'test_bit') twice"
        )
        assert str(exception_info.value).startswith(expected)

    def test_overriding_default_register(self):
        self.create_toml_file_with_extras(
            """
[register.config]

description = "apa"
"""
        )
        toml_registers = from_toml(self.module_name, self.toml_file, get_test_default_registers())

        assert toml_registers.get_register("config").description == "apa"

    def test_changing_mode_of_default_register_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.config]

mode = "w"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file, get_test_default_registers())
        assert (
            str(exception_info.value)
            == f'Overloading register "config" in {self.toml_file}, one can not change "mode" '
            "from default"
        )

    def test_unknown_register_field_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.test_reg]

mode = "w"
dummy = 3
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing register "test_reg" in {self.toml_file}: Unknown key "dummy".'
        )

    def test_unknown_register_array_field_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register_array.test_array]

array_length = 2
dummy = 3

[register_array.test_array.register.hest]

mode = "r"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing register array "test_array" in {self.toml_file}: '
            'Unknown key "dummy".'
        )

    def test_unknown_register_field_in_register_array_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register_array.test_array]

array_length = 2

[register_array.test_array.register.hest]

mode = "r"
dummy = 3
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing register "hest" in array "test_array" in {self.toml_file}: '
            'Unknown key "dummy".'
        )

    def test_unknown_bit_field_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.dummy_reg]

mode = "w"

[register.dummy_reg.bit.dummy_bit]

description = "Stuff"
height = 3
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert str(exception_info.value) == (
            f'Error while parsing field "dummy_bit" in register "dummy_reg" in {self.toml_file}: '
            'Unknown key "height".'
        )

    def test_unknown_bit_vector_field_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[register.dummy_reg]

mode = "w"

[register.dummy_reg.bit_vector.dummy_bit_vector]

description = "Stuff"
width = 3
height = 4

"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing field "dummy_bit_vector" in register "dummy_reg" in '
            f'{self.toml_file}: Unknown key "height".'
        )

    def test_constants_in_toml(self):
        # Test all supported data types
        self.create_toml_file_with_extras(
            """
[constant.data_width]

value = 0xf
description = "the width"

[constant.apa]

value = 3.14

[constant.hest]

value = true

[constant.zebra]

value = "foo"

[constant.base_address_hex]

value = "0xFF01_2345"
data_type = "unsigned"

[constant.base_address_bin]

value = "0b1000_0011"
data_type = "unsigned"
"""
        )

        register_list = from_toml(self.module_name, self.toml_file)
        assert len(register_list.constants) == 6

        assert register_list.constants[0].name == "data_width"
        assert register_list.constants[0].value == 15
        assert register_list.constants[0].description == "the width"

        assert register_list.constants[1].name == "apa"
        assert register_list.constants[1].value == 3.14
        assert register_list.constants[1].description == ""

        assert register_list.constants[2].name == "hest"
        assert register_list.constants[2].value is True

        assert isinstance(register_list.constants[3], StringConstant)
        assert register_list.constants[3].name == "zebra"
        assert register_list.constants[3].value == "foo"

        assert isinstance(register_list.constants[4], UnsignedVectorConstant)
        assert register_list.constants[4].name == "base_address_hex"
        assert register_list.constants[4].value == "FF01_2345"

        assert isinstance(register_list.constants[5], UnsignedVectorConstant)
        assert register_list.constants[5].name == "base_address_bin"
        assert register_list.constants[5].value == "1000_0011"

    def test_constant_without_value_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[constant.data_width]

description = "the width"
"""
        )
        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert str(exception_info.value) == (
            f'Constant "data_width" in {self.toml_file} does not have '
            'the required "value" property.'
        )

    def test_unknown_constant_field_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[constant.data_width]

value = 0xf
default_value = 0xf
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing constant "data_width" in {self.toml_file}: '
            'Unknown key "default_value".'
        )

    def test_data_type_on_non_string_constant_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[constant.data_width]

value = 0xf
data_type = "unsigned"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing constant "data_width" in {self.toml_file}: '
            'May not set "data_type" for non-string constant.'
        )

    def test_invalid_string_constant_data_type_should_raise_exception(self):
        self.create_toml_file_with_extras(
            """
[constant.data_width]

value = "0xff"
data_type = "signed"
"""
        )

        with pytest.raises(ValueError) as exception_info:
            from_toml(self.module_name, self.toml_file)
        assert (
            str(exception_info.value)
            == f'Error while parsing constant "data_width" in {self.toml_file}: '
            'Invalid data type "signed".'
        )
