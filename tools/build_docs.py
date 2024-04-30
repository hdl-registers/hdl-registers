# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import argparse
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
from tsfpga.system_utils import create_directory, create_file, delete, read_file, run_command
from tsfpga.tools.sphinx_doc import build_sphinx, generate_release_notes

# First party libraries
import hdl_registers
from hdl_registers.about import WEBSITE_URL, get_readme_rst, get_short_slogan

GENERATED_SPHINX = hdl_registers.HDL_REGISTERS_GENERATED / "sphinx_rst"
GENERATED_SPHINX_HTML = hdl_registers.HDL_REGISTERS_GENERATED / "sphinx_html"
SPHINX_DOC = hdl_registers.HDL_REGISTERS_DOC / "sphinx"

BADGE_COLOR_LEFT = "#32383f"
BADGE_COLOR_RIGHT = "#2db84d"


def main() -> None:
    args = arguments()

    logos_path = create_directory(GENERATED_SPHINX_HTML / "logos")
    shutil.copy2(hdl_registers.HDL_REGISTERS_DOC / "logos" / "banner.png", logos_path)

    badges_path = create_directory(GENERATED_SPHINX_HTML / "badges")
    build_information_badges(badges_path)

    rst = generate_release_notes(
        repo_root=hdl_registers.REPO_ROOT,
        release_notes_directory=hdl_registers.HDL_REGISTERS_DOC / "release_notes",
        project_name="hdl-registers",
    )
    create_file(GENERATED_SPHINX / "release_notes.rst", rst)

    generate_api_documentation()

    generate_bibtex()

    generate_register_code()

    generate_sphinx_index()

    build_sphinx(build_path=SPHINX_DOC, output_path=GENERATED_SPHINX_HTML)

    if args.skip_coverage:
        return

    build_python_coverage_badge(badges_path)
    copy_python_coverage_to_html_output()


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Build sphinx documentation", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--skip-coverage",
        action="store_true",
        help="skip handling of all coverage reports",
    )
    return parser.parse_args()


def generate_api_documentation() -> None:
    output_path = delete(GENERATED_SPHINX / "apidoc")

    cmd = [
        sys.executable,
        "-m",
        "sphinx.ext.apidoc",
        # Place module documentation before submodule documentation
        "--module-first",
        "--output-dir",
        str(output_path),
        # module path
        "hdl_registers",
        # exclude pattern
        "**/test/**",
    ]
    run_command(cmd=cmd, cwd=hdl_registers.REPO_ROOT)


def generate_register_code() -> None:
    # Set the path environment variable in the python calls below so they find e.g. tsfpga.
    env = dict(PYTHONPATH=":".join(sys.path))

    for folder in (SPHINX_DOC / "rst").glob("*"):
        for py_file in (folder / "py").glob("*.py"):
            output_folder = GENERATED_SPHINX / "register_code" / folder.name / py_file.stem

            command = [sys.executable, str(py_file), str(output_folder)]
            status = run_command(
                cmd=command, cwd=hdl_registers.REPO_ROOT, env=env, capture_output=True
            )

            print(status.stdout)
            create_file(file=output_folder / "stdout.txt", contents=status.stdout)

            if status.stderr:
                print(status.stderr)


def generate_bibtex() -> None:
    """
    Generate a BibTeX snippet for citing this project.

    Since BibTeX also uses curly braces, f-string formatting is hard here.
    Hence the string is split up.
    """
    rst_before = """\
.. code-block:: tex

  @misc{hdl-registers,
    author = {Vik, Lukas},
    title  = {{hdl-registers: """

    rst_after = f"""}}}},
    url    = {{{WEBSITE_URL}}},
  }}
"""

    rst = f"{rst_before}{get_short_slogan()}{rst_after}"

    create_file(GENERATED_SPHINX / "bibtex.rst", rst)


def generate_sphinx_index() -> None:
    """
    Generate index.rst for sphinx. Also verify that readme.rst in the project is identical.

    Rst file inclusion in readme.rst does not work on GitHub unfortunately, hence this
    cumbersome handling of syncing documentation.
    """
    rst_to_verify = get_readme_rst(include_extra_for_github=True)
    if read_file(hdl_registers.REPO_ROOT / "readme.rst") != rst_to_verify:
        file_path = create_file(
            hdl_registers.HDL_REGISTERS_GENERATED / "sphinx" / "readme.txt", rst_to_verify
        )
        raise ValueError(
            f"readme.rst in repo root not correct. Compare to reference in python: {file_path}"
        )

    result = get_readme_rst(include_extra_for_website=True)
    create_file(GENERATED_SPHINX / "index.rst", result)


def build_information_badges(output_path: Path) -> None:
    badge_svg = badge(
        left_text="pip install",
        right_text="hdl-registers",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(hdl_registers.HDL_REGISTERS_DOC / "logos" / "third_party" / "python.svg"),
        embed_logo=True,
    )
    create_file(output_path / "pip_install.svg", badge_svg)

    badge_svg = badge(
        left_text="license",
        right_text="BSD 3-Clause",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(hdl_registers.HDL_REGISTERS_DOC / "logos" / "third_party" / "law.svg"),
        embed_logo=True,
    )
    create_file(output_path / "license.svg", badge_svg)

    badge_svg = badge(
        left_text="github",
        right_text="hdl-registers/hdl-registers",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(hdl_registers.HDL_REGISTERS_DOC / "logos" / "third_party" / "github.svg"),
        embed_logo=True,
    )
    create_file(output_path / "repository.svg", badge_svg)

    badge_svg = badge(
        left_text="website",
        right_text="hdl-registers.com",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(hdl_registers.HDL_REGISTERS_DOC / "logos" / "third_party" / "firefox.svg"),
        embed_logo=True,
    )
    create_file(output_path / "website.svg", badge_svg)

    badge_svg = badge(
        left_text="chat",
        right_text="GitHub Discussions",
        left_color=BADGE_COLOR_LEFT,
        right_color=BADGE_COLOR_RIGHT,
        logo=str(hdl_registers.HDL_REGISTERS_DOC / "logos" / "third_party" / "discussions.svg"),
        embed_logo=True,
    )
    create_file(output_path / "chat.svg", badge_svg)


def build_python_coverage_badge(output_path: Path) -> None:
    coverage_xml = hdl_registers.HDL_REGISTERS_GENERATED / "python_coverage.xml"
    assert coverage_xml.exists(), "Run pytest with coverage before building documentation"

    xml_root = ElementTree.parse(coverage_xml).getroot()
    line_coverage = int(round(float(xml_root.attrib["line-rate"]) * 100))
    assert line_coverage > 50, f"Coverage is way low: {line_coverage}. Something is wrong."
    color = BADGE_COLOR_RIGHT if line_coverage > 80 else "red"

    badge_svg = badge(
        left_text="line coverage",
        right_text=f"{line_coverage}%",
        left_color=BADGE_COLOR_LEFT,
        right_color=color,
        logo=str(hdl_registers.HDL_REGISTERS_DOC / "logos" / "third_party" / "python.svg"),
        embed_logo=True,
    )
    create_file(output_path / "python_coverage.svg", badge_svg)


def copy_python_coverage_to_html_output() -> None:
    html_output_path = GENERATED_SPHINX_HTML / "python_coverage_html"
    delete(html_output_path)

    coverage_html = hdl_registers.HDL_REGISTERS_GENERATED / "python_coverage_html"
    assert (
        coverage_html / "index.html"
    ).exists(), "Run pytest with coverage before building documentation"

    shutil.copytree(coverage_html, html_output_path)


if __name__ == "__main__":
    main()
