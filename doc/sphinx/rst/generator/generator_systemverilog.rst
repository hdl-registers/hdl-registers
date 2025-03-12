.. _generator_systemverilog:

SystemVerilog generator
=======================

The :class:`.SystemVerilogAxiLiteGenerator` class creates a register file with AXI-Lite interface.
See :ref:`below <example_systemverilog>` for an example usage and a showcase of the code
that can be generated.


Details and limitations
-----------------------

The SystemVerilog code generator in hdl-registers is a wrapper around
`PeakRDL-regblock <https://github.com/SystemRDL/PeakRDL-regblock>`__.
The hdl-registers representation of register data is translated internally to a PeakRDL
representation before the PeakRDL exporter is called.
All the features of hdl-registers are supported, except for the following:

1. :ref:`Register constants <constant_overview>` (of any type).
2. :ref:`Register arrays <basic_feature_register_array>`.
3. :ref:`Integer fields <field_integer>` with signed range.
4. :ref:`Bit vector fields <field_bit_vector>` with a numeric interpretation other than unsigned.
5. Pulse-on-write :ref:`register modes <basic_feature_register_modes>`.

It is quite likely that some or even all of these could be supported in the future.
Some of the missing features are due to limitations in translation layer,
while others stem from the PeakRDL tool.


.. _systemverilog_flatten_axi_lite:

Configuration
_____________

The :meth:`.RegisterCodeGenerator.create` and :meth:`.RegisterCodeGenerator.create_if_needed`
methods of :class:`.SystemVerilogAxiLiteGenerator` can be supplied with a
``flatten_axi_lite`` argument.
If this is set to ``True``, the generated SystemVerilog module will have an input/output port
for each individual AXI-Lite signal.
If left as ``False``, the AXI-Lite signals will be grouped into a single SystemVerilog interface.

If using the non-flattened interface,
`this interface file \
<https://github.com/SystemRDL/PeakRDL-regblock/blob/main/hdl-src/axi4lite_intf.sv>`__
must be added to your simulation/build project.



.. _example_systemverilog:

Example
-------

An example is used to illustrate the generator API and to showcase the code that can be generated.


Register definition TOML file
_____________________________

The TOML file used in this example sets up some very basic registers with a few fields.

.. collapse:: Click to expand/collapse code.

  .. literalinclude:: example_basic/regs_basic.toml
    :caption: Example TOML file.
    :language: TOML
    :linenos:

|


Python file to generate register artifacts
__________________________________________

The Python code below is used to parse the above TOML file and generate the SystemVerilog code.


.. literalinclude:: py/generator_systemverilog.py
  :caption: Python code that parses the example TOML file and generates SystemVerilog code.
  :language: Python
  :linenos:
  :lines: 10-


Generated SystemVerilog register package
________________________________________

Below is the generated register package, which is used by the :ref:`generated_systemverilog`.
It must also be used wherever the register file is instantiated in order to get the correct
types for the register and field values.

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_systemverilog/basic_register_file_axi_lite_pkg.sv
  :caption: Example register package.
  :language: SystemVerilog
  :linenos:



.. _generated_systemverilog:

Generated SystemVerilog register file module
____________________________________________

Below is the generated SystemVerilog AXI-Lite register file module.

.. literalinclude:: ../../../../generated/sphinx_rst/register_code/generator/generator_systemverilog/basic_register_file_axi_lite.sv
  :caption: Example register file module.
  :language: SystemVerilog
  :linenos:
