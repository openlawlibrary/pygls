##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import logging
from . import lsp

log = logging.getLogger(__name__)


class CommandAlreadyRegisteredError(Exception):
    pass


class FeatureAlreadyRegisteredError(Exception):
    pass


class OptionsValidationError(Exception):
    def __init__(self, errors=None):
        self.errors = errors or []

    def __repr__(self):
        opt_errs = '\n-'.join([e for e in self.errors])
        return f"Missing options: {opt_errs}"


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

    @property
    def features(self):
        return self._features

    @property
    def feature_options(self):
        return self._feature_options

    @property
    def commands(self):
        return self._commands

    def feature(self, *feature_names, **options):
        '''
        Decorator used to register LSP features
        Params:
            feature_name(tuple): Name of the LSP feature(s)
            options(dict): Feature options
                           E.G. triggerCharacters=['.']
        '''
        def decorator(f):
            # Add feature if not exists
            for feature_name in feature_names:
                if feature_name in self._features:
                    log.error(f'Feature {feature_name} already exists.')
                    raise FeatureAlreadyRegisteredError()

                self._features[feature_name] = f

            if options:
                self._feature_options[feature_name] = options

            log.info(f'Registered {feature_name} with options {options}')

            return f
        return decorator

    def command(self, command_name):
        '''
        Decorator used to register commands
        Params:
            command_name(str): Name of the command
        '''
        def decorator(f):
            # Validate
            if command_name.isspace():
                log.error(f'Missing command name.')
                raise OptionsValidationError('Command name is required.')

            # Add if not exists
            if command_name in self._commands:
                log.error(f'Command {command_name} already exists.')
                raise CommandAlreadyRegisteredError()

            self._commands[command_name] = f

            log.info(f'Command {command_name} is successfully registered.')

            return f

        return decorator
