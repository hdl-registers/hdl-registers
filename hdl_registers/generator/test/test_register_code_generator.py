# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from unittest.mock import patch

# Third party libraries
import pytest
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.parser import from_toml


class Generator(RegisterCodeGenerator):
    SHORT_DESCRIPTION = "for test"
    COMMENT_START = "#"

    @property
    def output_file(self):
        return self.output_folder / f"{self.name}.x"

    def get_code(self, before_header="", **kwargs) -> str:
        return f"""\
{before_header}{self.header}
Nothing else, its a stupid generator.
"""


@pytest.fixture
def register_list_from_toml(tmp_path):
    def get(toml_extras=""):
        toml_data = f"""\
################################################################################
[register.data]

mode = "w"
description = "My register"

{toml_extras}
"""

        return from_toml(
            module_name="sensor", toml_file=create_file(tmp_path / "sensor_regs.toml", toml_data)
        )

    return get


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_create_should_not_run_if_nothing_has_changed(register_list_from_toml, tmp_path):
    register_list = register_list_from_toml()
    register_list.add_constant(name="apa", value=3, description="")
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()

    register_list = register_list_from_toml()
    register_list.add_constant(name="apa", value=3, description="")
    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()
        mocked_create.assert_not_called()


def test_create_should_run_if_hash_or_version_can_not_be_read(register_list_from_toml, tmp_path):
    register_list = register_list_from_toml()
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()

    # Overwrite the generated file, without a valid header
    file_path = tmp_path / "sensor.x"
    assert file_path.exists()
    create_file(file_path, contents="# Mumbo jumbo\n")

    register_list = register_list_from_toml()
    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_run_again_if_toml_file_has_changed(register_list_from_toml, tmp_path):
    register_list = register_list_from_toml()
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()

    register_list = register_list_from_toml(
        """
[constant.apa]

value = 3
"""
    )
    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_not_run_again_if_toml_file_has_only_cosmetic_change(
    register_list_from_toml, tmp_path
):
    register_list = register_list_from_toml()
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()

    register_list = register_list_from_toml(
        """
################################################################################
# A comment.
"""
    )
    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()
        mocked_create.assert_not_called()


def test_create_should_run_again_if_register_list_is_modified(register_list_from_toml, tmp_path):
    register_list = register_list_from_toml()
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()

    register_list = register_list_from_toml()
    register_list.add_constant(name="apa", value=3, description="")
    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_run_again_if_version_is_changed(register_list_from_toml, tmp_path):
    register_list = register_list_from_toml()
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()

    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create, patch(
        "hdl_registers.generator.register_code_generator.__version__", autospec=True
    ) as _:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed()
        mocked_create.assert_called_once()


def test_version_header_is_detected_even_if_not_on_first_line(register_list_from_toml, tmp_path):
    before_header = """
# #########################
# Another header
# #########################
"""
    register_list = register_list_from_toml()
    Generator(register_list=register_list, output_folder=tmp_path).create_if_needed(
        before_header=before_header
    )

    register_list = register_list_from_toml()
    with patch(f"{__name__}.Generator.create", autospec=True) as mocked_create:
        Generator(register_list=register_list, output_folder=tmp_path).create_if_needed(
            before_header=before_header
        )
        mocked_create.assert_not_called()


def test_to_pascal_case():
    assert Generator.to_pascal_case("test") == "Test"
    assert Generator.to_pascal_case("test_two") == "TestTwo"
