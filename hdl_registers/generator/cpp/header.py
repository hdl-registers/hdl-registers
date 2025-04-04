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
            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            public_cpp += f"""\
{separator}\
    // {description}
    // Mode '{register.mode.name}'.
{separator}\
"""

            if register.mode.software_can_read:
                public_cpp += self._get_public_getters(
                    register=register, register_array=register_array
                )
                private_cpp += self._get_private_getters(
                    register=register, register_array=register_array
                )

                if register.fields and register.mode.software_can_read:
                    # Add empty line between getter and setter interfaces.
                    public_cpp += "\n"

            if register.mode.software_can_write:
                public_cpp += self._get_setters(register=register, register_array=register_array)

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

{private_cpp}
  }};

"""
        cpp_code_top = f"""\
#pragma once

#include "i_{self.name}.h"

"""
        return cpp_code_top + self._with_namespace(cpp_code)

    def _get_public_getters(self, register: Register, register_array: RegisterArray | None) -> str:
        cpp_code: list[str] = []

        register_type = self._get_register_value_type(
            register=register, register_array=register_array
        )
        signature = self._register_getter_signature(
            register=register, register_array=register_array
        )
        cpp_code.append(self._get_override_function(return_type=register_type, signature=signature))

        for field in register.fields:
            field_type = self._get_field_value_type(
                register=register, register_array=register_array, field=field
            )
            signature = self._field_getter_function_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=False,
            )
            cpp_code.append(
                self._get_override_function(return_type=field_type, signature=signature)
            )

        return "\n".join(cpp_code)

    @staticmethod
    def _get_override_function(return_type: str, signature: str) -> str:
        return f"""\
  // See interface header for documentation.
  virtual {return_type} {signature} const override;
"""

    def _get_private_getters(self, register: Register, register_array: RegisterArray | None) -> str:
        cpp_code = ""

        def get_function(comment: str, return_type: str, signature: str) -> str:
            return f"""\
    // {comment}
    static {return_type} {signature};
"""

        for field in register.fields:
            field_type = self._get_field_value_type(
                register=register, register_array=register_array, field=field
            )
            signature = self._field_getter_function_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=True,
            )

            cpp_code += get_function(
                comment=f"Slice out the '{field.name}' field value from a raw register value.",
                return_type=field_type,
                signature=signature,
            )

        return cpp_code

    def _get_setters(self, register: Register, register_array: RegisterArray | None) -> str:
        cpp_code: list[str] = []

        signature = self._register_setter_function_signature(
            register=register, register_array=register_array
        )
        cpp_code.append(self._get_override_function(return_type="void", signature=signature))

        for field in register.fields:
            signature = self._field_setter_function_signature(
                register=register,
                register_array=register_array,
                field=field,
                from_raw=False,
            )
            cpp_code.append(self._get_override_function(return_type="void", signature=signature))

        return "\n".join(cpp_code)
