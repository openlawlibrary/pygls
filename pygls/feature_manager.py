##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import logging
from .exceptions import CommandAlreadyRegisteredError, \
    FeatureAlreadyRegisteredError, ValidationError

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
        # Key(str): LSP feature name
        # Value(func): Feature
        self._features = {}

        # Key(str): LSP feature name
        # Value(dict): Feature options
        self._feature_options = {}

        # Key(string): Command name
        # Value(func): Command
        self._commands = {}

    def command(self, command_name):
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

            self._commands[command_name] = f

            logger.info('Command {} is successfully registered.'
                        .format(command_name))

            return f

        return decorator

    @property
    def commands(self):
        return self._commands

    def feature(self, *feature_names, **options):
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

                self._features[feature_name] = f

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
