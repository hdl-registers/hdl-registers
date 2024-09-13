# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import sys
from os.path import relpath
from pathlib import Path

# Third party libraries
from setuptools import find_packages, setup

# Do PYTHONPATH insert() instead of append() to prefer any local repo checkout over any pip install.
REPO_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

# First party libraries
import hdl_registers
from hdl_registers.about import REPOSITORY_URL, WEBSITE_URL, get_readme_rst, get_short_slogan

# Duplicated from tsfpga/__init__.py since setup.py may not depend on tsfpga
DEFAULT_FILE_ENCODING = "utf-8"

REQUIREMENTS_TXT = hdl_registers.HDL_REGISTERS_PATH / "requirements.txt"
REQUIREMENTS_DEVELOP_TXT = hdl_registers.HDL_REGISTERS_PATH / "requirements_develop.txt"
PY_TYPED = hdl_registers.HDL_REGISTERS_PATH / "py.typed"


def main():
    """
    Be extremely careful when making changes to this setup script.
    It is hard to see what is actually included and what is missing.
    Also the package data, and where it gets placed in the release tree, is very messy.

    When making changes it is recommended to try the release locally before committing to main.
    To test in a docker image do, e.g:

    python3 -m build
    docker run --rm --interactive --tty --volume $(pwd)/dist:/dist:ro --workdir /dist \
        python:3.11-slim-buster /bin/bash
    python -m pip install hdl_registers-*.tar.gz

    The install should pass and you should be able to run python and "import hdl_registers".
    You should see all the files in "/usr/local/lib/python3.11/site-packages/hdl_registers".
    Test to run "python -m pip uninstall hdl_registers" and see that it passes.
    Check the output to see that there are not package files installed in weird locations
    (such as /usr/local/lib/).

    Can also try to run simulation/build in the tsfpga and hdl-modules repositories with the newly
    created release dist installed.
    If that passes, then everything that is needed is probably included.
    """
    # Make sure the "tests" folder does not get included in the release.
    packages = find_packages(include=["hdl_registers", "hdl_registers.*"])
    for package_name in packages:
        assert package_name.startswith("hdl_registers"), package_name

    setup(
        name="hdl_registers",
        #
        version=hdl_registers.__version__,
        #
        description=get_short_slogan(),
        #
        long_description=get_readme_rst(include_extra_for_pypi=True),
        long_description_content_type="text/x-rst",
        #
        author="Lukas Vik",
        author_email="10241915+LukasVik@users.noreply.github.com",
        #
        packages=packages,
        package_data={"hdl_registers": get_package_data()},
        #
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: BSD License",
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: OS Independent",
            "Operating System :: POSIX :: Linux",
            "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
            "Topic :: Scientific/Engineering",
            "Topic :: Software Development :: Testing",
            "Topic :: Software Development",
        ],
        #
        license="BSD 3-Clause License",
        #
        # Same as on GitHub
        keywords=[
            "python",
            "c",
            "html",
            "asic",
            "generator",
            "fpga",
            "cplusplus",
            "register",
            "vhdl",
            "eda",
            "rtl",
            "csr",
            "axi",
            "axi-lite",
            "register-interface",
        ],
        #
        install_requires=read_requirements_file(REQUIREMENTS_TXT),
        extras_require=dict(develop=read_requirements_file(REQUIREMENTS_DEVELOP_TXT)),
        #
        python_requires=">=3.9",
        #
        project_urls={
            "Homepage": WEBSITE_URL,
            "Documentation": WEBSITE_URL,
            "Changelog": f"{WEBSITE_URL}/rst/about/release_notes.html",
            "Source": REPOSITORY_URL,
            "Issues": f"{REPOSITORY_URL}/issues",
        },
    )


def read_requirements_file(path):
    requirements = []
    with open(path, encoding=DEFAULT_FILE_ENCODING) as file_handle:
        # Requirements file contains one package name per line
        for line_data in file_handle.readlines():
            if line_data:
                requirements.append(line_data.strip())

    return requirements


def get_package_data():
    """
    Get all files that shall be include with the release, apart from the package python files
    that are already there.
    """
    files = [REQUIREMENTS_TXT, REQUIREMENTS_DEVELOP_TXT, PY_TYPED]

    # Specify path relative to the python package folder
    package_data = [
        str(path_relative_to(file_path, hdl_registers.HDL_REGISTERS_PATH)) for file_path in files
    ]

    return package_data


# Duplicated system_utils.py since setup.py can not depend on tsfpga
def path_relative_to(path, other):
    """
    Note Path.relative_to() does not support the use case where e.g. readme.md should get
    relative path "../readme.md". Hence we have to use os.path.
    """
    assert path.exists(), path
    return Path(relpath(str(path), str(other)))


if __name__ == "__main__":
    main()
