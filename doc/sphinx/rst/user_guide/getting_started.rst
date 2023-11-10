Getting started
===============

.. _installation:

Installation
------------

The latest release version of hdl_registers can be installed from
`PyPI <https://pypi.org/project/hdl-registers/>`__ with the command

.. code-block:: shell

  python3 -m pip install hdl-registers

Alternatively, you can clone the `git repository <https://gitlab.com/hdl_registers/hdl_registers>`__
if you want to use a development version.
From the repo checkout you can install the Python package by running

.. code-block:: shell

  python3 setup.py install

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
  from hdl_registers.parser import from_toml


  this_dir = Path(__file__).parent

  register_list = from_toml(module_name="caesar", toml_file=this_dir / "caesar_registers.toml")
  VhdlRegisterPackageGenerator(register_list=register_list, output_folder=this_dir).create_if_needed()

The basis of all register operations is the :class:`.RegisterList` class.
An object of this type is returned when calling :func:`.from_toml` on a TOML file with the
:ref:`correct format <toml_format>`.
The :class:`.RegisterList` object makes up the register map, i.e. the registers of one module.
If you have more than one module with registers in your project then these are represented with a
:class:`.RegisterList` object each.

Register code generation is then done using the class methods on this object.
For example :class:`.VhdlRegisterPackageGenerator` as seen above.
See the sidebar under "Code Generators" for information on what can be generated and how to
invoke it.



Integration in tsfpga
---------------------

The tsfpga project (https://tsfpga.com, https://gitlab.com/tsfpga/tsfpga), which is a
sister project of hdl_registers, integrates register code generation in an elegant way.
If a file named ``regs_<name>.toml`` is placed in the root of a module, and ``<name>`` matches the
name of the module, it will be parsed and used as that module's register map.
In the simulation and build scripts there is then a call to :class:`.VhdlRegisterPackageGenerator`
for each module that has registers before each run.
This makes sure that an up-to-date register definition is always used.

This is a good example of how hdl_registers can be used in an effective way.
