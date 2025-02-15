What is hdl-registers?
======================

hdl-registers is a register interface code generator for FPGA/ASIC projects that is
fast, feature-rich, robust and easy to use.
Traditionally, register information is duplicated in HDL code, software code and documentation.
Furthermore, this information is usually written by hand at great discomfort to the developer.
hdl-registers aims to solve this situation, which is unacceptable in a modern
development environment.


.. _philosophy:

Philosophy
----------

The project started in late 2018.
While there have always been :ref:`other tools <similar_tools>` available, the authors had a very
clear list of requirements that was not, and is not, fulfilled by any other project.

1. Very fast.
   So that HDL code generation can be done automatically before each simulation or build,
   not as a separate step.
2. No hard-coded numbers done by hand.
   Everything should be calculated or inferred:
   Register addresses, field bit indexes, integer/enumeration widths, enumeration encodings, etc.
3. Bloat-free.
   Meaning, well-scoped and focused on the important features.
4. Clean, intuitive, well-documented and easy-to-use API.
5. Well-tested and reliable code.

All of these, but especially points 1. and 2., set this project apart
from :ref:`others <similar_tools>`.


.. _performance:

Performance
-----------

In order for unit testing and a test-driven approach to create value, the feedback loop of running
simulations has to be very quick.
Hence the HDL register code generation, which is a precursor to simulation, must also be very fast.

Consider the following scenario: You are about to run a simulation in your FPGA repository and want
to make sure that all your register definitions are up to date.
This scenario is very common, on a productive day it happens a hundred times.
The table below compares how long that would take in a medium-sized FPGA project.
It measures the time to parse and generate VHDL artifacts for 20 register lists with 16 registers
and 32 fields.


.. code-block:: none

  $ python3 tools/benchmark.py
  -------------------------------------------------------------------------------------------------------------
                        Tool | Generate time | Time relative (lower is better) |   LUT |   FF | LUT+FF relative
  ---------------------------+---------------+---------------------------------+-------+------+----------------
   hdl-registers (7.0.4-dev) |       10.4 ms |                   1x (baseline) |  1920 | 6100 |   1x (baseline)
            cheby (1.6.dev0) |       1.88  s |                            181x |  2120 | 7940 |            1.3x
             corsair (1.0.4) |       2.33  s |                            224x |  3500 | 7700 |            1.4x
             PeakRDL (1.2.3) |       6.98  s |                            672x |  7520 | 7300 |            1.8x
                rggen (0.34) |       9.68  s |                            932x | 11880 | 6880 |            2.3x
             vhdmmio (0.0.3) |       9.39  s |                            904x |  5700 | 8320 |            1.7x


Clearly, only one of these tools is fast enough to run in real time without impacting productivity.
It is also evident that a lot of resources can be lost or gained depending on what tools is used.

Disclaimer:
We have tried to be as fair as possible in this comparison, see
`the script <https://github.com/hdl-registers/hdl-registers/blob/main/tools/benchmark.py>`_
for details.
We do not mean to bash anyone.
We encourage and applaud all open-source contributions.
See :ref:`similar_tools` below for links to the other projects.
The PeakRDL tool has no official VHDL generator, so we used the SystemVerilog generator
for comparison.


.. _scope:

Scope
-----

This project handles the registers for individual modules on a register bus.

Usually an FPGA/ASIC project consists of multiple modules/IP/banks that have to be allocated base
addresses and connected on a register bus.
This task is outside the scope of this project and is left to the user.

The authors believe that the greatest benefit of a register code generator is
for the module-level information.
The top-level architecture is very often unique to every project, and it is hard to make an
automated tool that solves every situation in a clean and elegant way that actually adds value.

With this said, there are some very convenient tools in the sister project
:ref:`hdl-modules <module_register_file>` to achieve these things.


.. _similar_tools:

Similar tools
-------------

If you want a register code generator, but hdl-registers is not really right for you,
feel free to check out one of the other available tools listed below.


* **Cheby**

  Repo: https://gitlab.cern.ch/be-cem-edl/common/cheby

  Documentation: https://gitlab.cern.ch/be-cem-edl/common/cheby/-/blob/master/doc/cheby-ug.pdf

* **Corsair**

  Repo: https://github.com/esynr3z/corsair

  Documentation: https://corsair.readthedocs.io

* **PeakRDL**

  Repo: https://github.com/SystemRDL

  Documentation: https://peakrdl.readthedocs.io

  No VHDL generator available, but possible to write your own custom generator.

* **reggen**

  Repo: https://github.com/lowRISC/opentitan

  Documentation: https://opentitan.org/book/util/reggen/index.html

  No VHDL generator available.

* **regio**

  Repo: https://github.com/esnet/regio

  No VHDL generator available.

* **registerMap**

  Repo: https://gitlab.com/registerMap/registermap

  Documentation: https://registermap.readthedocs.io

  No VHDL generator available.

* **RgGen**

  Repo: https://github.com/rggen/rggen

  Documentation: https://github.com/rggen/rggen/wiki

  Written in Ruby.

* **vhdMMIO**

  Repo: https://github.com/abs-tudelft/vhdmmio

  Documentation: https://abs-tudelft.github.io/vhdmmio

* **airhdl**

  Website: https://airhdl.com

  Commercial tool, closed source.
  Web-based workflow, no possibility to run locally.
