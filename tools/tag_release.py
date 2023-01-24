# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to be run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import argparse
import sys
from pathlib import Path
from shutil import move

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH. pylint: disable=unused-import
import tools.tools_pythonpath  # noqa: F401

# Third party libraries
from git import Repo
from tsfpga.system_utils import create_file
from tsfpga.tools.version_number_handler import (
    UNRELEASED_EMPTY,
    VersionNumberHandler,
    commit_and_tag_release,
    make_commit,
    verify_new_version_number,
)

# First party libraries
from hdl_registers import HDL_REGISTERS_DOC, HDL_REGISTERS_PATH


def main():
    parser = argparse.ArgumentParser(description="Make release commits and tag")
    parser.add_argument(
        "release_version", nargs=1, type=str, help="release version number MAJOR.MINOR.PATCH"
    )
    release_version = parser.parse_args().release_version[0]

    repo = Repo(REPO_ROOT)
    git_tag = verify_new_version_number(
        repo=repo,
        pypi_project_name="hdl_registers",
        new_version=release_version,
        unreleased_notes_file=HDL_REGISTERS_DOC / "release_notes" / "unreleased.rst",
    )

    version_number_handler = VersionNumberHandler(
        repo=repo, version_file_path=HDL_REGISTERS_PATH / "__init__.py"
    )
    version_number_handler.update(new_version=release_version)

    move_release_notes(repo=repo, version=release_version)

    commit_and_tag_release(repo=repo, version=release_version, git_tag=git_tag)

    version_number_handler.bump_to_prelease()
    make_commit(repo=repo, commit_message="Set pre-release version number")


def move_release_notes(repo, version):
    unreleased_rst = HDL_REGISTERS_DOC / "release_notes" / "unreleased.rst"
    version_rst = HDL_REGISTERS_DOC / "release_notes" / f"{version}.rst"

    if version_rst.exists():
        raise RuntimeError(f"Release notes already exist: {version_rst}")

    move(unreleased_rst, version_rst)

    # Create a new, empty, unreleased notes file
    create_file(unreleased_rst, UNRELEASED_EMPTY)

    # Add files so that the changes get included in the commit
    repo.index.add(str(unreleased_rst.resolve()))
    repo.index.add(str(version_rst.resolve()))


if __name__ == "__main__":
    main()
