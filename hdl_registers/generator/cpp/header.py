# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl-registers project, an HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://github.com/hdl-registers/hdl-registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
from pathlib import Path
from typing import Any

# Local folder libraries
from .cpp_generator_common import CppGeneratorCommon


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

    def get_code(self, **kwargs: Any) -> str:
        """
        Get a complete C++ class header with methods for accessing registers and fields.
        """
        cpp_code = f"  class {self._class_name} : public I{self._class_name}\n"
        cpp_code += "  {\n"

        cpp_code += "  private:\n"
        cpp_code += "    volatile uint32_t *m_registers;\n\n"

        cpp_code += "  public:\n"
        cpp_code += f"    {self._constructor_signature()};\n\n"
        cpp_code += f"    virtual ~{self._class_name}() {{}}\n"

        def function(return_type_name: str, signature: str) -> str:
            return f"    virtual {return_type_name} {signature} const override;\n"

        for register, register_array in self.iterate_registers():
            cpp_code += f"\n{self.get_separator_line()}"

            description = self._get_methods_description(
                register=register, register_array=register_array
            )
            cpp_code += self.comment_block(
                text=[description, "See interface header for documentation."]
            )

            if register.mode.software_can_read:
                signature = self._register_getter_function_signature(
                    register=register, register_array=register_array
                )
                cpp_code += function(return_type_name="uint32_t", signature=signature)

                for field in register.fields:
                    field_type_name = self._field_value_type_name(
                        register=register, register_array=register_array, field=field
                    )

                    signature = self._field_getter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=False,
                    )
                    cpp_code += function(return_type_name=field_type_name, signature=signature)

                    signature = self._field_getter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=True,
                    )
                    cpp_code += function(return_type_name=field_type_name, signature=signature)

            if register.mode.software_can_write:
                signature = self._register_setter_function_signature(
                    register=register, register_array=register_array
                )

                cpp_code += function(return_type_name="void", signature=signature)

                for field in register.fields:
                    signature = self._field_setter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=False,
                    )
                    cpp_code += function(return_type_name="void", signature=signature)

                    signature = self._field_setter_function_signature(
                        register=register,
                        register_array=register_array,
                        field=field,
                        from_value=True,
                    )
                    cpp_code += function(return_type_name="uint32_t", signature=signature)

        cpp_code += "  };\n"

        cpp_code_top = f"""\
{self.header}
#pragma once

#include "i_{self.name}.h"

"""
        return cpp_code_top + self._with_namespace(cpp_code)
