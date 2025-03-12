# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

import pytest
from tsfpga.system_utils import create_file, read_file

from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.field.numerical_interpretation import (
    Signed,
    SignedFixedPoint,
    UnsignedFixedPoint,
)
from hdl_registers.generator.systemverilog.axi_lite.register_file import (
    SystemVerilogAxiLiteGenerator,
)
from hdl_registers.register_list import RegisterList
from hdl_registers.register_modes import REGISTER_MODES


def get_basic_register_list(path=None):
    source_definition_file = None if path is None else path
    register_list = RegisterList(name="caesar", source_definition_file=source_definition_file)

    register = register_list.append_register(name="reg0", mode=REGISTER_MODES["w"], description="")
    register.append_bit(name="bit0", description="", default_value="0")
    register.append_bit(name="bit1", description="", default_value="1")
    register.append_bit_vector(name="bit_vector0", description="", width=4, default_value="1101")
    register.append_bit_vector(
        name="bit_vector1",
        description="",
        width=4,
        default_value="1001",
        numerical_interpretation=Signed(bit_width=4),
    )
    register.append_bit_vector(
        name="bit_vector2",
        description="",
        width=4,
        default_value="1101",
        numerical_interpretation=UnsignedFixedPoint(1, -2),
    )
    register.append_bit_vector(
        name="bit_vector3",
        description="",
        width=4,
        default_value="1101",
        numerical_interpretation=SignedFixedPoint(2, -1),
    )
    register.append_integer(
        name="int0", min_value=3, max_value=16383, default_value=16377, description=""
    )

    register = register_list.append_register(name="reg1", mode=REGISTER_MODES["r"], description="")
    register.append_enumeration(
        name="enum0",
        description="",
        elements={"element0": "", "element1": "", "element2": "", "element3": "", "element4": ""},
        default_value="element1",
    )
    register.append_bit_vector(name="bit_vector4", description="", width=1, default_value="0")
    register.append_bit(name="bit2", description="", default_value="1")

    register = register_list.append_register(
        name="reg2", mode=REGISTER_MODES["r_w"], description=""
    )
    register.append_bit_vector(name="bit_vector5", description="", width=6, default_value="010101")
    register.append_enumeration(
        name="enum1", description="", elements={"element5": ""}, default_value="element5"
    )

    return register_list


def test_basic_register_list(tmp_path):
    generator = SystemVerilogAxiLiteGenerator(
        register_list=get_basic_register_list(), output_folder=tmp_path
    )
    generator.create()

    for generated_file in generator.output_files:
        print(generated_file)


def test_create_if_needed(tmp_path):
    generator = SystemVerilogAxiLiteGenerator(
        register_list=get_basic_register_list(), output_folder=tmp_path
    )

    def create(expect_create: bool = True):
        created, _ = generator.create_if_needed()
        assert created == expect_create

    create()
    create(expect_create=False)

    sv = read_file(generator.output_file)
    create_file(generator.output_file, sv.replace("hdl-registers version ", "AAAAAAA"))
    create()
    create(expect_create=False)

    (tmp_path / "caesar_register_file_axi_lite.sv").unlink()
    create()
    create(expect_create=False)

    (tmp_path / "caesar_register_file_axi_lite_pkg.sv").unlink()
    create()
    create(expect_create=False)


def test_flatten(tmp_path):
    generator = SystemVerilogAxiLiteGenerator(
        register_list=get_basic_register_list(), output_folder=tmp_path
    )

    interface = "axi4lite_intf.slave s_axil,"
    flattened = "input wire s_axil_awvalid,"

    generator.create(flatten_axi_lite=True)
    sv = read_file(generator.output_file)

    assert interface not in sv
    assert flattened in sv

    generator.create(flatten_axi_lite=False)
    sv = read_file(generator.output_file)

    assert interface in sv
    assert flattened not in sv


def test_with_and_without_source_definition_file(tmp_path):
    """
    The name of the source definition file does not seem to appear anywhere in the
    generated SystemVerilog code.
    But we set it anyway since it's part of the API.
    In SystemRDL it is required, but in hdl-registers it is optional, so we test both cases.
    """
    SystemVerilogAxiLiteGenerator(
        register_list=get_basic_register_list(path=tmp_path), output_folder=tmp_path
    ).create()
    SystemVerilogAxiLiteGenerator(
        register_list=get_basic_register_list(), output_folder=tmp_path
    ).create()


def test_default_values_on_reset(tmp_path):
    register_list = get_basic_register_list()
    sv = read_file(
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    )

    for register in register_list.register_objects:
        for field in register.fields:
            default_value_int = (
                field.default_value.value
                if isinstance(field, Enumeration)
                else field.default_value
                if isinstance(field, Integer)
                else int(field.default_value, 2)
            )
            default_value_hex = hex(default_value_int)[2:]

            print(field)
            reset_assign = f"""
        if(rst) begin
            field_storage.{register.name}.{field.name}.value <="""

            if register.mode.software_can_write:
                assert f"{reset_assign} {field.width}'h{default_value_hex};\n" in sv
            else:
                assert reset_assign not in sv


