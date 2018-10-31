##########################################################################
# Original work Copyright 2018 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import asyncio
import time

import mock

from pygls import utils


def test_clip_column():
    assert utils.clip_column(0, [], 0) == 0
    assert utils.clip_column(2, ['123'], 0) == 2
    assert utils.clip_column(3, ['123'], 0) == 3
    assert utils.clip_column(5, ['123'], 0) == 3
    assert utils.clip_column(0, ['\n', '123'], 0) == 0
    assert utils.clip_column(1, ['\n', '123'], 0) == 0
    assert utils.clip_column(2, ['123\n', '123'], 0) == 2
    assert utils.clip_column(3, ['123\n', '123'], 0) == 3
    assert utils.clip_column(4, ['123\n', '123'], 1) == 3


def test_debounce():
    interval = 0.1
    obj = mock.Mock()

    @utils.debounce(0.1)
    def call_m():
        obj()

    assert not obj.mock_calls

    call_m()
    call_m()
    call_m()
    assert not obj.mock_calls

    time.sleep(interval * 2)
    assert len(obj.mock_calls) == 1

    call_m()
    time.sleep(interval * 2)
    assert len(obj.mock_calls) == 2


def test_debounce_keyed_by():
    interval = 0.1
    obj = mock.Mock()

    @utils.debounce(0.1, keyed_by='key')
    def call_m(key):
        obj(key)

    assert not obj.mock_calls

    call_m(1)
    call_m(2)
    call_m(3)
    assert not obj.mock_calls

    time.sleep(interval * 2)
    obj.assert_has_calls([
        mock.call(1),
        mock.call(2),
        mock.call(3),
    ], any_order=True)
    assert len(obj.mock_calls) == 3

    call_m(1)
    call_m(1)
    call_m(1)
    time.sleep(interval * 2)
    assert len(obj.mock_calls) == 4


def test_find_parents(tmpdir):
    subsubdir = tmpdir.ensure_dir("subdir", "subsubdir")
    path = subsubdir.ensure("path.py")
    test_cfg = tmpdir.ensure("test.cfg")

    assert utils.find_parents(tmpdir.strpath, path.strpath, [
        "test.cfg"]) == [test_cfg.strpath]


def test_has_ls_param_or_annotation():
    class Temp:
        pass

    def f1(ls, a, b, c):
        pass

    def f2(temp: Temp, a, b, c):
        pass

    assert utils.has_ls_param_or_annotation(f1, None)
    assert utils.has_ls_param_or_annotation(f2, Temp)


def test_list_to_string():
    assert utils.list_to_string("string") == "string"
    assert utils.list_to_string(["a", "r", "r", "a", "y"]) == "a,r,r,a,y"


def test_merge_dicts():
    assert utils.merge_dicts(
        {'a': True, 'b': {'x': 123, 'y': {'hello': 'world'}}},
        {'a': False, 'b': {'y': [], 'z': 987}}
    ) == {'a': False, 'b': {'x': 123, 'y': [], 'z': 987}}


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
