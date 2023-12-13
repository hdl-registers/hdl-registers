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
from unittest.mock import PropertyMock, patch

# Third party libraries
import pytest
from tsfpga.system_utils import create_file

# First party libraries
from hdl_registers import __version__ as hdl_registers_version
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.parser.toml import from_toml
from hdl_registers.register_list import RegisterList


class CustomGenerator(RegisterCodeGenerator):
    SHORT_DESCRIPTION = "for test"
    COMMENT_START = "#"
    __version__ = "3.0.1"

    @property
    def output_file(self):
        return self.output_folder / f"{self.name}.x"

    def get_code(self, before_header="", **kwargs) -> str:
        return f"""\
{before_header}{self.header}
Nothing else, its a stupid generator.
"""


@pytest.fixture
def generator_from_toml(tmp_path):
    def get(toml_extras=""):
        toml_data = f"""\
################################################################################
[register.data]

mode = "w"
description = "My register"

{toml_extras}
"""

        register_list = from_toml(
            name="sensor", toml_file=create_file(tmp_path / "sensor_regs.toml", toml_data)
        )

        return CustomGenerator(register_list=register_list, output_folder=tmp_path)

    return get


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_create_should_not_run_if_nothing_has_changed(generator_from_toml):
    generator = generator_from_toml()
    generator.register_list.add_constant(name="apa", value=3, description="")
    generator.create_if_needed()

    generator = generator_from_toml()
    generator.register_list.add_constant(name="apa", value=3, description="")
    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create:
        generator.create_if_needed()
        mocked_create.assert_not_called()


def test_create_should_run_if_hash_or_version_can_not_be_read(generator_from_toml):
    generator = generator_from_toml()
    generator.create_if_needed()

    # Overwrite the generated file, without a valid header
    file_path = generator.output_folder / "sensor.x"
    assert file_path.exists()
    create_file(file_path, contents="# Mumbo jumbo\n")

    generator = generator_from_toml()
    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create:
        generator.create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_run_again_if_toml_file_has_changed(generator_from_toml):
    generator = generator_from_toml()
    generator.create_if_needed()

    generator = generator_from_toml(
        """
[constant.apa]

value = 3
"""
    )
    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create:
        generator.create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_not_run_again_if_toml_file_has_only_cosmetic_change(generator_from_toml):
    generator = generator_from_toml()
    generator.create_if_needed()

    generator = generator_from_toml(
        """
################################################################################
# A comment.
"""
    )
    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create:
        generator.create_if_needed()
        mocked_create.assert_not_called()


def test_create_should_run_again_if_register_list_is_modified(generator_from_toml):
    generator = generator_from_toml()
    generator.create_if_needed()

    generator = generator_from_toml()
    generator.register_list.add_constant(name="apa", value=3, description="")
    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create:
        generator.create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_run_again_if_package_version_is_changed(generator_from_toml):
    generator = generator_from_toml()
    generator.create_if_needed()

    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create, patch(
        "hdl_registers.generator.register_code_generator.hdl_registers_version", autospec=True
    ) as _:
        generator.create_if_needed()
        mocked_create.assert_called_once()


def test_create_should_run_again_if_generator_version_is_changed(generator_from_toml):
    generator = generator_from_toml()
    generator.create_if_needed()

    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create, patch(
        f"{__name__}.CustomGenerator.__version__", new_callable=PropertyMock
    ) as mocked_generator_version:
        mocked_generator_version.return_value = "4.0.0"

        generator.create_if_needed()
        mocked_create.assert_called_once()


def test_version_header_is_detected_even_if_not_on_first_line(generator_from_toml):
    before_header = """
# #########################
# Another header
# #########################
"""
    generator = generator_from_toml()
    generator.create_if_needed(before_header=before_header)

    generator = generator_from_toml()
    with patch(f"{__name__}.CustomGenerator.create", autospec=True) as mocked_create:
        generator.create_if_needed(before_header=before_header)
        mocked_create.assert_not_called()


