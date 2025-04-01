.. _generator_vhdl:

VHDL generator
==============

A large ecosystem of VHDL artifacts can be generated that support both implementation
and simulation in your project.
For synthesis:

* :class:`.VhdlRegisterPackageGenerator` generates the base VHDL package with indexes,
  modes, types, and conversion functions.
* :class:`.VhdlRecordPackageGenerator` generates a package with register records
  that use native VHDL types for all fields, along with conversion functions.
* :class:`.VhdlAxiLiteWrapperGenerator` generates a VHDL entity that wraps an AXI-Lite general
  register file, and exposes register values to application using the natively typed records.

For simulation:

* :class:`.VhdlSimulationReadWritePackageGenerator` generates a package with
  procedures for reading and writing register/field values as a one-liner.
* :class:`.VhdlSimulationCheckPackageGenerator` generates a package with
  procedures for checking current register/field values against a given expected value.
* :class:`.VhdlSimulationWaitUntilPackageGenerator` generates a package with
  procedures for waiting until a readable register/field assumes a given value.


Example
-------

To illustrate the code generators and how to use the code from them in an effective way,
there is a complete VHDL entity and testbench below.
While the application (a counter that periodically sends out a pulse) is silly, the goal of the
example is to showcase as many of the features as possible and how to efficiently use them.


Register definition TOML file
_____________________________

The registers are generated from the TOML file below.
Note that there are three registers of different :ref:`modes <basic_feature_register_modes>`:
"Read, Write", "Write-pulse" and "Read".
In the registers there are a few different fields, of type :ref:`bit <field_bit>`,
:ref:`integer <field_integer>` and :ref:`enumeration <field_enumeration>`.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: example_counter/regs_counter.toml
    :caption: TOML file for example.
    :language: TOML
    :linenos:

|


Python file to generate register artifacts
__________________________________________

The Python code below is used to parse the above TOML file and generate all the VHDL code
we need for our VHDL implementation and testbench.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: py/generator_vhdl.py
    :caption: Python code that parses the example TOML file and generates the VHDL code we need.
    :language: Python
    :linenos:
    :lines: 10-

|


.. _example_counter_vhdl:

VHDL example implementation
___________________________

The VHDL below is the implementation of our example counter.
Once again, the application is a bit silly, but it does showcase a lot of interesting features.

1. The entity uses an AXI-Lite register bus and instantiates the register file produced by
   :class:`.VhdlAxiLiteWrapperGenerator`, which can be seen
   :ref:`below <example_counter_axi_lite_wrapper>`.
2. Register values up and down are record types from the package produced by
   :class:`.VhdlRecordPackageGenerator`, which can be seen
   :ref:`below <example_counter_record_package>`.
3. The ``set_status`` process shows

   a. How to access bit fields in a "Write-pulse" register and how to set bit fields in a
      "Read" register.
   b. How to set and update an integer field in a "Read" register.
   c. How to perform an action when a specific register is written on the register bus.

   Note how all the operations are performed using native VHDL types (``std_ulogic``, ``integer``).

4. The ``count`` process shows

  a. How to take different action depending on an enumeration field
     in a "Read, Write" register.
     Note that the field type is a VHDL enum with its elements
     (e.g. ``condition_clock_cycles``) exposed.

  b. How to use a numeric value from a "Read, Write" register.
     Since the field is of integer type, it can simply be added to another integer.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: example_counter/counter.vhd
    :caption: Implementation of counter example.
    :language: VHDL
    :linenos:
    :lines: 8-

|


.. _example_tb_counter:

VHDL example testbench
___________________________

The VHDL below is the testbench for our example counter implementation above.

1. The testbench uses register read/write procedures from the package produced by
   :class:`.VhdlSimulationReadWritePackageGenerator`, which can be seen
   :ref:`below <example_counter_simulation_read_write_package>`.
   For example ``write_counter_conf``.
2. The testbench uses register wait until procedures from the package produced by
   :class:`.VhdlSimulationWaitUntilPackageGenerator`, which can be seen
   :ref:`below <example_counter_simulation_wait_until_package>`.

   a. For example ``wait_until_counter_status_pulse_count_equals``, which will continuously read
      the ``status`` register until the ``pulse_count`` field is exactly equal to the
      supplied value.

3. The type of the ``value`` for each procedure is the native record type for that register.

   a. For example, ``read_counter_status`` returns a value of type ``counter_status_t`` which is
      a record that contains a bit ``enabled`` and an integer ``pulse_count``.

4. The testbench uses register field check procedures from the package produced by
   :class:`.VhdlSimulationCheckPackageGenerator`, which can be seen
   :ref:`below <example_counter_simulation_check_package>`.
   For example ``check_counter_status_enabled_equal``.

5. The testbench instantiates :ref:`bfm.axi_lite_master` which creates AXI-Lite transactions
   based on the VUnit bus master verification component interface commands created by the
   :ref:`example_counter_simulation_read_write_package`.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: example_counter/tb_counter.vhd
    :caption: Testbench for counter example.
    :language: VHDL
    :linenos:
    :lines: 10-

|


.. _example_counter_register_package:

Generated VHDL register package
_______________________________

Below is the generated register package, created from the TOML file above via the
:class:`.VhdlRegisterPackageGenerator` class.
This is used by the :ref:`example_counter_record_package` and
the :ref:`example_counter_axi_lite_wrapper`.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_vhdl/counter_regs_pkg.vhd
    :caption: Example register package.
    :language: VHDL
    :linenos:

|


.. _example_counter_record_package:

Generated VHDL record package
_____________________________