def test_field_bit_indexes(tmp_path):
    register_list = get_basic_register_list(path=tmp_path)
    sv = read_file(
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    )

    for register in register_list.register_objects:
        for field in register.fields:
            bits = f"{field.base_index + field.width - 1}:{field.base_index}"

            if register.mode.software_can_write:
                assert (
                    f"next_c = "
                    f"(field_storage.{register.name}.{field.name}.value "
                    f"& ~decoded_wr_biten[{bits}])"
                ) in sv

            if register.mode.software_can_read:
                value_source = "field_storage" if register.mode.software_can_write else "hwif_in"
                assert (
                    f"[{bits}] = (decoded_reg_strb.{register.name} && !decoded_req_is_wr) ? "
                    f"{value_source}.{register.name}.{field.name}."
                ) in sv


def test_enumeration_naming_and_encoding(tmp_path):
    SystemVerilogAxiLiteGenerator(
        register_list=get_basic_register_list(path=tmp_path), output_folder=tmp_path
    ).create()
    sv = read_file(tmp_path / "caesar_register_file_axi_lite_pkg.sv")

    assert (
        """
    typedef enum logic [2:0] {
        caesar_reg1_enum0__element0 = 'h0,
        caesar_reg1_enum0__element1 = 'h1,
        caesar_reg1_enum0__element2 = 'h2,
        caesar_reg1_enum0__element3 = 'h3,
        caesar_reg1_enum0__element4 = 'h4
    } caesar_reg1_enum0_e;

    typedef enum logic {
        caesar_reg2_enum1__element5 = 'h0
    } caesar_reg2_enum1_e;
"""
        in sv
    )


def test_empty_register_list(tmp_path):
    register_list = RegisterList(name="empty")
    _test_empty_register_list(register_list=register_list, tmp_path=tmp_path)


def _test_empty_register_list(register_list, tmp_path, extra=""):
    with pytest.raises(ValueError) as exception_info:
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    assert str(exception_info.value) == (
        f'Error while translating "empty"{extra}: '
        "SystemVerilog generator requires at least one register."
    )


def test_error_message_with_and_without_source_definition_file(tmp_path):
    register_list = RegisterList(name="empty")
    _test_empty_register_list(register_list=register_list, tmp_path=tmp_path)

    register_list = RegisterList(name="empty", source_definition_file=tmp_path)
    _test_empty_register_list(
        register_list=register_list, tmp_path=tmp_path, extra=f" in {tmp_path}"
    )


def test_register_array(tmp_path):
    register_list = get_basic_register_list(path=tmp_path)
    register_list.append_register_array(name="a", length=2, description="").append_register(
        "b", mode=REGISTER_MODES["r"], description=""
    )

    with pytest.raises(ValueError) as exception_info:
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    assert str(exception_info.value) == (
        f'Error while translating "caesar.a" in {tmp_path}: '
        "SystemVerilog generator does not support register arrays."
    )


def test_empty_register(tmp_path):
    register_list = get_basic_register_list(path=tmp_path)
    register_list.append_register("b", mode=REGISTER_MODES["r"], description="")

    with pytest.raises(ValueError) as exception_info:
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    assert str(exception_info.value) == (
        f'Error while translating "caesar.b" in {tmp_path}: '
        "SystemVerilog generator requires at least one field per register."
    )


def test_signed_integer_field(tmp_path):
    register_list = get_basic_register_list(path=tmp_path)
    register_list.append_register("b", mode=REGISTER_MODES["r"], description="").append_integer(
        name="c", min_value=-1, max_value=1, default_value=0, description=""
    )

    with pytest.raises(ValueError) as exception_info:
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    assert str(exception_info.value) == (
        f'Error while translating "caesar.b.c" in {tmp_path}: '
        "SystemVerilog generator does not support signed integer fields."
    )


def test_constant(tmp_path):
    register_list = get_basic_register_list(path=tmp_path)
    register_list.add_constant(name="c", value=42, description="")

    with pytest.raises(ValueError) as exception_info:
        SystemVerilogAxiLiteGenerator(register_list=register_list, output_folder=tmp_path).create()
    assert str(exception_info.value) == (
        f'Error while translating "caesar" in {tmp_path}: '
        "SystemVerilog generator does not support constants."
    )


def test_register_mode_r_wpulse(tmp_path):
    def run_test(mode):
        register_list = get_basic_register_list(path=tmp_path)
        register_list.append_register(
            name="a", mode=REGISTER_MODES[mode], description=""
        ).append_bit(name="b", description="", default_value="1")

        with pytest.raises(ValueError) as exception_info:
            SystemVerilogAxiLiteGenerator(
                register_list=register_list, output_folder=tmp_path
            ).create()
        assert str(exception_info.value) == (
            f'Error while translating "caesar.a" in {tmp_path}: '
            "SystemVerilog generator does not support "
            f"register mode: RegisterMode(shorthand={mode})"
        )

    run_test("r_wpulse")
    run_test("wpulse")
