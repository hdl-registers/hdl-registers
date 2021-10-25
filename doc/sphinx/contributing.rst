Contribution guide
==================

Information on how to make contributions to the ``hdl_registers`` project.



Setting up development environment
----------------------------------

For development we have a lot more python dependencies than when simply using the package.
Install further dependencies with:

.. code-block:: shell

    python -m pip install --upgrade --requirement hdl_registers/requirements_develop.txt



.. _maintain_changelog:

Maintaining changelog
---------------------

We maintain a changelog according to the `keep a changelog <https://keepachangelog.com/>`__ format.
The unreleased changelog in ``doc/release_notes/unreleased.rst`` shall be updated continuously, not just at release.
Release note files are in the ``rst`` format, inspect older release note files to see the formatting details.



How to build documentation
--------------------------

Documentation is built using the ``tools/build_docs.py`` script.
The documentation pages have information about python unit test code coverage.
So before building documentation you must run pytest with coverage reports enabled like in CI:

.. code-block:: shell

    python -m pytest -v --cov hdl_registers --cov-report xml:generated/python_coverage.xml --cov-report html:generated/python_coverage_html hdl_registers

If want to skip handling of coverage for the documentation there is a flag available in the script, see ``build_docs.py --help``.



How to make a new release
-------------------------

Releases are made to the Python Packaging Index (PyPI) and can be installed with the python ``pip`` tool.
To make a new release follow these steps.


Test CI pipeline
________________

Before doing anything, launch a CI run from master to see that everything works as expected.
The CI environment is stable but due to things like, e.g., new pylint version it can unexpectedly break.
When the pipeline has finished and is green you can move on to the next step.


Determine new version number
____________________________

We use the `Semantic Versioning <https://semver.org/>`__ scheme.
Read the **Summary** at the top of that page and decide the new version number accordingly.


Review the release notes
________________________

Check the release notes file ``unreleased.rst``.
Fill in anything that is missing according to :ref:`Maintaining changelog <maintain_changelog>`.


Run release script
__________________

Run the script

.. code-block:: shell

    python3 tools/tag_release.py X.Y.Z

where X.Y.Z is your new version number.
The script will bump the ``hdl_registers`` version number and copy release notes to a new file.
The changes will be committed and then tagged.


Push commit and tag
___________________

.. code-block:: shell

    git push origin --tag vX.Y.Z HEAD:release_branch

Pushing a tag will create a special CI run in gitlab:

.. image:: files/ci_deploy_pipelines.png

The pipeline for the tag will run an additional job ``deploy_pypi``:

.. image:: files/ci_deploy_jobs.png

Wait until that pipeline is finished before proceeding to merge the commits.
The pipeline for the merge request might finish before the pipeline for the tag (which pushes to PyPI).
So we wait for the tag pipeline to finish before merging, to be sure that the release upload worked before adding commits to master.

The package is uploaded to https://pypi.org/project/hdl_registers/.
You can check there to make sure your new release is available.


Merge
_____

If everything went well then you can merge your release commit to master via the gitlab merge request GUI.
