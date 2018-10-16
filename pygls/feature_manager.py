##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import logging

from .exceptions import CommandAlreadyRegisteredError, \
    FeatureAlreadyRegisteredError, ValidationError
from .utils import wrap_with_server

logger = logging.getLogger(__name__)


class FeatureManager(object):
    '''
    Class for registering user defined features.

    Attributes:
        _features(dict): Registered features
        _feature_options(dict): Registered feature's options
        _commands(dict): Registered commands
    '''

    def __init__(self):
        self._builtin_features = {}
        self._feature_options = {}
        self._features = {}
        self._command_options = {}
        self._commands = {}

    def add_builtin_feature(self, feature_name: str, func):
        '''
        Register builtin (predefined) features
        '''
        self._builtin_features[feature_name] = func
        logger.info('Registered builtin feature {}'.format(feature_name))

    @property
    def builtin_features(self):
        return self._builtin_features

    def command(self, server, command_name, **options):
        '''
        Decorator used to register commands
        Params:
            command_name(str): Name of the command
        '''
        def decorator(f):
            # Validate
            if command_name.isspace():
                logger.error('Missing command name.')
                raise ValidationError('Command name is required.')

            # Add if not exists
            if command_name in self._commands:
                logger.error('Command {} already exists.'
                             .format(command_name))
                raise CommandAlreadyRegisteredError()

            self._commands[command_name] = wrap_with_server(f, server)

            if options:
                self._command_options[command_name] = options

            logger.info('Command {} is successfully registered.'
                        .format(command_name))

            return f

        return decorator

    @property
    def command_options(self):
        return self._command_options

    @property
    def commands(self):
        return self._commands

    def feature(self, server, *feature_names, **options):
        '''
        Decorator used to register LSP features
        Params:
            *feature_names(tuple): Name of the LSP feature(s)
            **options(dict): Feature options
                E.G. triggerCharacters=['.']
        '''
        def decorator(f):
            # Add feature if not exists
            for feature_name in feature_names:
                if feature_name in self._features:
                    logger.error('Feature {} already exists.'
                                 .format(feature_name))
                    raise FeatureAlreadyRegisteredError()

                self._features[feature_name] = wrap_with_server(f, server)

            if options:
                self._feature_options[feature_name] = options

            logger.info('Registered {} with options {}'
                        .format(feature_name, options))

            return f
        return decorator

    @property
    def feature_options(self):
        return self._feature_options

    @property
    def features(self):
        return self._features
