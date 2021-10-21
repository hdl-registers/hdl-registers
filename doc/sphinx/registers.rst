.. _registers:

Register code generation
========================

There is a register code generation eco-system available in tsfpga which generates code from textual configuration files.
To start using it simply create a file ``regs_<name>.toml`` in the root of a module

From the TOML definition the register generator can create a VHDL package with all registers and their fields.
This VHDL package can then be used with the generic AXI-Lite register file in tsfpga.
Apart from that a C header and a C++ class can be generated, as well as a HTML page with human-readable documentation.

The register generator is well-integrated in the tsfpga module work flow.
It is fast enough that before each build and each simulation run, the modules will re-generate their VHDL register package so that it is always up-to-date.
Creating documentation and headers, which are typically distributed as part of FPGA release artifacts, is simple and easy to integrate in a build script.

There is also a set of VHDL AXI components that enable the register bus: AXI-to-AXI-Lite converter, AXI/AXI-Lite interconnect, AXI-Lite mux (splitter), AXI-Lite clock domain crossing, AXI-Lite generic register file.
These are found in the repo within the `axi module <https://gitlab.com/tsfpga/tsfpga/-/tree/master/modules/axi>`__.



.. _register_toml_format:

Register TOML format
--------------------

The register generator parses a TOML file in order to gather all register information.
It is important the the TOML is formatted correctly and has the necessary fields.
The register TOML parser will warn if there are any error in the TOML, such as missing fields, unknown fields, wrong data types for fields, etc.

Below is a compilation of all the TOML properties that are available.
Comments describe what attributes are optional and which are required.


.. code-block:: toml
  :caption: Register TOML format rules.

  ################################################################################
  # This will allocate a register with the name "configuration".
  [register.configuration]

  # The "mode" property MUST be present for a register.
  # The value specified must be a valid mode string value.
  mode = "r_w"
  # The "description" property is optional for a register. Will default to "" if not specified.
  # The value specified must be a string.
  description = """This is the description of my register.

  Rudimentary RST formatting can be used, such as **boldface** and *italics*."""


  # This will allocate a bit field named "enable" in the "configuration" register.
  [register.configuration.bit.enable]

  # The "description" property is optional for a bit field. Will default to "" if not specified.
  # The value specified must be a string.
  description = "Description of the **enable** bit field."
  # The "default_value" property is optional for a bit field.
  # Must hold either of the strings "1" or "0" if specified.
  # Will default to "0" if not specified.
  default_value = "1"


  # This will allocate a bit vector field named "data_tag" in the "configuration" register.
  [register.configuration.bit_vector.data_tag]

  # The "width" property MUST be present for a bit vector field.
  # The value specified must be an integer.
  width = 4
  # The "description" property is optional for a bit vector field. Will default to "" if not specified.
  # The value specified must be a string.
  description = "Description of my **data_tag** bit vector field."
  # The "default_value" property is optional for a bit vector field.
  # The value specified must be a string whose length is the same as the specified **width** property value.
  # May only contain ones and zeros.
  # Will default to all zeros if not specified.
  default_value = "0101"


  ################################################################################
  # This will allocate a register array with the name "base_addresses".
  [register_array.base_addresses]

  # The "array_length" property MUST be present for a register array.
  # The value specified must be an integer.
  # The registers within the array will be repeated this many times.
  array_length = 3
  # The "description" property is optional for a register array. Will default to "" if not specified.
  # The value specified must be a string.
  description = "One set of base addresses for each feature."


  # ------------------------------------------------------------------------------
  # This will allocate a register "read_address" in the "base_addresses" array.
  [register_array.base_addresses.register.read_address]

  # Registers in a register array follow the exact same rules as "plain" registers.
  # The properties that may and must be set are the same.
  # Fields (bits, bit vectors, ...) can be added to array registers in the same way.
  mode = "w"

  # This will allocate a bit vector field named "address" in the "read_address" register within the "base_addresses" array.
  [register_array.base_addresses.register.read_address.bit_vector.address]

  width = 28
  description = "Read address for a 256 MB address space."


  # ------------------------------------------------------------------------------
  # This will allocate a register "write_address" in the "base_addresses" array.
  [register_array.base_addresses.register.write_address]

  mode = "w"

  # This will allocate a bit vector field named "address" in the "write_address" register within the "base_addresses" array.
  [register_array.base_addresses.register.write_address.bit_vector.address]

  width = 28
  description = "Write address for a 256 MB address space."



