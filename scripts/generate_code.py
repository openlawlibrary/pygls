"""Script to automatically generate a lanaguge client and server from `lsprotocol`
type definitons."""

import argparse
import inspect
import pathlib
import re
import textwrap
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type

from lsprotocol._hooks import _resolve_forward_references
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
    result = re.sub(r"<class '([\w.]+)'>", r"\1", str(result_field.type))
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


if __name__ == "__main__":
    main()