@patch("hdl_registers.generator.register_code_generator.git_commands_are_available", autospec=True)
@patch("hdl_registers.generator.register_code_generator.get_git_commit", autospec=True)
@patch("hdl_registers.generator.register_code_generator.svn_commands_are_available", autospec=True)
@patch(
    "hdl_registers.generator.register_code_generator.get_svn_revision_information", autospec=True
)
@patch("hdl_registers.register_list.RegisterList.object_hash", new_callable=PropertyMock)
def test_generated_source_info(
    object_hash,
    get_svn_revision_information,
    svn_commands_are_available,
    get_git_commit,
    git_commands_are_available,
):
    register_list = RegisterList(name="", source_definition_file=Path("/apa/whatever/regs.toml"))

    expected_first_line = (
        f"This file is automatically generated by hdl-registers version {hdl_registers_version}."
    )
    expected_second_line = "Code generator CustomGenerator version 3.0.1."
    object_hash.return_value = "REGISTER_SHA"

    # Test with git information
    git_commands_are_available.return_value = True
    get_git_commit.return_value = "GIT_SHA"

    got = CustomGenerator(register_list=register_list, output_folder=None).generated_source_info

    assert got[0] == expected_first_line
    assert got[1] == expected_second_line
    assert " from file regs.toml at commit GIT_SHA." in got[2]
    assert got[3] == "Register hash REGISTER_SHA."

    # Test with SVN information
    git_commands_are_available.return_value = False
    svn_commands_are_available.return_value = True
    get_svn_revision_information.return_value = "REVISION"

    got = CustomGenerator(register_list=register_list, output_folder=None).generated_source_info
    assert got[0] == expected_first_line
    assert got[1] == expected_second_line
    assert " from file regs.toml at revision REVISION." in got[2]
    assert got[3] == "Register hash REGISTER_SHA."

    # Test with no source definition file
    register_list.source_definition_file = None

    got = CustomGenerator(register_list=register_list, output_folder=None).generated_source_info
    assert got[0] == expected_first_line
    assert got[1] == expected_second_line
    assert "from file" not in got[2]
    assert " at revision REVISION." in got[2]
    assert got[3] == "Register hash REGISTER_SHA."


def test_constant_with_reserved_name_should_raise_exception(generator_from_toml):
    generator = generator_from_toml(
        """
[constant.for]
value = 3
"""
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert str(exception_info.value) == 'Error for constant "for": Name is a reserved keyword.'


def test_plain_register_with_reserved_name_should_raise_exception(generator_from_toml):
    generator = generator_from_toml(
        """
[register.for]
mode = "r_w"
"""
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert str(exception_info.value) == 'Error for register "for": Name is a reserved keyword.'


def test_plain_register_field_with_reserved_name_should_raise_exception(generator_from_toml):
    generator = generator_from_toml(
        """
[register.test]
mode = "r_w"
bit.for.description = ""
""",
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert str(exception_info.value) == 'Error for field "for": Name is a reserved keyword.'


def test_register_array_with_reserved_name_should_raise_exception(generator_from_toml):
    generator = generator_from_toml(
        """
[register_array.for]
array_length = 3
register.data.mode = "r_w"
""",
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert (
        str(exception_info.value) == 'Error for register array "for": Name is a reserved keyword.'
    )


def test_array_register_with_reserved_name_should_raise_exception(generator_from_toml):
    generator = generator_from_toml(
        """
[register_array.test]
array_length = 3
register.for.mode = "r_w"
""",
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert str(exception_info.value) == 'Error for register "for": Name is a reserved keyword.'


def test_array_register_field_with_reserved_name_should_raise_exception(generator_from_toml):
    generator = generator_from_toml(
        """
[register_array.test]
array_length = 3
register.data.mode = "r_w"
register.data.bit.for.description = ""
""",
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert str(exception_info.value) == 'Error for field "for": Name is a reserved keyword.'


def test_reserved_name_check_works_even_with_strange_case(generator_from_toml):
    generator = generator_from_toml(
        """
[register.FoR]
mode = "r_w"
"""
    )
    with pytest.raises(ValueError) as exception_info:
        generator.create_if_needed()
    assert str(exception_info.value) == 'Error for register "FoR": Name is a reserved keyword.'
