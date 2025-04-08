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

from .cpp_generator_common import CppGeneratorCommon

if TYPE_CHECKING:
    from pathlib import Path

    from hdl_registers.register import Register
    from hdl_registers.register_array import RegisterArray


class CppHeaderGenerator(CppGeneratorCommon):
    """
    Generate a C++ class header.
    See the :ref:`generator_cpp` article for usage details.

    The class header will contain:

    * for each register, signature of getter and setter methods for reading/writing the register as
      an ``uint``.

    * for each field in each register, signature of getter and setter methods for reading/writing
      the field as its native type (enumeration, positive/negative int, etc.).

      * The setter will read-modify-write the register to update only the specified field,
        depending on the mode of the register.
    """

    __version__ = "1.0.0"

    SHORT_DESCRIPTION = "C++ header"

    DEFAULT_INDENTATION_LEVEL = 4

    @property
    def output_file(self) -> Path:
        """
        Result will be placed in this file.
        """
        return self.output_folder / f"{self.name}.h"

    def get_code(
        self,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> str:
        """
        Get a complete C++ class header with methods for accessing registers and fields.
        """
        public_cpp = ""
        private_cpp = ""
        separator = self.get_separator_line()

        for register, register_array in self.iterate_registers():
            heading = self._get_register_heading(
                register=register, register_array=register_array, separator=separator
            )
            public_cpp += heading

            register_has_private_methods = len(register.fields) != 0
            if register_has_private_methods:
                private_cpp += heading

            if register.mode.software_can_read:
                public_getters, private_getters = self._get_getters(
                    register=register, register_array=register_array
                )
                public_cpp += public_getters
                private_cpp += private_getters

                if register.mode.software_can_write:
                    # Add empty line between getter and setter interfaces.
                    public_cpp += "\n"
                    if register_has_private_methods:
                        private_cpp += "\n"

            if register.mode.software_can_write:
                public_setters, private_setters = self._get_setters(
                    register=register, register_array=register_array
                )
                public_cpp += public_setters
                private_cpp += private_setters

            public_cpp += separator
            if register_has_private_methods:
                private_cpp += separator

        cpp_code = f"""\
  class {self._class_name} : public I{self._class_name}
  {{
  public:
    /**
     * Class constructor.
     * @param base_address Byte address where these registers are memory mapped.
     *                     Can be e.g. '0x43C00000' in bare metal, or e.g.
     *                     'reinterpret_cast<uintptr_t>(mmap(...))' in Linux.
     *                     When using an operating system, care must be taken to pass the
     *                     virtual address, not the physical address.
     *                     When using bare metal, these are the same.
     * @param assertion_handler Function to call when an assertion fails.
     *                          Function takes a string pointer as an argument, where the string
     *                          will contain an error diagnostic message.
     *                          Function must return a boolean 'true'.
     */
    {self._constructor_signature()};

    virtual ~{self._class_name}() {{}}
{public_cpp}
  private:
    volatile uint32_t *m_registers;
    bool (*m_assertion_handler) (const std::string*);
{private_cpp}\
  }};

"""
        cpp_code_top = f"""\
#pragma once

#include "i_{self.name}.h"

"""
        return cpp_code_top + self._with_namespace(cpp_code)

    def _get_getters(
        self, register: Register, register_array: RegisterArray | None
    ) -> tuple[str, str]:
        def get_from_raw_function(comment: str, return_type: str, signature: str) -> str:
            return f"""\
{comment}\
    {return_type} {signature};
"""

        public_cpp: list[str] = []
        private_cpp: list[str] = []

        register_type = self._get_register_value_type(
            register=register, register_array=register_array
        )
        signature = self._register_getter_signature(
            register=register, register_array=register_array
        )
        public_cpp.append(
            self._get_override_function(
                comment=self._get_getter_comment(),
                return_type=register_type,
                signature=signature,
            )
        )

        if register.fields:
            # The main getter will perform type conversion.
            # Provide a getter that returns the raw value also.
            signature = self._register_getter_signature(
                register=register, register_array=register_array, raw=True
            )
            public_cpp.append(
                self._get_override_function(
                    comment=self._get_getter_comment(raw=True),
                    return_type="uint32_t",
                    signature=signature,
                )
            )

        for field in register.fields:
            field_type = self._get_field_value_type(
                register=register, register_array=register_array, field=field
            )

            signature = self._field_getter_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=False,
            )
            public_cpp.append(
                self._get_override_function(
                    comment=self._get_getter_comment(field=field),
                    return_type=field_type,
                    signature=signature,
                )
            )

            signature = self._field_getter_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=True,
            )
            private_cpp.append(
                get_from_raw_function(
                    comment=self._get_from_raw_comment(field=field),
                    return_type=field_type,
                    signature=signature,
                )
            )

        return "\n".join(public_cpp), "\n".join(private_cpp)

    @staticmethod
    def _get_override_function(comment: str, return_type: str, signature: str) -> str:
        return f"""\
{comment}\
    virtual {return_type} {signature} override;
"""

    def _get_setters(
        self, register: Register, register_array: RegisterArray | None
    ) -> tuple[str, str]:
        def get_to_raw_function(comment: str, signature: str) -> str:
            return f"""\
{comment}\
    uint32_t {signature};
"""

        public_cpp: list[str] = []
        private_cpp: list[str] = []

        signature = self._register_setter_signature(
            register=register, register_array=register_array
        )
        public_cpp.append(
            self._get_override_function(
                comment=self._get_setter_comment(register=register),
                return_type="void",
                signature=signature,
            )
        )

        if register.fields:
            # The main setter will perform type conversion.
            # Provide a setter that takes a raw value also.
            signature = self._register_setter_signature(
                register=register, register_array=register_array, raw=True
            )
            public_cpp.append(
                self._get_override_function(
                    comment=self._get_setter_comment(register=register, raw=True),
                    return_type="void",
                    signature=signature,
                )
            )

        for field in register.fields:
            signature = self._field_setter_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=False,
            )
            public_cpp.append(
                self._get_override_function(
                    comment=self._get_setter_comment(register=register, field=field),
                    return_type="void",
                    signature=signature,
                )
            )

            signature = self._field_to_raw_signature(
                register=register, register_array=register_array, field=field
            )
            private_cpp.append(
                get_to_raw_function(
                    comment=self._get_to_raw_comment(field=field), signature=signature
                )
            )

        return "\n".join(public_cpp), "\n".join(private_cpp)
