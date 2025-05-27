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
"""This demonstrates the different ways in which server commands can be registered.
"""
from __future__ import annotations

import asyncio
import logging
import math

import attrs
from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer

server = LanguageServer("commands-server", "v1")


@server.command("random")
def random():
    """Accepts no arguments, returns a random number"""
    return 4  # https://xkcd.com/221/


@server.command("random.wrapped")
def random_wrapped(ls):
    """Accepts no arguments (but uses an injected server instance).
    Returns a random number"""
    ls.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message="running...")
    )
    return 4


@server.command("calculate.sum")
def calculate_sum(*args):
    """Using *args to accept any number of arguments"""
    logging.info("arguments: %r", args)
    return sum(args)


@server.command("calculate.sum.wrapped")
def calculate_sum_wrapped(s: LanguageServer, *args):
    """Using *args to accept any number of arguments"""
    s.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message=f"{args=}")
    )
    return calculate_sum(*args)


@server.command("calculate.pow")
def calculate_pow(x: float, n):
    """One typed, one un-typed argument"""
    logging.info("x: %r, n: %r", x, n)
    return x**n


@server.command("calculate.pow.wrapped")
def calculate_pow_wrapped(s: LanguageServer, x, n: int):
    """One typed, one un-typed argument"""
    s.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message=f"{x=}, {n=}")
    )
    return calculate_pow(x, n)


@server.command("calculate.pow.async")
async def calculate_pow_async(x: float, n):
    """One typed, one un-typed argument, async"""
    await asyncio.sleep(1)

    logging.info("x: %r, n: %r", x, n)
    return x**n


@server.command("calculate.pow.async.wrapped")
async def calculate_pow_async_wrapped(s: LanguageServer, x, n: int):
    """One typed, one un-typed argument, async"""
    s.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message=f"{x=}, {n=}")
    )
    return await calculate_pow_async(x, n)


@server.command("calculate.div")
def calculate_div(x: float, n):
    """"""
    logging.info("x: %r, n: %r", x, n)
    return x / n


@server.command("calculate.div.wrapped")
def calculate_div_wrapped(s: LanguageServer, x, n: float):
    """Using *args to accept any number of arguments"""
    s.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message=f"{x=}, {n=}")
    )
    return calculate_div(x, n)


@attrs.define
class Triangle:
    """A triangle."""

    a: float
    """Length of side a"""

    b: float
    """Length of side b"""

    c: float = attrs.field(default=0)
    """Length of side c - the hypotenuse"""


@server.command("calculate.triangle.hypotenuse")
def calculate_triangle_hypotenuse(triangle: Triangle):
    """When type annotations are given, pygls will automatically convert compatible
    values to their attrs-based representation"""
    logging.info("triangle: %r", triangle)

    triangle.c = math.sqrt(triangle.a**2 + triangle.b**2)
    return triangle


@server.command("calculate.triangle.hypotenuse.wrapped")
def calculate_triangle_hypotenuse_wrapped(ls: LanguageServer, triangle: Triangle):
    """When type annotations are given, pygls will automatically convert compatible
    values to their attrs-based representation"""
    ls.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message=f"{triangle=}")
    )
    return calculate_triangle_hypotenuse(triangle)


@server.command("calculate.untyped.hypotenuse")
def calculate_untyped_hypotenuse(tri):
    """Calculate the hypotenuse of a right-angled triangle"""
    logging.info("tri: %r", tri)

    a = tri["a"]
    b = tri["b"]
    c = math.sqrt(a**2 + b**2)
    return dict(a=a, b=b, c=c)


@server.command("calculate.untyped.hypotenuse.wrapped")
def calculate_untyped_hypotenuse_wrapped(ls: LanguageServer, tri):
    """Calculate the hypotenuse of a right-angled triangle"""
    ls.window_log_message(
        types.LogMessageParams(type=types.MessageType.Info, message=f"{tri=}")
    )
    return calculate_untyped_hypotenuse(tri)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
