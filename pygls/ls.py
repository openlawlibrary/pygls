'''
This module contains all generic language server features.

'''

import logging
import functools
import inspect

from itertools import zip_longest

from .workspace import Workspace
from . import lsp, _utils, uris
from .decorators import call_user_features
from .feature_manager import FeatureManager

from .jsonrpc.json_rpc_server import JsonRPCServer

log = logging.getLogger(__name__)


class LSMeta(type):
    """
    A metaclass to dynamically add decorators to generic LSP features.

    EXAMPLE:
    If `lsp.TEXT_DOC_DID_OPEN` is registered, it will be called after the
    same method from base_features
    """

    def __new__(self, cls_name, cls_bases, cls):
        # Skip for classes that are derived from LanguageServer
        if cls_name == 'LanguageServer':
            for attr_name, attr_val in cls.items():
                # Add wrappers only for "public" methods
                # TODO: Find better way to filter methods
                skip_methods = ['register', 'get_configuration']

                if callable(attr_val) and not attr_name.startswith('_') and \
                        attr_name not in skip_methods:

                    method_name = _utils.to_lsp_name(attr_name)
                    cls[attr_name] = call_user_features(attr_val, method_name)

        return super(LSMeta, self).__new__(
            self, cls_name, cls_bases, cls)


class LanguageServer(JsonRPCServer, metaclass=LSMeta):
    '''
    Class with implemented generic LSP features
    https://github.com/Microsoft/language-server-protocol/blob/master/versions/protocol-1-x.md

    Attributes:
        workspace(Workspace): Object that represents workspace
        workspace_folders(dict): Multi-root workspace's folders
        _shutdown(bool): True if client sent shutdown notification
        _base_features(dict): Registered generic LSP features
    '''

    def __init__(self):
        super(LanguageServer, self).__init__()

        self.fm = FeatureManager()

        self._shutdown = False

        self.workspace = None
        self.workspace_folders = {}

        self._base_features = {}

        self._setup_base_features()

    @property
    def features(self):
        return self.fm.features

    @property
    def feature_options(self):
        return self.fm.feature_options

    @property
    def commands(self):
        return self.fm.commands

    @property
    def base_features(self):
        return self._base_features

    def register(self, feature_name, **options):
        return self.fm.register(feature_name, **options)

    def __getitem__(self, item):
        try:
            # if self._shutdown and item != 'exit':
            #     # exit is the only allowed method during shutdown
            #     log.debug("Ignoring non-exit method during shutdown: %s", item)
            #     raise KeyError

            try:
                # Look at base features
                method = self.base_features[item]
            except:
                # Look at user defined features
                method = self.features[item]

            @functools.wraps(method)
            def handler(params):
                args = inspect.getargspec(method)[0]
                if 'ls' in args:
                    return method(ls=self, **(params or {}))
                else:
                    return method(**(params or {}))

            return handler
        except:
            # log
            raise KeyError()

    def _setup_base_features(self):
        # General
        self._base_features[lsp.INITIALIZE] = self.initialize
        self._base_features[lsp.INITIALIZED] = self.initialized
        self._base_features[lsp.SHUTDOWN] = self.shutdown
        self._base_features[lsp.EXIT] = self.exit

        # Workspace
        self._base_features[lsp.EXECUTE_COMMAND] = self.execute_command
        self._base_features[lsp.DID_CHANGE_WORKSPACE_FOLDERS] = self.workspace__did_change_workspace_folders
        self._base_features[lsp.DID_CHANGE_CONFIGURATION] = self.workspace__did_change_configuration

        # Text Synchronization
        self._base_features[lsp.TEXT_DOC_DID_OPEN] = self.text_document__did_open
        self._base_features[lsp.TEXT_DOC_DID_CHANGE] = self.text_document__did_change
        self._base_features[lsp.TEXT_DOC_DID_CLOSE] = self.text_document__did_close
        self._base_features[lsp.TEXT_DOC_DID_SAVE] = self.text_document__did_save

    def _capabilities(self, client_capabilities):
        '''
            Server capabilities depends on registered features
            TODO: It should depend on a client capabilities also
        '''
        server_capabilities = lsp.ServerCapabilities(self)

        # Convert to dict for json serialization
        sc_dict = _utils.to_dict(server_capabilities)

        log.info(f'Server capabilities: {sc_dict}')

        return sc_dict

    def initialize(self, processId=None, rootUri=None, rootPath=None,
                   initializationOptions=None, **_kwargs):

        log.debug(
            f'Language server initialized with {processId} {rootUri} {rootPath} {initializationOptions}')

        if rootUri is None:
            rootUri = uris.from_fs_path(
                rootPath) if rootPath is not None else ''

        self.workspace = Workspace(rootUri, self._endpoint)

        workspace_folders = _kwargs.get('workspaceFolders', [])
        for folder in workspace_folders:
            self.workspace_folders[folder['uri']] = folder

        client_capabilities = _kwargs.get('capabilities', {})

        return {'capabilities': self._capabilities(client_capabilities)}

    def initialized(self):
        pass

    def shutdown(self, **_kwargs):
        self._shutdown = True

    def exit(self, **_kwargs):
        self._endpoint.shutdown()
        self._jsonrpc_stream_reader.close()
        self._jsonrpc_stream_writer.close()

    def text_document__did_close(self, textDocument=None, **_kwargs):
        self.workspace.rm_document(textDocument['uri'])

    def text_document__did_open(self, textDocument=None, **_kwargs):
        self.workspace.put_document(doc_uri=textDocument['uri'],
                                    source=textDocument['text'],
                                    version=textDocument.get('version'))

    def text_document__did_change(self, contentChanges=None,
                                  textDocument=None, **_kwargs):

        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )

    def text_document__did_save(self, textDocument=None, **_kwargs):
        pass

    def text_document__rename(self, textDocument=None, position=None,
                              newName=None, **_kwargs):
        return self.rename(textDocument['uri'], position, newName)

    def workspace__did_change_configuration(self, settings=None):
        pass

    def execute_command(self, command=None, arguments=None):
        try:
            return self.commands[command](self, arguments)
        except:
            pass

    def workspace__did_change_workspace_folders(self, event=None):
        added_folders = event['added'] or []
        removed_folders = event['removed'] or []

        for for_add, for_remove in zip_longest(added_folders, removed_folders):
            # Add folder
            try:
                self.workspace_folders[for_add['uri']] = for_add
            except:
                pass
            # Remove folder
            try:
                del self.workspace_folders[for_remove['uri']]
            except:
                pass

    def get_configuration(self, params, callback):
        def configuration(future):
            return callback(future.result())

        result = self._endpoint.request(
            lsp.CONFIGURATION, params).result(timeout=5)
        future.add_done_callback(configuration)

        return
