Getting started
===============

The basis of all register operations is the :class:`.RegisterList` class.
An object of this type is returned when calling :func:`.from_toml` on a TOML file with the :doc:`correct format <toml_format>`.
The :class:`.RegisterList` object makes up the register map, i.e. the registers of one module.
If you have more than one module with registers in your project then these are represented with a :class:`.RegisterList` object each.

Register code generation is then done using the class methods on this object.
For example :meth:`.create_vhdl_package`.
See the sidebar for information on how to use the different generators.


Default registers
-----------------

A lot of projects use a few default registers in standard locations that shall be present in all modules.
For example, very commonly the first register of a module is an interrupt status register and the second one is an interrupt mask.
In order to handle this, without having to duplicate names and descriptions in many places, there is a ``default_registers`` flag to the :func:`.from_toml` function.
Passing a list of :class:`.Register` objects will insert these registers first in the :class:`.RegisterList`.


Integration in tsfpga
---------------------

The tsfpga project (https://tsfpga.com, https://gitlab.com/tsfpga/tsfpga), which is a
sister project of hdl_registers, integrates register code generation in an elegant way.
If a file named ``regs_<name>.toml`` is placed in the root of a module, and ``<name>`` matches the
name of the module, it will be parsed and used as that module's register map.
In the simulation and build scripts there is then a call to :meth:`.create_vhdl_package` for
each module that has registers before each run.
This makes sure that an up-to-date register definition is always used.

This is a good example of how hdl_registers can be used in an effective way.
