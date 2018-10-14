##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import asyncio
import functools
import inspect
import itertools
import logging
import os
import threading
import json

log = logging.getLogger(__name__)


def call_user_feature(base_func, method_name):
    '''
    Wraps generic LSP features and calls user registered
    feature immediately after it.
    '''
    @functools.wraps(base_func)
    def decorator(self, *args, **kwargs):
        ret_val = base_func(self, *args, **kwargs)

        try:
            user_func = self.fm.features[method_name]
            self._execute_notification(user_func, *args, **kwargs)
        except:
            pass

        return ret_val

    return decorator


def clip_column(column, lines, line_number):
    # Normalize the position as per the LSP
    # that accepts character positions >line length
    # https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md#position
    max_column = len(lines[line_number].rstrip('\r\n')
                     ) if len(lines) > line_number else 0
    return min(column, max_column)


def debounce(interval_s, keyed_by=None):
    '''Debounce calls to this function until interval_s seconds have passed.'''
    def wrapper(func):
        timers = {}
        lock = threading.Lock()

        @functools.wraps(func)
        def debounced(*args, **kwargs):
            call_args = inspect.getcallargs(func, *args, **kwargs)
            key = call_args[keyed_by] if keyed_by else None

            def run():
                with lock:
                    del timers[key]
                return func(*args, **kwargs)

            with lock:
                old_timer = timers.get(key)
                if old_timer:
                    old_timer.cancel()

                timer = threading.Timer(interval_s, run)
                timers[key] = timer
                timer.start()
        return debounced
    return wrapper


def find_parents(root, path, names):
    '''Find files matching the given names relative to the given path.

    Args:
        path (str): The file path to start searching up from.
        names (List[str]): The file/directory names to look for.
        root (str): The directory at which to stop recursing upwards.

    Note:
        The path MUST be within the root.
    '''
    if not root:
        return []

    if not os.path.commonprefix((root, path)):
        log.warning('Path {} not in {}'.format(path, root))
        return []

    # Split the relative by directory, generate all the parent directories,
    # then check each of them.
    # This avoids running a loop that has different base-cases for unix/windows
    # e.g. /a/b and /a/b/c/d/e.py -> ['/a/b', 'c', 'd']
    dirs = [root] + \
        os.path.relpath(os.path.dirname(path), root).split(os.path.sep)

    # Search each of /a/b/c, /a/b, /a
    while dirs:
        search_dir = os.path.join(*dirs)
        existing = list(
            filter(os.path.exists,
                   [os.path.join(search_dir, n) for n in names]))
        if existing:
            return existing
        dirs.pop()

    # Otherwise nothing
    return []


def format_docstring(contents):
    '''Python doc strings come in a number of formats, but LSP wants markdown.

    Until we can find a fast enough way of discovering and parsing each format,
    we can do a little better by at least preserving indentation.
    '''
    contents = contents.replace('\t', u'\u00A0' * 4)
    contents = contents.replace('  ', u'\u00A0' * 2)
    contents = contents.replace('*', '\\*')
    return contents


def has_ls_param_or_annotation(f, annotation):
    try:
        sig = inspect.signature(f)
        first_p = next(itertools.islice(sig.parameters.values(), 0, 1))
        return first_p.name == 'ls' or first_p.annotation is annotation
    except:
        return False


def list_to_string(value):
    return ','.join(value) if isinstance(value, list) else value


def merge_dicts(dict_a, dict_b):
    '''Recursively merge dictionary b into dictionary a.

    If override_nones is True, then
    '''
    def _merge_dicts_(a, b):
        for key in set(a.keys()).union(b.keys()):
            if key in a and key in b:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    yield (key, dict(_merge_dicts_(a[key], b[key])))
                elif b[key] is not None:
                    yield (key, b[key])
                else:
                    yield (key, a[key])
            elif key in a:
                yield (key, a[key])
            elif b[key] is not None:
                yield (key, b[key])
    return dict(_merge_dicts_(dict_a, dict_b))


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


def to_lsp_name(method_name):
    '''
    Convert method name to LSP real name
    EXAMPLE:
    text_document__did_open -> textDocument/didOpen
    '''
    method_name = method_name.replace('__', '/')
    m_chars = list(method_name)
    m_replaced = []

    for i, ch in enumerate(m_chars):
        if ch is '_':
            continue

        if m_chars[i-1] is '_':
            m_replaced.append(ch.capitalize())
            continue

        m_replaced.append(ch)

    return ''.join(m_replaced)


def wrap_with_server(f, server):
    if not has_ls_param_or_annotation(f, type(server)):
        return f

    if asyncio.iscoroutinefunction(f):
        return asyncio.coroutine(functools.partial(f, server))
    else:
        return functools.partial(f, server)
