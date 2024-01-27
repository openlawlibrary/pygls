"""Script to automatically generate a lanaguge client from `lsprotocol` type definitons
"""

import argparse
import inspect
import pathlib
import re
import sys
import textwrap
from typing import Optional
from typing import Type

from lsprotocol._hooks import _resolve_forward_references
from lsprotocol.types import METHOD_TO_TYPES
from lsprotocol.types import message_direction

cli = argparse.ArgumentParser(
    description="generate a base language client and server from lsprotocol types."
)
cli.add_argument(
    "-o", "--outdir", default=None, help="the directory to save the generated files to"
)


def to_snake_case(string: str) -> str:
    return "".join(f"_{c.lower()}" if c.isupper() else c for c in string)


def write_notification(method: str, notification: Type, params: Optional[Type]) -> str:
    """Write a method that sends the given notification message

    Parameters
    ----------
    method
       The notification method name

    notification
       The class representing the notification message's overall structure

    params
       The class representing the notification message's parameters

    Returns
    -------
    str
       The method definition
    """
    python_name = to_snake_case(method).replace("/", "_").replace("$_", "")

    if params is None:
        param_name = "None"
        param_mod = ""
    elif "typing" in str(params):
        param_name = str(params).replace("typing.", "")
        param_mod = ""
    else:
        param_mod, param_name = params.__module__, params.__name__
        param_mod = param_mod.replace("lsprotocol.types", "types") + "."

    return "\n".join(
        [
            f"def {python_name}(self, params: {param_mod}{param_name}) -> None:",
            f'    """Send a :lsp:`{method}` notification.',
            "",
            textwrap.indent(inspect.getdoc(notification) or "", "    "),
            '    """',
            "",
            f'    self.send_notification("{method}", params)',
            "",
        ]
    )


def get_response_type(response: Type) -> str:
    """Given a response message type, return the corresponsing result type annotation.

    Parameters
    ----------
    response
       The class describing the response message

    Returns
    -------
    str
       The type annotation to use for the response type.
    """
    # Find the response type.
    result_field = [f for f in response.__attrs_attrs__ if f.name == "result"][0]
    result = re.sub(r"<class '([\w.]+)'>", r"\1", str(result_field.type))
    result = re.sub(r"ForwardRef\('([\w.]+)'\)", r"lsprotocol.types.\1", result)
    result = result.replace("NoneType", "None")

    result = result.replace("lsprotocol.types.", "types.")
    result = result.replace("typing.", "")

    return result


def write_request(
    method: str, request: Type, params: Optional[Type], response: Type
) -> str:
    """Write a method that sends the given request

    Parameters
    ----------
    method
       The notification method name

    request
       The class representing the request message's overall structure

    params
       The class representing the request message's parameters

    response
       The class representing the respone message's overall structure

    Returns
    -------
    str
       The method definition
    """

    python_name = to_snake_case(method).replace("/", "_").replace("$_", "")

    if params is None:
        param_name = "None"
        param_mod = ""
    else:
        param_mod, param_name = params.__module__, params.__name__
        param_mod = param_mod.replace("lsprotocol.types", "types") + "."

    result_type = get_response_type(response)

    return "\n".join(
        [
            f"def {python_name}(",
            "    self,",
            f"    params: {param_mod}{param_name},",
            f"    msg_id: Optional[MsgId] = None,",
            f"    callback: Optional[Callable[[{result_type}], None]] = None,",
            f") -> asyncio.Task[{result_type}]:",
            f'    """Make a :lsp:`{method}` request.',
            "",
            textwrap.indent(inspect.getdoc(request) or "", "    "),
            '    """',
            f'    return self.send_request("{method}", params, msg_id=msg_id, callback=callback)',
            "",
        ]
    )


def generate_client() -> str:
    """Generate a base language client derived from ``lsprotocol`` type definitions.

    Returns
    -------
    str
       The generated base client.
    """
    methods = []

    for method_name, types in METHOD_TO_TYPES.items():
        # Skip any requests that come from the server.
        if message_direction(method_name) == "serverToClient":
            continue

        request, response, params, _ = types

        if response is None:
            method = write_notification(method_name, request, params)
        else:
            method = write_request(method_name, request, params, response)

        methods.append(textwrap.indent(method, "    "))

    code = [
        "# GENERATED FROM scripts/genenerate_base_lsp_classes.py -- DO NOT EDIT",
        "# flake8: noqa",
        "from __future__ import annotations",
        "",
        "import typing",
        "",
        "from pygls.client import JsonRPCClient",
        "",
        "from .protocol import LanguageServerProtocol",
        "",
        "if typing.TYPE_CHECKING:",
        "    import asyncio",
        "    from typing import Any, Callable, List, Optional, Type, Union",
        "",
        "    from lsprotocol import types",
        "",
        "    from pygls.protocol import MsgId",
        "",
        "",
        "class BaseLanguageClient(JsonRPCClient):",
        '    """Base language client."""',
        "",
        "    def __init__(",
        "        self,",
        "        *args,",
        "        protocol_cls: Type[LanguageServerProtocol] = LanguageServerProtocol,",
        "        **kwargs,",
        "    ):",
        "        super().__init__(*args, protocol_cls=protocol_cls, **kwargs)",
        "",
        *methods,
    ]
    return "\n".join(code)


def generate_server() -> str:
    """Generate a base language server derived from ``lsprotocol`` type definitions.

    Returns
    -------
    str
       The generated base server.
    """
    methods = []
    for method_name, types in METHOD_TO_TYPES.items():
        # Skip any requests that come from the client.
        if message_direction(method_name) == "clientToServer":
            continue

        request, response, params, _ = types

        if response is None:
            method = write_notification(method_name, request, params)
        else:
            method = write_request(method_name, request, params, response)

        methods.append(textwrap.indent(method, "    "))

    code = [
        "# GENERATED FROM scripts/genenerate_base_lsp_classes.py -- DO NOT EDIT",
        "# flake8: noqa",
        "from __future__ import annotations",
        "",
        "import typing",
        "",
        "from pygls.server import JsonRPCServer",
        "",
        "from .protocol import LanguageServerProtocol",
        "",
        "if typing.TYPE_CHECKING:",
        "    import asyncio",
        "    from typing import Any, Callable, List, Optional, Type",
        "",
        "    from lsprotocol import types",
        "",
        "    from pygls.protocol import MsgId",
        "",
        "",
        "class BaseLanguageServer(JsonRPCServer):",
        '    """Base language server,"""',
        "",
        "    def __init__(",
        "        self,",
        "        *args,",
        "        protocol_cls: Type[LanguageServerProtocol] = LanguageServerProtocol,",
        "        **kwargs,",
        "    ):",
        "        super().__init__(*args, protocol_cls=protocol_cls, **kwargs)",
        "",
        *methods,
    ]
    return "\n".join(code)


def main():
    args = cli.parse_args()

    # Make sure all the type annotations in lsprotocol are resolved correctly.
    _resolve_forward_references()
    client = generate_client()
    server = generate_server()

    if args.outdir is None:
        sys.stdout.write(client)
        sys.stdout.write(server)
    else:
        outdir = pathlib.Path(args.outdir)

        (outdir / "_base_client.py").write_text(client)
        (outdir / "_base_server.py").write_text(server)


if __name__ == "__main__":
    main()
