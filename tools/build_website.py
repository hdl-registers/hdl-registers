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

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# Import before others since it modifies PYTHONPATH. pylint: disable=unused-import
import tools.tools_pythonpath  # noqa: F401

# Third party libraries
from tsfpga.system_utils import create_directory, create_file, delete, read_file, run_command
from tsfpga.tools.sphinx_doc import build_sphinx, generate_release_notes

# First party libraries
import hdl_registers
from hdl_registers.about import get_readme_rst, get_short_slogan

GENERATED_SPHINX = hdl_registers.HDL_REGISTERS_GENERATED / "sphinx_rst"
GENERATED_SPHINX_HTML = hdl_registers.HDL_REGISTERS_GENERATED / "sphinx_html"
SPHINX_DOC = hdl_registers.HDL_REGISTERS_DOC / "sphinx"


def main() -> None:
    logos_path = create_directory(GENERATED_SPHINX_HTML / "logos")
    shutil.copy2(hdl_registers.HDL_REGISTERS_DOC / "logos" / "banner.png", logos_path)

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
            stdout = run_command(
                cmd=command, cwd=hdl_registers.REPO_ROOT, env=env, capture_output=True
            ).stdout

            print(stdout)
            create_file(file=output_folder / "stdout.txt", contents=stdout)


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

    rst_after = """}},
    url    = {https://hdl-registers.com},
  }
"""

    rst = f"{rst_before}{get_short_slogan()}{rst_after}"

    create_file(GENERATED_SPHINX / "bibtex.rst", rst)


def generate_sphinx_index() -> None:
    """
    Generate index.rst for sphinx. Also verify that readme.rst in the project is identical.

    Rst file inclusion in readme.rst does not work on github unfortunately, hence this
    cumbersome handling of syncing documentation.
    """
    rst_to_verify = get_readme_rst(include_extra_for_github=True)
    if read_file(hdl_registers.REPO_ROOT / "readme.rst") != rst_to_verify:
        file_path = create_file(
            hdl_registers.HDL_REGISTERS_GENERATED / "sphinx" / "readme.rst", rst_to_verify
        )
        raise ValueError(
            f"readme.rst in repo root not correct. Compare to reference in python: {file_path}"
        )

    result = get_readme_rst(include_extra_for_website=True)
    create_file(GENERATED_SPHINX / "index.rst", result)


if __name__ == "__main__":
    main()
