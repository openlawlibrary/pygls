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

    def register(self, feature_name, **options):
        '''
        Decorator used to register user defined features
        Params:
            feature_name(str): Name of the LSP feature or command
                               EG: 'textDocument/completions'
            options(dict): Options for feature or command
                           EG: triggerCharacters=['.']
        '''
        log.info(f'Registering {feature_name} with options {options}')

        def decorator(f):
            # Validate options
            errors = self._validate_options(feature_name, options)

            if len(errors) > 0:
                log.error(f'Validation errors: {errors}')
                raise OptionsValidationError(errors=errors)

            # Register
            if feature_name is lsp.REGISTER_COMMAND:
                # commands
                cmd_name = options['name']

                if cmd_name in self._commands:
                    log.error(f'Command {cmd_name} already exists.')
                    raise CommandAlreadyRegisteredError()

                self._commands[cmd_name] = f
            else:
                # lsp features
                if feature_name in self._features:
                    log.error(f'Feature {feature_name} already exists.')
                    raise FeatureAlreadyRegisteredError()

                self._features[feature_name] = f

            if options:
                self._feature_options[feature_name] = options

            return f
        return decorator

    def _validate_options(self, f_name, opts):
        errors = []
        if f_name is lsp.REGISTER_COMMAND:
            if 'name' not in opts:
                errors.append('name')

        return errors
