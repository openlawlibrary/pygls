##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import logging
from typing import Callable, Dict

from .exceptions import (CommandAlreadyRegisteredError,
                         FeatureAlreadyRegisteredError, ValidationError)
from .utils import wrap_with_server

logger = logging.getLogger(__name__)


class FeatureManager:
    """A class for managing server features.

    Attributes:
        _builtin_features(dict): Predefined set of lsp methods
        _feature_options(dict): Registered feature's options
        _features(dict): Registered features
        _commands(dict): Registered commands
        server(LanguageServer): Reference to the language server
                                If passed, server will be passed to registered
                                features/commands with first parameter:
                                    1. ls - parameter naming convention
                                    2. name: LanguageServer - add typings
    """

    def __init__(self, server=None):
        self._builtin_features = {}
        self._feature_options = {}
        self._features = {}
        self._commands = {}
        self.server = server

    def add_builtin_feature(self, feature_name: str, func: Callable) -> None:
        """Registers builtin (predefined) feature."""
        self._builtin_features[feature_name] = func
        logger.info('Registered builtin feature {}'.format(feature_name))

    @property
    def builtin_features(self) -> Dict:
        """Returns server builtin features."""
        return self._builtin_features

    def command(self, command_name: str) -> Callable:
        """Decorator used to register custom commands.

        Example:
            @ls.command('myCustomCommand')
        """
        def decorator(f):
            # Validate
            if command_name.isspace():
                logger.error('Missing command name.')
                raise ValidationError('Command name is required.')

            # Check if not already registered
            if command_name in self._commands:
                logger.error('Command {} already registered.'
                             .format(command_name))
                raise CommandAlreadyRegisteredError()

            self._commands[command_name] = wrap_with_server(f, self.server)

            logger.info('Command {} is successfully registered.'
                        .format(command_name))

            return f
        return decorator

    @property
    def commands(self) -> Dict:
        """Returns registered custom commands."""
        return self._commands

    def feature(self, feature_name: str, **options: Dict) -> Callable:
        """Decorator used to register LSP features.

        Example:
            @ls.feature('textDocument/completion', triggerCharacters=['.'])
        """
        def decorator(f):
            # Validate
            if feature_name.isspace():
                logger.error('Missing feature name.')
                raise ValidationError('Feature name is required.')

            # Add feature if not exists
            if feature_name in self._features:
                logger.error('Feature {} already registered.'
                             .format(feature_name))
                raise FeatureAlreadyRegisteredError()

            self._features[feature_name] = wrap_with_server(f, self.server)

            if options:
                self._feature_options[feature_name] = options

            logger.info('Registered {} with options {}'
                        .format(feature_name, options))

            return f
        return decorator

    @property
    def feature_options(self) -> Dict:
        """Returns feature options for registered features."""
        return self._feature_options

    @property
    def features(self) -> Dict:
        """Returns registered features"""
        return self._features
