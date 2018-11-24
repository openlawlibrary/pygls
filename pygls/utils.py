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
import json
import logging

logger = logging.getLogger(__name__)


def call_user_feature(base_func, method_name):
    """Wraps generic LSP features and calls user registered feature
    immediately after it.
    """
    @functools.wraps(base_func)
    def decorator(self, *args, **kwargs):
        ret_val = base_func(self, *args, **kwargs)

        try:
            user_func = self.fm.features[method_name]
            self._execute_notification(user_func, *args, **kwargs)
        except Exception:
            pass

        return ret_val

    return decorator


def has_ls_param_or_annotation(f, annotation):
    """Returns true if callable has first parameter named `ls` or type of
    annotation"""
    try:
        sig = inspect.signature(f)
        first_p = next(itertools.islice(sig.parameters.values(), 0, 1))
        return first_p.name == 'ls' or first_p.annotation is annotation
    except Exception:
        return False


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


def to_lsp_name(method_name):
    """Convert method name to LSP real name

    Example:
        text_document__did_open -> textDocument/didOpen
    """
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
    """Returns a new callable/coroutine with server as first argument."""
    if not has_ls_param_or_annotation(f, type(server)):
        return f

    if asyncio.iscoroutinefunction(f):
        return asyncio.coroutine(functools.partial(f, server))
    else:
        wrapped = functools.partial(f, server)
        if getattr(f, 'execute_in_thread', False):
            wrapped.execute_in_thread = True
        return wrapped
