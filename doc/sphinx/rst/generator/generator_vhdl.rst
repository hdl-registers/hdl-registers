.. _vhdl_generator:

VHDL code generator
===================

A VHDL package can be generated with a call to :meth:`.RegisterList.create_vhdl_package`.
The VHDL package file is designed to be used with the generic AXI-Lite register file available in
the `hdl_modules <https://hdl-modules.com>`__ project: :ref:`reg_file.axi_lite_reg_file`.

Since generation of VHDL packages is usually run in real time (e.g. before running a simulation) the
speed of the tool is important.
In order the save time, :meth:`.RegisterList.create_vhdl_package` maintains a hash of the
register definitions,
and will only generate the VHDL file when necessary.


Requirements
------------

The VHDL package depends on :ref:`reg_file.reg_file_pkg` from the :ref:`reg_file <module_reg_file>`
module of `hdl_modules <https://hdl-modules.com>`__.
Can be downloaded from gitlab here:
https://gitlab.com/hdl_modules/hdl_modules/-/blob/main/modules/reg_file/src/reg_file_pkg.vhd


Example
-------

Below is the resulting code from the :ref:`TOML format example <toml_format>`.

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/vhdl/example_regs_pkg.vhd
   :caption: example_regs_pkg.vhd
   :language: vhdl
   :linenos:

For a plain register (e.g. ``configuration``) the register index is simply a natural
(``example_configuration``, where "example" is the name of the module).
For register arrays it is instead a function, e.g. ``example_base_addresses_read_address``
(where ``base_addresses`` is the name of the array and ``read_address`` is the name of
the register).

Note that there is a large eco-system of register-related components in
the `hdl_modules <https://hdl-modules.com>`__ project.
Firstly there are wrappers available for easier working with VUnit verification components.
See the :ref:`bfm library <module_bfm>` and :ref:`reg_file.reg_operations_pkg`.
Furthermore there is a large number of synthesizable AXI components available that enable the
register bus: AXI-to-AXI-Lite converter, AXI/AXI-Lite interconnect, AXI-Lite mux (splitter),
AXI-Lite clock domain crossing, etc.
See the :ref:`reg_file library <module_reg_file>` and :ref:`axi library <module_axi>` for
more details.


Unresolved types
----------------

The generated VHDL uses unresolved types
(e.g. ``std_ulogic_vector`` instead of ``std_logic_vector``) consistently.
This means that accidental multiple drivers of a signal will result in an error when simulating
or synthesizing the design.

Since e.g. ``std_logic`` is a sub-type of ``std_ulogic`` in VHDL-2008, it is no problem if
hdl_registers components are integrated in a code base that still uses the resolved types.
I.e. a ``std_logic`` signal can be assigned to a hdl_registers signal of type ``std_ulogic``,
and vice versa, without problem.
