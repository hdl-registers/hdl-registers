Getting started
===============

.. _installation:

Installation
------------

The latest release version of hdl-registers can be installed from
`PyPI <https://pypi.org/project/hdl-registers/>`__ with the command

.. code-block:: shell

  python3 -m pip install hdl-registers

Alternatively, you can clone the `git repository <https://github.com/hdl-registers/hdl-registers>`__
if you want to use a development version.
From the repo checkout you can install the Python package by running

.. code-block:: shell

  python3 -m pip install .

in the repo root.
You can also access it in your scripts by adding the repo path to the ``PYTHONPATH`` environment
variable, or by modifying ``sys.path`` in your script.



.. _usage:

Usage
-----

A minimal usage example:

.. code-block:: python

  from pathlib import Path

  from hdl_registers.generator.vhdl.register_package import VhdlRegisterPackageGenerator
  from hdl_registers.parser.toml import from_toml


  this_dir = Path(__file__).parent

  register_list = from_toml(name="caesar", toml_file=this_dir / "caesar_registers.toml")
  VhdlRegisterPackageGenerator(register_list=register_list, output_folder=this_dir).create_if_needed()

The basis of all register operations is the :class:`.RegisterList` class, which represents a
register map, meaning, the registers of one module.
An object of this type is returned when calling :func:`.from_toml` on a TOML file with the
:ref:`correct format <toml_format>`.
To try things out you could use the register TOML data from the
:ref:`TOML format example <toml_formatting>`.

Register code generation is then done using one of the generator classes,
for example :class:`.VhdlRegisterPackageGenerator` as seen in the example above.
See the sidebar under "Code Generators" for information on what can be generated and how to
invoke it.

If you have more than one module with registers in your project then these are represented with a
:class:`.RegisterList` object each.
See :ref:`scope` for a background on this.



Integration in tsfpga
---------------------

The `tsfpga <https://tsfpga.com>`__ project, which is a sister project of hdl-registers,
integrates register code generation in an elegant way.
If a file named ``regs_<name>.toml`` is placed in the root of a module, and ``<name>`` matches the
name of the module, it will be parsed and used as that module's register map.
In the simulation and build scripts there is then a call to the
:ref:`VHDL generators <generator_vhdl>` for each register list before each run.
This makes sure that an up-to-date register definition is always used.

This is a good example of how hdl-registers can be used in an effective way.
