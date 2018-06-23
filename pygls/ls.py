import logging
import functools
import inspect

from itertools import zip_longest

from .workspace import Workspace
from . import lsp, _utils, uris
from .decorators import call_user_feature
from .feature_manager import FeatureManager

from .jsonrpc.json_rpc_server import JsonRPCServer

log = logging.getLogger(__name__)


class LSMeta(type):
    """
    Metaclass for language server.
    Purpose:
        Wrap LS base methods with decorator which will call the user registered
        method with the same LSP name.
    """

    def __new__(self, cls_name, cls_bases, cls):
        # Skip for classes that are derived from LanguageServer
        if cls_name == 'LanguageServer':

            for attr_name, attr_val in cls.items():
                if callable(attr_val) and attr_name.startswith('gf_'):
                    method_name = _utils.to_lsp_name(attr_name[3:])
                    cls[attr_name] = call_user_feature(attr_val, method_name)

                    log.debug(f"Added decorator for lsp method: {attr_name}")

        return super().__new__(
            self, cls_name, cls_bases, cls)


class LanguageServer(JsonRPCServer, metaclass=LSMeta):
    '''
    Class with implemented generic LSP features
    https://github.com/Microsoft/language-server-protocol/blob/master/versions/protocol-1-x.md

    Attributes:
        fm(FeatureManager): Object which is responsible for
                            registering features and commands
        workspace(Workspace): Object that represents workspace
        _shutdown(bool): True if client sent shutdown notification
        _generic_features(dict): Registered generic LSP features

    Generic LSP features starts with `gf_` (e.g. gf_text_document__did_open).
    Also convention is to use underscores in generic LSP feature names.
    E.G. text_document__did_open is dinamically registered as
         textDocument/didOpen
    '''

    def __init__(self):
        super().__init__()

        self.fm = FeatureManager()
        self.workspace = None
        self._shutdown = False
        self._generic_features = {}

        self._register_generic_features()

    @property
    def features(self):
        '''
        Returns registered features.
        '''
        return self.fm.features

    @property
    def feature_options(self):
        '''
        Returns options for registered features.
        '''
        return self.fm.feature_options

    @property
    def commands(self):
        '''
        Returns registered commands.
        '''
        return self.fm.commands

    @property
    def generic_features(self):
        '''
        Returns generic LSP features.
        '''
        return self._generic_features

    def feature(self, feature_name, **options):
        '''
        Registers a LSP feature (delegating to FeatureManager).

        Args:
            feature_name(str): Name of the feature to register
                NOTE: All possible LSP features are listed in lsp module
            options(dict): Options for registered feature
                E.G. triggerCharacters=['.']
        '''
        return self.fm.feature(feature_name, **options)

    def command(self, command_name):
        '''
        Registers new command (delegating to FeatureManager).

        Args:
            command_name(str): Name of the command to register
        '''
        return self.fm.command(command_name)

    def __getitem__(self, item):
        '''
        Finds and returns either generic or user registered feature.

        Args:
            item(str): LSP method name (E.G. textDocument/didOpen)
        '''
        try:
            # if self._shutdown and item != 'exit':
            #     # exit is the only allowed method during shutdown
            #     log.debug(f"Ignoring non-exit method during shutdown.")
            #     raise KeyError

            try:
                # Look at base features
                method = self.generic_features[item]
                log.info(f'Found {method} in base features')
            except:
                # Look at user defined features
                method = self.features[item]
                log.info(f'Found {method} in user features')

            @functools.wraps(method)
            def handler(params):
                '''
                If registered feature contains `ls` (LanguageServer) instance
                as first parameter, it will be passed.
                Although `ls` instance exists in outer scope (@ls.feature),
                this will allow easier unit testing.
                '''
                args = inspect.getargspec(method)[0]
                if 'ls' in args:
                    log.debug(f"Invoking {method.__name__} with 'ls' param.")
                    return method(ls=self, **(params or {}))
                else:
                    return method(**(params or {}))

            return handler
        except:
            # log
            raise KeyError()

    def _register_generic_features(self):
        '''
        Registers generic LSP features from this class.
        Convention for feature names iss described in class doc.
        '''
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and name.startswith('gf_'):
                lsp_name = _utils.to_lsp_name(name[3:])
                self._generic_features[lsp_name] = attr
                log.debug(f"Registered generic feature {name}")

    def _capabilities(self, client_capabilities):
        '''
            Server capabilities depends on registered features.
            TODO: It should depend on a client capabilities as well.

            Args:
                client_capabilities(dict): Capabilities that client supports
        '''
        server_capabilities = lsp.ServerCapabilities(self)

        # Convert to dict for json serialization
        sc_dict = _utils.to_dict(server_capabilities)

        log.info(f'Server capabilities: {sc_dict}')

        return sc_dict

    def gf_initialize(
            self,
            processId=None,
            rootUri=None,
            rootPath=None,
            initializationOptions=None,
            **_kwargs
    ):
        '''
        This method is called once, after the client activates server.
        It will compute and return server capabilities based on
        registered features.
        '''

        log.debug(
            f'Language server initialized with {processId} \
                                               {rootUri} \
                                               {rootPath} \
                                               {initializationOptions}')

        if rootUri is None:
            rootUri = uris.from_fs_path(
                rootPath) if rootPath is not None else ''

        self.workspace = Workspace(rootUri, self._endpoint)

        workspace_folders = _kwargs.get('workspaceFolders') or []
        for folder in workspace_folders:
            self.workspace.add_folder(folder)

        client_capabilities = _kwargs.get('capabilities', {})

        return {'capabilities': self._capabilities(client_capabilities)}

    def gf_initialized(self):
        '''
        Notification that everything works well.
        '''
        pass

    def gf_shutdown(self, **_kwargs):
        '''
        Request from client which asks server to shutdown.
        '''
        self._shutdown = True

    def gf_exit(self, **_kwargs):
        '''
        Stops the server process. Should only work if _shutdown flag is True
        '''
        self._endpoint.shutdown()
        self._jsonrpc_stream_reader.close()
        self._jsonrpc_stream_writer.close()

    def gf_text_document__did_open(self, textDocument=None, **_kwargs):
        '''
        Puts document to workspace.
        '''
        self.workspace.put_document(doc_uri=textDocument['uri'],
                                    source=textDocument['text'],
                                    version=textDocument.get('version'))

    def gf_text_document__did_close(self, textDocument=None, **_kwargs):
        '''
        Removes document from workspace.
        '''
        self.workspace.rm_document(textDocument['uri'])

    def gf_text_document__did_change(self, contentChanges=None,
                                     textDocument=None, **_kwargs):
        '''
        Updates document's content.
        (Incremental (from server capabilities); not configurable for now)
        '''
        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )

    def gf_text_document__did_save(self, textDocument=None, **_kwargs):
        '''
        Does nothing.
        '''
        pass

    def gf_text_document__rename(
        self,
        textDocument=None,
        position=None,
        newName=None,
        **_kwargs
    ):
        '''
        Changes document name in the workspace
        '''
        return self.rename(textDocument['uri'], position, newName)

    def gf_workspace__execute_command(self, command=None, arguments=None):
        '''
        Executes commands with passed arguments and returns a value.
        '''
        try:
            return self.commands[command](self, arguments)
        except Exception as ex:
            ex_msg = repr(ex)
            log.error(f"Error while executing command '{command}': {ex_msg}")
            self.workspace.show_message(
                f"Error while executing command: {ex_msg}")

    def gf_workspace__did_change_workspace_folders(self, event=None):
        '''
        Adds/Removes folders from the workspace
        '''
        log.info(f'Workspace folders changed: {event}')

        added_folders = event['added'] or []
        removed_folders = event['removed'] or []

        for f_add, f_remove in zip_longest(added_folders, removed_folders):
            if f_add:
                self.workspace.add_folder(f_add)
            if f_remove:
                self.workspace.remove_folder(f_remove)

    def get_configuration(self, config_params, callback):
        '''
        Gets the configuration settings from the client.
        This method is asynchronous and the callback function
        will be called after the response is received.

        Args:
            config_params(dict): ConfigurationParams from lsp specs
            callback(callable): Callabe which will be called after
                response from the client is received
        '''
        def configuration(future):
            result = future.result()
            log.info(f'Configuration for {config_params} received: {result}')
            return callback(result)

        future = self._endpoint.request(
            lsp.WORKSPACE_CONFIGURATION, config_params)
        future.add_done_callback(configuration)
