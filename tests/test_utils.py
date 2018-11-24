##########################################################################
# Original work Copyright 2018 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import asyncio

from pygls import utils


def test_has_ls_param_or_annotation():
    class Temp:
        pass

    def f1(ls, a, b, c):
        pass

    def f2(temp: Temp, a, b, c):
        pass

    assert utils.has_ls_param_or_annotation(f1, None)
    assert utils.has_ls_param_or_annotation(f2, Temp)


def test_to_lsp_name():
    f_name = 'text_document__did_open'
    name = 'textDocument/didOpen'

    assert utils.to_lsp_name(f_name) == name


def test_wrap_with_server_async():
    class Server:
        pass

    async def f(ls):
        assert isinstance(ls, Server)

    wrapped = utils.wrap_with_server(f, Server())
    assert asyncio.iscoroutinefunction(wrapped)


def test_wrap_with_server_sync():
    class Server:
        pass

    def f(ls):
        assert isinstance(ls, Server)

    wrapped = utils.wrap_with_server(f, Server())
    wrapped()


def test_wrap_with_server_thread():
    class Server:
        pass

    def f(ls):
        assert isinstance(ls, Server)
    f.execute_in_thread = True

    wrapped = utils.wrap_with_server(f, Server())
    assert wrapped.execute_in_thread is True
