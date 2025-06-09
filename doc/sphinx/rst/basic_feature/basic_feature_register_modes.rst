.. _basic_feature_register_modes:

Register modes
==============

Each register, whether plain or in a :ref:`register array <basic_feature_register_array>`,
must have a specified access *mode*.

The different modes are defined by the class :class:`.RegisterMode`.
In the documentation of that class you will find a diagram that explains the terms used
when describing a mode.

The official register modes available in hdl-registers are defined by the ``REGISTER_MODES``
constant in :mod:`hdl_registers.register_modes`
(`GitHub <https://github.com/hdl-registers/hdl-registers/blob/main/hdl_registers/register_modes.py>`__).


Typical modes
-------------

The following register modes, which are widely used in many FPGA/ASIC designs, are avilable:

.. include:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_modes/typical_modes.rst



Special modes
-------------

Apart from the typical ones, there are also a few special modes available:

.. include:: ../../../../generated/sphinx_rst/register_code/basic_feature/basic_feature_register_modes/special_modes.rst

The "Write-pulse" mode is a suitable for "command"-style registers.

The "Read, Write-pulse" mode is suitable for interrupt status registers, where a
read shall show the current status and a write shall clear interrupts.
Suitable for usage with :ref:`register_file.interrupt_register`.

The "Write-masked" mode can be used to avoid read-modify-write operations in some
performance-critical cases.
A "mask" field will be added automatically at the correct location.


Generated code
--------------

The chosen mode will highly affect the generated code.

For example a register of mode "Read" will only have getters in its
generated :ref:`C++ code <generator_cpp>`, whereas mode "Write" will have only setters.

The generated :ref:`VHDL package and AXI-Lite register file <generator_vhdl>` will
implement the correct FPGA behavior for all the different modes.
It will detect illegal operations and will e.g. respond with an ``RRESP`` of ``SLVERR`` if a read
is attempted of a "Write" register.
