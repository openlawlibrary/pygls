"""Script to automatically generate a lanaguge client and server from `lsprotocol`
type definitons."""

import argparse
import inspect
import pathlib
import re
import textwrap
import typing
from typing import Any
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type

from lsprotocol._hooks import _resolve_forward_references
from lsprotocol.types import ClientCapabilities
from lsprotocol.types import ServerCapabilities
from lsprotocol.types import METHOD_TO_TYPES
from lsprotocol.types import message_direction

cli = argparse.ArgumentParser(
    description="generate language client from lsprotocol types."
)
cli.add_argument("output", type=pathlib.Path)

LICENSE_HEADER = """\
############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
"""


def write_imports(imports: Set[Tuple[str, str]]) -> str:
    """Write the standard runtime Python imports for the given set of ``imports``"""
    lines = []

    for import_ in sorted(list(imports), key=lambda i: (i[0], i[1])):
        if isinstance(import_, tuple):
            mod, name = import_
            lines.append(f"from {mod} import {name}")
            continue

        lines.append(f"import {import_}")

    return "\n".join(lines)


def write_typing_imports(imports: Set[Tuple[str, str]]) -> str:
    """Write ``TYPE_CHECKING`` imports for the given set of ``imports``"""
    lines = [
        "if typing.TYPE_CHECKING:",
        textwrap.indent(write_imports(imports), " " * 4),
    ]
    return "\n".join(lines)


def to_snake_case(string: str) -> str:
    return "".join(f"_{c.lower()}" if c.isupper() else c for c in string)


def write_client_notification(
    method: str,
    request: Type,
    params: Optional[Type],
    imports: Set[Tuple[str, str]],
) -> str:
    python_name = to_snake_case(method).replace("/", "_").replace("$_", "")

    if params is None:
        param_name = "None"
        param_mod = ""
    else:
        param_mod, param_name = params.__module__, params.__name__
        param_mod = param_mod.replace("lsprotocol.types", "types") + "."

    return "\n".join(
        [
            f"def {python_name}(self, params: {param_mod}{param_name}) -> None:",
            f'    """Send a :lsp:`{method}` notification.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            "    if self.stopped:",
            '        raise RuntimeError("Client has been stopped.")',
            "",
            f'    self.protocol.notify("{method}", params)',
            "",
        ]
    )


def write_server_notification(
    method: str,
    request: Type,
    params: Optional[Type],
    imports: Set[Tuple[str, str]],
) -> str:
    python_name = to_snake_case(method).replace("/", "_").replace("$_", "")

    if params is None:
        param_name = "None"
        param_mod = ""
    elif "lsprotocol" not in str(params):
        param_mod = str(params)
        param_name = ""
    else:
        param_mod, param_name = params.__module__, params.__name__
        param_mod = param_mod.replace("lsprotocol.types", "types") + "."

    return "\n".join(
        [
            f"def {python_name}(self, params: {param_mod}{param_name}) -> None:",
            f'    """Send a :lsp:`{method}` notification.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            f'    self.protocol.notify("{method}", params)',
            "",
        ]
    )


def get_response_type(response: Type, imports: Set[Tuple[str, str]]) -> str:
    # Find the response type.
    result_field = [f for f in response.__attrs_attrs__ if f.name == "result"][0]
    return rewrite_type(str(result_field.type), imports)


def rewrite_type(type_name: str, imports: set[tuple[str, str]]) -> str:
    result = re.sub(r"<class '([\w.]+)'>", r"\1", type_name)

    # For some reason enum reprs are not namespaced...
    result = re.sub(r"<enum '([\w.]+)'>", r"types.\1", result)

    result = re.sub(r"ForwardRef\('([\w.]+)'\)", r"lsprotocol.types.\1", result)
    result = result.replace("NoneType", "None")

    # Replace any typing imports with their short name.
    for match in re.finditer(r"typing.([\w]+)", result):
        imports.add(("typing", match.group(1)))

    result = result.replace("lsprotocol.types.", "types.")
    result = result.replace("typing.", "")

    return result


def write_client_method(
    method: str,
    request: Type,
    params: Optional[Type],
    response: Type,
    imports: Set[Tuple[str, str]],
) -> str:
    python_name = to_snake_case(method).replace("/", "_").replace("$_", "")

    if params is None:
        param_name = "None"
        param_mod = ""
    else:
        param_mod, param_name = params.__module__, params.__name__
        param_mod = param_mod.replace("lsprotocol.types", "types") + "."

    result_type = get_response_type(response, imports)

    return "\n".join(
        [
            f"def {python_name}(",
            "    self,",
            f"    params: {param_mod}{param_name},",
            f"    callback: Optional[Callable[[{result_type}], None]] = None,",
            f") -> Future[{result_type}]:",
            f'    """Make a :lsp:`{method}` request.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            "    if self.stopped:",
            '        raise RuntimeError("Client has been stopped.")',
            "",
            f'    return self.protocol.send_request("{method}", params, callback)',
            "",
            f"async def {python_name}_async(",
            "    self,",
            f"    params: {param_mod}{param_name},",
            f") -> {result_type}:",
            f'    """Make a :lsp:`{method}` request.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            "    if self.stopped:",
            '        raise RuntimeError("Client has been stopped.")',
            "",
            f'    return await self.protocol.send_request_async("{method}", params)',
            "",
        ]
    )


