.. _basic_feature_register_modes:

Register modes
==============

Each register, whether plain or in a :ref:`register array <basic_feature_register_array>`,
must have a specified *mode*.

The available register modes are listed in the table below.

.. include:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_modes/modes_table.rst


* The "Read", "Write" and "Read, Write" modes are well-known and self-explanatory.
* The "Write-pulse" mode is a special mode suitable for "command"-style registers.
* The "Read, Write-pulse" mode is a special mode suitable for interrupt status registers, where a
  read shall show the current status and a write shall clear interrupts.
  Suitable for usage with :ref:`reg_file.interrupt_register`.


Generated code
--------------

The chosen mode will highly affect the generated code.

For example a register of mode "Read" will only have getters in its
generated :ref:`C++ code <generator_cpp>`, whereas mode "Write" will have only setters.

The generated :ref:`VHDL package <generator_vhdl>` used with :ref:`reg_file.axi_lite_reg_file` will
implement the correct FPGA behavior for all the different modes.
It will detect illegal operations and will e.g. respond with an ``RRESP`` of ``SLVERR`` if a read
is attempted of a "Write" register.

