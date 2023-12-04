# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH. pylint: disable=unused-import
import tools.tools_pythonpath  # noqa: F401

# Third party libraries
from pybadges import badge
from tsfpga.system_utils import create_directory, create_file, delete

# First party libraries
from hdl_registers import (
    HDL_REGISTERS_DOC,
    HDL_REGISTERS_GENERATED,
    HDL_REGISTERS_GENERATED_SPHINX_HTML,
)

BADGE_COLOR_LEFT = "#32383f"
BADGE_COLOR_RIGHT = "#2db84d"


def main() -> None:
    logos_path = HDL_REGISTERS_DOC / "logos" / "third_party"
    badges_path = create_directory(HDL_REGISTERS_GENERATED_SPHINX_HTML / "badges")

    build_information_badges(logos_path=logos_path, output_path=badges_path)
    build_python_coverage_badge(logos_path=logos_path, output_path=badges_path)
    copy_python_coverage_to_html_output()


def build_information_badges(logos_path: Path, output_path: Path) -> None:
    badge_svg = badge(
        left_text="pip install",
        right_text="hdl-registers",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(logos_path / "python.svg"),
        embed_logo=True,
    )
    create_file(output_path / "pip_install.svg", badge_svg)

    badge_svg = badge(
        left_text="license",
        right_text="BSD 3-Clause",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(logos_path / "law.svg"),
        embed_logo=True,
    )
    create_file(output_path / "license.svg", badge_svg)

    badge_svg = badge(
        left_text="github",
        right_text="hdl-registers/hdl-registers",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(logos_path / "github.svg"),
        embed_logo=True,
    )
    create_file(output_path / "repository.svg", badge_svg)

    badge_svg = badge(
        left_text="website",
        right_text="hdl-registers.com",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(logos_path / "firefox.svg"),
        embed_logo=True,
    )
    create_file(output_path / "website.svg", badge_svg)

    badge_svg = badge(
        left_text="chat",
        right_text="GitHub Discussions",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(logos_path / "discussions.svg"),
        embed_logo=True,
    )
    create_file(output_path / "chat.svg", badge_svg)


def build_python_coverage_badge(logos_path: Path, output_path: Path) -> None:
    coverage_xml = HDL_REGISTERS_GENERATED / "python_coverage.xml"
    assert coverage_xml.exists(), "Run pytest with coverage before building badge"

    xml_root = ElementTree.parse(coverage_xml).getroot()
    line_coverage = int(round(float(xml_root.attrib["line-rate"]) * 100))
    assert line_coverage > 50, f"Coverage is way low: {line_coverage}. Something is wrong."
    color = BADGE_COLOR_RIGHT if line_coverage > 80 else "red"

    badge_svg = badge(
        left_text="line coverage",
        right_text=f"{line_coverage}%",
        left_color=BADGE_COLOR_LEFT,
        right_color=color,
        logo=str(logos_path / "python.svg"),
        embed_logo=True,
    )
    create_file(output_path / "python_coverage.svg", badge_svg)


def copy_python_coverage_to_html_output() -> None:
    html_output_path = HDL_REGISTERS_GENERATED_SPHINX_HTML / "python_coverage_html"
    delete(html_output_path)

    coverage_html = HDL_REGISTERS_GENERATED / "python_coverage_html"
    assert (coverage_html / "index.html").exists(), "Run pytest with coverage before"

    shutil.copytree(coverage_html, html_output_path)


if __name__ == "__main__":
    main()