def write_server_method(
    method: str,
    request: Type,
    params: Optional[Type],
    response: Type,
    imports: Set[Tuple[str, str]],
) -> str:
    python_name = to_snake_case(method).replace("/", "_").replace("$_", "")

    if params is None:
        param_name = "None"
        param_mod = ""
    else:
        param_mod, param_name = params.__module__, params.__name__
        param_mod = param_mod.replace("lsprotocol.types", "types") + "."

    result_type = get_response_type(response, imports)

    return "\n".join(
        [
            f"def {python_name}(",
            "    self,",
            f"    params: {param_mod}{param_name},",
            f"    callback: Optional[Callable[[{result_type}], None]] = None,",
            f") -> Future[{result_type}]:",
            f'    """Make a :lsp:`{method}` request.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            f'    return self.protocol.send_request("{method}", params, callback)',
            "",
            f"async def {python_name}_async(",
            "    self,",
            f"    params: {param_mod}{param_name},",
            f") -> {result_type}:",
            f'    """Make a :lsp:`{method}` request.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            f'    return await self.protocol.send_request_async("{method}", params)',
            "",
        ]
    )


def generate_client() -> str:
    methods = []
    imports = {
        "typing",
        ("lsprotocol", "types"),
        ("pygls.protocol", "LanguageServerProtocol"),
        ("pygls.protocol", "default_converter"),
        ("pygls.client", "JsonRPCClient"),
    }

    typing_imports = {
        "cattrs",
        ("concurrent.futures", "Future"),
        ("typing", "Callable"),
        ("typing", "Optional"),
    }

    for method_name, types in METHOD_TO_TYPES.items():
        # Skip any requests that come from the server.
        if message_direction(method_name) == "serverToClient":
            continue

        request, response, params, _ = types

        if response is None:
            method = write_client_notification(
                method_name, request, params, typing_imports
            )
        else:
            method = write_client_method(
                method_name, request, params, response, typing_imports
            )

        methods.append(textwrap.indent(method, "    "))

    code = [
        LICENSE_HEADER,
        "# GENERATED FROM scripts/generate_code.py -- DO NOT EDIT",
        "# flake8: noqa",
        "from __future__ import annotations",
        "",
        write_imports(imports),
        "",
        write_typing_imports(typing_imports),
        "",
        "",
        "class BaseLanguageClient(JsonRPCClient):",
        "",
        "    def __init__(",
        "        self,",
        "        name: str,",
        "        version: str,",
        "        protocol_cls: type[LanguageServerProtocol] = LanguageServerProtocol,",
        "        converter_factory: Callable[[], cattrs.Converter] = default_converter,",
        "    ):",
        "        self.name = name",
        "        self.version = version",
        "        super().__init__(protocol_cls, converter_factory)",
        "",
        *methods,
    ]
    return "\n".join(code)


def generate_server() -> str:
    methods = []
    imports = {
        "typing",
        ("lsprotocol", "types"),
        ("pygls.protocol", "LanguageServerProtocol"),
        ("pygls.protocol", "default_converter"),
        ("pygls.server", "JsonRPCServer"),
    }

    typing_imports = {
        ("concurrent.futures", "Future"),
        ("typing", "Callable"),
        ("typing", "Optional"),
        ("cattrs", "Converter"),
    }

    for method_name, types in METHOD_TO_TYPES.items():
        # Skip any requests that come from the client.
        if message_direction(method_name) == "clientToServer":
            continue

        request, response, params, _ = types

        if response is None:
            method = write_server_notification(
                method_name, request, params, typing_imports
            )
        else:
            method = write_server_method(
                method_name, request, params, response, typing_imports
            )

        methods.append(textwrap.indent(method, "    "))

    code = [
        LICENSE_HEADER,
        "# GENERATED FROM scripts/generate_code.py -- DO NOT EDIT",
        "# flake8: noqa",
        "from __future__ import annotations",
        "",
        write_imports(imports),
        "",
        write_typing_imports(typing_imports),
        "",
        "",
        "class BaseLanguageServer(JsonRPCServer):",
        "",
        "    protocol: LanguageServerProtocol",
        "",
        "    def __init__(",
        "        self,",
        "        protocol_cls: type[LanguageServerProtocol] = LanguageServerProtocol,",
        "        converter_factory: Callable[[], Converter] = default_converter,",
        "        max_workers: int | None = None,",
        "    ):",
        "        super().__init__(protocol_cls, converter_factory, max_workers)",
        "",
        *methods,
    ]
    return "\n".join(code)


