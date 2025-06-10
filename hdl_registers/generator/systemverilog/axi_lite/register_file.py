# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.cpuif.axi4lite import AXI4Lite_Cpuif, AXI4Lite_Cpuif_flattened
from peakrdl_regblock.udps import ALL_UDPS
from systemrdl import RDLCompiler
from systemrdl.importer import RDLImporter
from systemrdl.rdltypes import AccessType
from systemrdl.rdltypes.user_enum import UserEnum, UserEnumMemberContainer
from tsfpga.system_utils import prepend_file

from hdl_registers.field.bit import Bit
from hdl_registers.field.bit_vector import BitVector
from hdl_registers.field.enumeration import Enumeration
from hdl_registers.field.integer import Integer
from hdl_registers.generator.register_code_generator import RegisterCodeGenerator
from hdl_registers.generator.register_code_generator_helpers import (
    iterate_registers,
    qualified_field_name,
)
from hdl_registers.register_modes import REGISTER_MODES

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from systemrdl.component import Addrmap, Field
    from systemrdl.node import RootNode

    from hdl_registers.field.register_field import RegisterField
    from hdl_registers.register import Register
    from hdl_registers.register_list import RegisterList


class SystemVerilogAxiLiteGenerator(RegisterCodeGenerator):
    """
    Generate a SystemVerilog register file with AXI-Lite interface.
    See the :ref:`generator_systemverilog` article for usage details.

    This generator will create

    1. the register file module, and
    2. a package file.

    The :meth:`.RegisterCodeGenerator.create` and :meth:`.RegisterCodeGenerator.create_if_needed`
    methods in this generator can be supplied with a ``flatten_axi_lite`` argument.
    See :ref:`here <systemverilog_flatten_axi_lite>` for details.
    """

    __version__ = "0.0.1"

    SHORT_DESCRIPTION = "SystemVerilog AXI-Lite register file"

    COMMENT_START = "//"

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        This specific generator will also create a package file with the same name, but with a
        ``_pkg`` suffix.
        """
        return self.output_folder / f"{self.name}_register_file_axi_lite.sv"

    @property
    def output_files(self) -> Iterable[Path]:
        """
        All the files that this generator creates.
        """
        output_file = self.output_file
        yield output_file
        yield output_file.parent / f"{output_file.stem}_pkg.sv"

    @property
    def should_create(self) -> bool:
        """
        Indicates if a (re-)create of artifacts is needed.
        Override the default behavior with a check for multiple files, instead of just one.
        """
        return any(self._should_create(file_path=file_path) for file_path in self.output_files)

    def get_code(
        self,
        **kwargs: Any,  # noqa: ANN401
    ) -> str:
        """
        Is required in the abstract base class, but not used in this generator.
        Do not call this method.
        """
        raise NotImplementedError("Do not call this method directly")

    def _create_artifact(
        self,
        output_file: Path,
        flatten_axi_lite: bool = False,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> Path:
        """
        Override how the artifact file is created, since when using PeakRDL one call will generate
        two files.
        So we can not use :meth:`.get_code` and the default behavior of :meth:`.create_file`.
        """
        # Import to SystemRDL representation.
        root_node = to_systemrdl(register_list=self.register_list)

        cpu_interface = AXI4Lite_Cpuif_flattened if flatten_axi_lite else AXI4Lite_Cpuif

        # Export to SystemVerilog.
        exporter = RegblockExporter()
        exporter.export(
            node=root_node,
            output_dir=str(self.output_folder),
            cpuif_cls=cpu_interface,
            module_name=self.output_file.stem,
        )

        # Prepend the hdl-registers header so we can detect if the file needs a re-create in
        # the future.
        header = self.header + "\n"
        for created_file in self.output_files:
            prepend_file(file_path=created_file, text=header)

        # Return just one of the two files, which isn't great, but we need to follow the API of the
        # base class.
        return output_file


def to_systemrdl(register_list: RegisterList) -> RootNode:
    """
    Translate the register data from hdl-registers representation to SystemRDL representation.

    .. warning::
        This is an internal function.
        Do not use it directly, API is subject to change.
    """
    compiler = RDLCompiler()
    for udp in ALL_UDPS:
        compiler.register_udp(definition_cls=udp)

    HdlRegistersImporter(compiler=compiler).import_register_list(register_list=register_list)

    return compiler.elaborate()


class HdlRegistersImporter(RDLImporter):
    """
    Importer class that translates the register data from hdl-registers representation
    to SystemRDL representation.

    .. warning::
        This is an internal class.
        Do not use it directly, API is subject to change.
    """

    # The register list to import.
    _register_list: RegisterList

    # A note about the source definition file, to be included in error messages.
    _source_note: str

    # The name of the register list, aka the name of the module.
    _name: str

    def import_register_list(self, register_list: RegisterList) -> None:
        """
        Call this method to perform the import.
        """
        self._register_list = register_list
        self._source_note = (
            ""
            if self._register_list.source_definition_file is None
            else f" in {self._register_list.source_definition_file}"
        )
        self._name = self._register_list.name

        source_definition_file = (
            ""
            if register_list.source_definition_file is None
            else str(register_list.source_definition_file)
        )
        # To set the 'default_src_ref'.
        # Does not seem to ever appear in the generated code,
        # but its part of the API so let's do it.
        self.import_file(path=source_definition_file)

        top_component = self.create_addrmap_definition(type_name=register_list.name)

        self._import(top_component=top_component)

        self.register_root_component(definition=top_component)

    def _import(self, top_component: Addrmap) -> None:
        if self._register_list.constants:
            raise ValueError(
                f'Error while translating "{self._name}"{self._source_note}: '
                "SystemVerilog generator does not support constants."
            )

        if not self._register_list.register_objects:
            raise ValueError(
                f'Error while translating "{self._name}"{self._source_note}: '
                "SystemVerilog generator requires at least one register."
            )

        for register, register_array in iterate_registers(register_list=self._register_list):
            if register_array is not None:
                raise ValueError(
                    f'Error while translating "{self._name}.{register_array.name}"'
                    f"{self._source_note}: "
                    "SystemVerilog generator does not support register arrays."
                )

            self._add_register(top_component=top_component, register=register)

    def _add_register(self, top_component: Addrmap, register: Register) -> None:
        if not register.fields:
            raise ValueError(
                f'Error while translating "{self._name}.{register.name}"{self._source_note}: '
                "SystemVerilog generator requires at least one field per register."
            )

        register_instance = self.instantiate_reg(
            comp_def=self.create_reg_definition(type_name=register.name),
            inst_name=register.name,
            addr_offset=register.address,
        )

        hw_access_type, sw_access_type = self._decode_register_mode(register=register)
        for field in register.fields:
            self._add_field(
                register_component=register_instance,
                hw_access_type=hw_access_type,
                sw_access_type=sw_access_type,
                register=register,
                field=field,
            )

        self.add_child(parent=top_component, child=register_instance)

    def _add_field(
        self,
        register_component: Addrmap,
        hw_access_type: AccessType,
        sw_access_type: AccessType,
        register: Register,
        field: RegisterList.Register.Field,
    ) -> None:
        field_instance = self.instantiate_field(
            comp_def=self.create_field_definition(type_name=field.name),
            inst_name=field.name,
            bit_offset=field.base_index,
            bit_width=field.width,
        )

        self.assign_property(component=field_instance, prop_name="hw", value=hw_access_type)
        self.assign_property(component=field_instance, prop_name="sw", value=sw_access_type)

        self._assign_field_properties(register=register, field=field, field_instance=field_instance)

        self.add_child(parent=register_component, child=field_instance)

    def _assign_field_properties(
        self, register: Register, field: RegisterField, field_instance: Field
    ) -> None:
        if isinstance(field, Bit):
            self.assign_property(
                component=field_instance, prop_name="reset", value=int(field.default_value)
            )
            return

        if isinstance(field, BitVector):
            self.assign_property(
                component=field_instance, prop_name="reset", value=int(field.default_value, base=2)
            )
            return

        if isinstance(field, Enumeration):
            members = [
                UserEnumMemberContainer(name=element.name, value=element.value)
                for element in field.elements
            ]
            enum_type = UserEnum.define_new(
                qualified_field_name(
                    register_list=self._register_list, register=register, field=field
                ),
                members,
            )
            self.assign_property(component=field_instance, prop_name="encode", value=enum_type)
            self.assign_property(
                component=field_instance, prop_name="reset", value=field.default_value.value
            )
            return

        if isinstance(field, Integer):
            if field.is_signed:
                # Mainly because it's a hassle to convert a negative default value number to
                # positive representation here.
                raise ValueError(
                    f'Error while translating "{self._name}.{register.name}.{field.name}"'
                    f"{self._source_note}: "
                    "SystemVerilog generator does not support signed integer fields."
                )

            self.assign_property(
                component=field_instance, prop_name="reset", value=field.default_value
            )
            return

        raise ValueError(f"Unknown field: {field}")

    def _decode_register_mode(self, register: Register) -> tuple[AccessType, AccessType]:
        """
        Return tuple: (hardware access, software access).
        """
        if register.mode == REGISTER_MODES["r"]:
            # HW provides a value that SW can read.
            return AccessType.w, AccessType.r

        if register.mode == REGISTER_MODES["w"]:
            # SW writes a value that HW can use.
            return AccessType.r, AccessType.w

        if register.mode == REGISTER_MODES["r_w"]:
            # SW writes a value that HW can use.
            # SW can also read back the value.
            return AccessType.r, AccessType.rw

        raise ValueError(
            f'Error while translating "{self._name}.{register.name}"{self._source_note}: '
            f"SystemVerilog generator does not support register mode: {register.mode}"
        )
