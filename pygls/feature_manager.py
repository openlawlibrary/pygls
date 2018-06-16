from . import lsp


class FeatureManager(object):
    '''
    Class for registering user defined features

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
        def decorator(f):
            # Register commands separately
            if feature_name is lsp.REGISTER_COMMAND:
                self._commands[options['name']] = f
            else:
                self._features[feature_name] = f

            if options:
                self._feature_options[feature_name] = options

            return f
        return decorator