def write_overload(fn: str, args: list[tuple[str, str]], result: str) -> str:
    """Write a typing overload for the given function"""

    arguments = ", ".join([f"{pname}: {ptype}" for pname, ptype in args])

    lines = [
        "@typing.overload",
        f"def {fn}({arguments}) -> {result}: ...",
    ]

    return "\n".join(lines)


def write_capability_overloads_for(
    base_type: str,
    obj: type[Any],
    overloads: list[str],
    imports: set[tuple[str, str]],
    processed_capabilities: set[str],
    prefix: str = "",
):
    """Write the ``get_capability`` overloads for the given type

    This function will iterate over all of the fields of ``obj`` and
    append a corresponding overload to ``overloads``. It will then
    recurse on each of the fields of ``obj`` so that we eventually emit
    an overload for each nested field under the original ``base_type``.

    Parameters
    ----------
    base_type
       The type of the ``capabilities`` argument to ``get_capabilities``

    obj
       The type we are currently generating overloads for

    overloads
       The list of overloads written so far

    imports
       The set of import statements to add to the generated module

    processed_capabilities
       The set of capabilities we have processed so far, used to prevent
       generating duplicated overloads.

    prefix
       The common prefix to assign to all fields of ``obj``
       e.g. ``text_document.completion``
    """

    if not hasattr(obj, "__attrs_attrs__"):
        return

    base_args = [("capabilities", base_type)]

    for field in obj.__attrs_attrs__:
        if prefix:
            field_name = f"{prefix}.{field.name}"
        else:
            field_name = field.name

        result_types = []
        result_type_names = {"None"}

        if "typing." in str(field.type):
            inner_types = typing.get_args(field.type)
            for field_type in inner_types:
                result_types.append(field_type)
                field_type_name = rewrite_type(str(field_type), imports)
                result_type_names.add(field_type_name)
        else:
            field_type = field.type
            result_types.append(field_type)
            result_type_names.add(rewrite_type(str(field_type), imports))

        if field_name not in processed_capabilities:
            processed_capabilities.add(field_name)

            # First we write the overload in which the caller does not provide a default
            # (or provides None) and we may return None.
            result_type_names_string = " | ".join(
                sorted(result_type_names, key=len, reverse=True)
            )
            args = [
                *base_args,
                ("field", f"Literal['{field_name}']"),
                ("default", "None = None"),
            ]

            overloads.append(
                write_overload("get_capability", args, result_type_names_string)
            )

            # Then we write the overload in which the caller provides a default value.
            result_type_names.remove("None")
            result_type_names_string = " | ".join(
                sorted(result_type_names, key=len, reverse=True)
            )
            args = [
                *base_args,
                ("field", f"Literal['{field_name}']"),
                ("default", result_type_names_string),
            ]

            overloads.append(
                write_overload("get_capability", args, result_type_names_string)
            )

        for nested_type in result_types:
            write_capability_overloads_for(
                base_type,
                nested_type,
                overloads,
                imports,
                processed_capabilities,
                prefix=field_name,
            )


def generate_capabilities() -> str:
    imports = {
        "typing",
        ("functools", "reduce"),
    }

    typing_imports = {
        ("typing", "Literal"),
        ("lsprotocol", "types"),
    }

    overloads = []
    write_capability_overloads_for(
        "types.ClientCapabilities",
        ClientCapabilities,
        overloads,
        typing_imports,
        processed_capabilities=set(),
        prefix="",
    )
    write_capability_overloads_for(
        "types.ServerCapabilities",
        ServerCapabilities,
        overloads,
        typing_imports,
        processed_capabilities=set(),
        prefix="",
    )

    code = [
        LICENSE_HEADER,
        "# GENERATED FROM scripts/generate_code.py -- DO NOT EDIT",
        "# flake8: noqa",
        "from __future__ import annotations",
        "",
        write_imports(imports),
        "",
        write_typing_imports(typing_imports),
        "",
        *overloads,
        "@typing.overload",
        "def get_capability(capabilities: Any, field: str, default: Any | None = None) -> Any | None: ...",
        "def get_capability(capabilities, field, default = None):",
        '    """Return the value of some nested capability with a fallback value to use in the',
        '       case where it does not exist."""' "",
        "    try:",
        '        value = reduce(getattr, field.split("."), capabilities)',
        "    except AttributeError:",
        "        return default",
        "",
        "    return value if value is not None else default",
        "",
    ]
    return "\n".join(code)


def main():
    args = cli.parse_args()

    # Make sure all the type annotations in lsprotocol are resolved correctly.
    _resolve_forward_references()

    client = generate_client()
    output = args.output / "_base_client.py"
    output.write_text(client)

    server = generate_server()
    output = args.output / "_base_server.py"
    output.write_text(server)

    capabilities = generate_capabilities()
    output = args.output / "_capabilities.py"
    output.write_text(capabilities)


if __name__ == "__main__":
    main()