Below is the generated record package, created from the TOML file above via the
:class:`.VhdlRecordPackageGenerator` class.
This is used by the :ref:`example_counter_axi_lite_wrapper` as well as the
:ref:`example_counter_vhdl` and the :ref:`example_tb_counter`.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_vhdl/counter_register_record_pkg.vhd
    :caption: Example register record package.
    :language: VHDL
    :linenos:

|


.. _example_counter_axi_lite_wrapper:

Generated VHDL AXI-Lite register file wrapper
_____________________________________________

Below is the generated AXI-Lite register file wrapper, created from the TOML file above via the
:class:`.VhdlAxiLiteWrapperGenerator` class.
This is instantiated in the :ref:`example_counter_vhdl` to get register values of native type
without any manual casting.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_vhdl/counter_register_file_axi_lite.vhd
    :caption: Example AXI-Lite register file wrapper.
    :language: VHDL
    :linenos:

|


.. _example_counter_simulation_read_write_package:

Generated VHDL simulation read/write package
____________________________________________

Below is the generated register simulation read/write package, created from the TOML file above via
the :class:`.VhdlSimulationReadWritePackageGenerator` class.
It is used by the :ref:`example_tb_counter` to read/write registers in a compact way.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_vhdl/counter_register_read_write_pkg.vhd
    :caption: Example register simulation read/write package.
    :language: VHDL
    :linenos:

|


.. _example_counter_simulation_check_package:

Generated VHDL simulation check package
_______________________________________

Below is the generated register simulation check package, created from the TOML file above via
the :class:`.VhdlSimulationCheckPackageGenerator` class.
It is used by the :ref:`example_tb_counter` to check that the ``status`` register has the
expected value.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_vhdl/counter_register_check_pkg.vhd
    :caption: Example register simulation check package.
    :language: VHDL
    :linenos:

|


.. _example_counter_simulation_wait_until_package:

Generated VHDL simulation wait until package
____________________________________________

Below is the generated register simulation wait until package, created from the TOML file above via
the :class:`.VhdlSimulationWaitUntilPackageGenerator` class.
It is used by the :ref:`example_tb_counter` to wait for registers to assume a give value.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_vhdl/counter_register_wait_until_pkg.vhd
    :caption: Example register simulation wait until package.
    :language: VHDL
    :linenos:

|


Performance
-----------

Since generation of VHDL packages is usually run in real time (e.g. before running a simulation) the
speed of the tool is important.
In order the save time, :meth:`.RegisterCodeGenerator.create_if_needed` maintains a hash of the
register definitions, and will only generate the VHDL file when necessary.
Hence it is recommended to call this function as opposed to :meth:`.RegisterCodeGenerator.create`
which will waste time by always re-creating, even when it is not necessary.

See :ref:`here <performance>` for a comparison with the performance of other tools.


.. _vhdl_dependencies:

Dependencies
------------

Generated VHDL code depends on files from `hdl-modules <https://hdl-modules.com>`_
version 6.2.0 or greater:

1. `axi_lite_pkg.vhd <https://github.com/hdl-modules/hdl-modules/blob/main/modules/axi_lite/src/axi_lite_pkg.vhd>`_
   and
   `axi_lite_register_file.vhd <https://github.com/hdl-modules/hdl-modules/blob/main/modules/register_file/src/axi_lite_register_file.vhd>`_
   in a library called ``axi_lite``.
2. `register_file_pkg.vhd <https://github.com/hdl-modules/hdl-modules/blob/main/modules/register_file/src/register_file_pkg.vhd>`_
   in a library called ``register_file``.

The simulation code is furthermore dependent on the file
`register_operations_pkg.vhd <https://github.com/hdl-modules/hdl-modules/blob/main/modules/register_file/sim/register_operations_pkg.vhd>`_
in the library ``register_file``, and access to `VUnit <https://vunit.github.io/>`_'s
VHDL libraries.


Unresolved types
----------------

The generated VHDL uses unresolved types
(e.g. ``std_ulogic_vector`` instead of ``std_logic_vector``) consistently.
This means that accidental multiple drivers of a signal will result in an error when simulating
or synthesizing the design.

Since e.g. ``std_logic`` is a sub-type of ``std_ulogic`` in VHDL-2008, it is no problem if
hdl-registers components are integrated in a code base that still uses the resolved types.
I.e. a ``std_logic`` signal can be assigned to a hdl-registers signal of type ``std_ulogic``,
and vice versa, without problem.


Further tools for simplifying register handling
-----------------------------------------------

There is a large eco-system of register-related components in the
`hdl-modules <https://hdl-modules.com>`__ project.
Firstly there are wrappers in the :ref:`bfm library <module_bfm>` for easier working with VUnit
verification components.
Furthermore there is a large number of synthesizable AXI/AXI-Lite components available that enable
the register bus:

* AXI-to-AXI-Lite converter: :ref:`axi_lite.axi_to_axi_lite`,
* AXI/AXI-Lite crossbar: :ref:`axi.axi_simple_read_crossbar`, :ref:`axi.axi_simple_write_crossbar`,
  :ref:`axi_lite.axi_lite_simple_read_crossbar`, :ref:`axi_lite.axi_lite_simple_write_crossbar`,
* AXI-Lite mux (splitter): :ref:`axi_lite.axi_lite_mux`,
* AXI-Lite clock domain crossing: :ref:`axi_lite.axi_lite_cdc`,
* etc...

See the :ref:`register_file library <module_register_file>`, :ref:`axi library <module_axi>` and
:ref:`axi_lite library <module_axi_lite>` for more details.