.. _default_registers:

Default registers
-----------------

A lot of projects use a few default registers in standard locations that shall be present in all modules.
Passing a list of :class:`.Register` objects will insert them in the register list of all modules that use registers.


Bus layout
----------

Below is a diagram of the typical layout for a register bus.

.. digraph:: my_graph

  graph [ dpi = 300 splines=ortho ];
  rankdir="LR";

  cpu [ label="AXI master\n(CPU)" shape=box ];
  cpu -> axi_to_axi_lite [label="AXI"];

  axi_to_axi_lite [ label="axi_to_axi_lite" shape=box ];
  axi_to_axi_lite -> axi_lite_mux  [label="AXI-Lite" ];

  axi_lite_mux [ label="axi_lite_mux" shape=box height=3.5 ];

  axi_lite_mux -> axi_lite_reg_file0;
  axi_lite_reg_file0 [ label="axi_lite_reg_file" shape=box ];

  axi_lite_mux -> axi_lite_reg_file1;
  axi_lite_reg_file1 [ label="axi_lite_reg_file" shape=box ];

  axi_lite_mux -> axi_lite_cdc2;
  axi_lite_cdc2 [ label="axi_lite_cdc" shape=box ];
  axi_lite_cdc2 -> axi_lite_reg_file2;
  axi_lite_reg_file2 [ label="axi_lite_reg_file" shape=box ];

  axi_lite_mux -> axi_lite_cdc3;
  axi_lite_cdc3 [ label="axi_lite_cdc" shape=box ];
  axi_lite_cdc3 -> axi_lite_reg_file3;
  axi_lite_reg_file3 [ label="axi_lite_reg_file" shape=box ];

  dots [ shape=none label="..."];
  axi_lite_mux -> dots;

In tsfpga, the register bus used is AXI-Lite.
In cases where a module uses a different clock than the AXI master (CPU), the bus must be resynchronized.
This makes sure that each module's register values are always in the clock domain where they are used.
This means that the module design does not have to worry about metastability, vector coherency, pulse resynchronization, etc.

* ``axi_to_axi_lite`` is a simple protocol converter between AXI and AXI-Lite.
  It does not perform any burst splitting or handling of write strobes, but instead assumes the master to be well behaved.
  If this is not the case, AXI slave error (``SLVERR``) will be sent on the response channel (``R``/``B``).

* ``axi_lite_mux`` is a 1-to-N AXI-Lite multiplexer that operates based on base addresses and address masks specified via a generic.
  If the address requested by the master does not match any slave, AXI decode error (``DECERR``) will be sent on the response channel (``R``/``B``).
  There will still be proper AXI handshaking done, so the master will not be stalled.

* ``axi_lite_cdc`` is an asynchronous FIFO-based clock domain crossing (CDC) for AXI-Lite buses.
  It must be used in the cases where the ``axi_lite_reg_file`` (i.e. your module) is in a different clock domain than the CPU AXI master.

* ``axi_lite_reg_file`` is a generic, parameterizable, register file for AXI-Lite register buses.
  It is parameterizable via a generic that sets the list of registers, with their modes and their default values.
  If the address requested by the master does not match any register, or there is a
  mode mismatch (e.g. write to a read-only register), AXI slave error (``SLVERR``) will be sent on the response channel (``R``/``B``).

All these entities are available in the repo in the `axi <https://gitlab.com/tsfpga/tsfpga/-/tree/master/modules/axi>`__
and `reg_file <https://gitlab.com/tsfpga/tsfpga/-/tree/master/modules/reg_file>`__ modules.
Note that there is a convenience wrapper
`axi.axi_to_axi_lite_vec <https://gitlab.com/tsfpga/tsfpga/-/tree/master/modules/axi/src/axi_to_axi_lite_vec.vhd>`__
that instantiates ``axi_to_axi_lite``, ``axi_lite_mux`` and any necessary ``axi_lite_cdc`` based on the appropriate generics.

