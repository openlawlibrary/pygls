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
from __future__ import annotations

import asyncio
import functools
import inspect
import itertools
import logging
import typing
from typing import Any
from typing import Callable
from typing import Optional
from typing import get_type_hints

import cattrs

from pygls.constants import ATTR_COMMAND_TYPE
from pygls.constants import ATTR_EXECUTE_IN_THREAD
from pygls.constants import ATTR_FEATURE_TYPE
from pygls.constants import ATTR_REGISTERED_NAME
from pygls.constants import ATTR_REGISTERED_TYPE
from pygls.constants import PARAM_LS
from pygls.exceptions import CommandAlreadyRegisteredError
from pygls.exceptions import FeatureAlreadyRegisteredError
from pygls.exceptions import ThreadDecoratorError
from pygls.exceptions import ValidationError

if typing.TYPE_CHECKING:
    from . import JsonRPCHandler


def assign_help_attrs(f, reg_name, reg_type):
    setattr(f, ATTR_REGISTERED_NAME, reg_name)
    setattr(f, ATTR_REGISTERED_TYPE, reg_type)


def assign_thread_attr(f):
    setattr(f, ATTR_EXECUTE_IN_THREAD, True)


def get_help_attrs(f):
    return getattr(f, ATTR_REGISTERED_NAME, None), getattr(
        f, ATTR_REGISTERED_TYPE, None
    )


def has_ls_param_or_annotation(f, annotation):
    """Returns true if callable has first parameter named `ls` or type of
    annotation"""
    try:
        sig = inspect.signature(f)
        first_p = next(itertools.islice(sig.parameters.values(), 0, 1))
        return first_p.name == PARAM_LS or get_type_hints(f)[first_p.name] == annotation
    except Exception:
        return False


def is_thread_function(f):
    return getattr(f, ATTR_EXECUTE_IN_THREAD, False)


def wrap_with_handler(f, handler):
    """Returns a new callable/coroutine with handler as first argument."""
    if not has_ls_param_or_annotation(f, type(handler)):
        return f

    if asyncio.iscoroutinefunction(f):

        async def wrapped(*args, **kwargs):
            return await f(handler, *args, **kwargs)

    else:
        wrapped = functools.partial(f, handler)
        if is_thread_function(f):
            assign_thread_attr(wrapped)

    return wrapped


class FeatureManager:
    """A class for managing server features."""

    def __init__(
        self,
        converter: cattrs.Converter,
        logger: Optional[logging.Logger] = None,
    ):
        self.builtin_features = {}
        """Features that are internal to pygls."""

        self.user_features = {}
        """Features provided by the user."""

        self.user_options = {}
        """Additional options for features provided by the user."""

        self.commands = {}
        """Custom commands provided by the user."""

        self.converter = converter
        """The converter instance to use"""

        self.logger = logger or logging.getLogger(__name__)
        """The logger instance to use"""

    def add_builtin_feature(self, feature_name: str, func: Callable) -> None:
        """Registers builtin (predefined) feature."""
        self.builtin_features[feature_name] = func
        self.logger.debug("Registered builtin feature %s", feature_name)

    def command(self, handler: JsonRPCHandler, command_name: str) -> Callable:
        """Decorator used to register custom commands.

        Example:
            @ls.command('myCustomCommand')
        """

        def decorator(f):
            # Validate
            if command_name is None or command_name.strip() == "":
                self.logger.error("Missing command name.")
                raise ValidationError("Command name is required.")

            # Check if not already registered
            if command_name in self.commands:
                self.logger.error('Command "%s" is already registered.', command_name)
                raise CommandAlreadyRegisteredError(command_name)

            assign_help_attrs(f, command_name, ATTR_COMMAND_TYPE)

            wrapped = wrap_with_handler(f, handler)

            # Assign help attributes for thread decorator
            assign_help_attrs(wrapped, command_name, ATTR_COMMAND_TYPE)

            self.commands[command_name] = wrapped

            self.logger.debug('Command "%s" is successfully registered.', command_name)

            return f

        return decorator

    def feature(
        self,
        handler: JsonRPCHandler,
        feature_name: str,
        options: Optional[Any] = None,
        **kwargs,
    ) -> Callable:
        """Decorator used to register LSP features."""

        def decorator(f):
            # Validate
            if feature_name is None or feature_name.strip() == "":
                self.logger.error("Missing feature name.")
                raise ValidationError("Feature name is required.")

            # Add feature if not exists
            if feature_name in self.user_features:
                self.logger.error('Feature "%s" is already registered.', feature_name)
                raise FeatureAlreadyRegisteredError(feature_name)

            assign_help_attrs(f, feature_name, ATTR_FEATURE_TYPE)

            wrapped = wrap_with_handler(f, handler)
            # Assign help attributes for thread decorator
            assign_help_attrs(wrapped, feature_name, ATTR_FEATURE_TYPE)

            opts = {}
            if options is not None:
                opts = self.converter.unstructure(options)

            user_options = {**opts, **kwargs}
            if len(user_options) > 0:
                self.user_options[feature_name] = user_options

            self.user_features[feature_name] = wrapped
            self.logger.debug(
                'Registered "%s" with options "%s"', feature_name, user_options
            )

            return f

        return decorator

    def thread(self) -> Callable:
        """Decorator that mark function to execute it in a thread."""

        def decorator(f):
            if asyncio.iscoroutinefunction(f):
                raise ThreadDecoratorError(
                    f'Thread decorator cannot be used with async functions "{f.__name__}"'
                )

            # Allow any decorator order
            try:
                reg_name = getattr(f, ATTR_REGISTERED_NAME)
                reg_type = getattr(f, ATTR_REGISTERED_TYPE)

                if reg_type is ATTR_FEATURE_TYPE:
                    assign_thread_attr(self.user_features[reg_name])
                elif reg_type is ATTR_COMMAND_TYPE:
                    assign_thread_attr(self.commands[reg_name])

            except AttributeError:
                assign_thread_attr(f)

            return f

        return decorator
