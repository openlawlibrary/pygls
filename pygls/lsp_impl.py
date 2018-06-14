'''
This module contains all generic language server features.

'''

import logging
from itertools import zip_longest

from .workspace import Workspace
from . import lsp, _utils, uris

log = logging.getLogger(__name__)


LINT_DEBOUNCE_S = 0.5  # 500 ms


class LSPBase(object):

    def __init__(self):
        self.workspace = None
        self.workspace_folders = {}

        self._shutdown = False

        self._base_features = {}
        self._setup_base_features()

        self._features = {}
        self._feature_options = {}

        self._commands = {}

    def register(self, feature_name, **options):
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

    def _setup_base_features(self):
        # General
        self._base_features[lsp.INITIALIZE] = self.initialize
        self._base_features[lsp.INITIALIZED] = self.initialized
        # self._base_features[lsp.SHUTDOWN] = self.m_shutdown
        # self._base_features[lsp.EXIT] = self.m_exit

        # Workspace
        self._base_features[lsp.EXECUTE_COMMAND] = self.execute_command
        self._base_features[lsp.DID_CHANGE_WORKSPACE_FOLDERS] = self.workspace__did_change_workspace_folders
        self._base_features[lsp.DID_CHANGE_CONFIGURATION] = self.workspace__did_change_configuration

        # Text Synchronization
        self._base_features[lsp.TEXT_DOC_DID_OPEN] = self.text_document__did_open
        self._base_features[lsp.TEXT_DOC_DID_CHANGE] = self.text_document__did_change
        self._base_features[lsp.TEXT_DOC_DID_CLOSE] = self.text_document__did_close
        self._base_features[lsp.TEXT_DOC_DID_SAVE] = self.text_document__did_save

    def capabilities(self):
        '''
        We should create server capabilities based on registered features
        and client capabilities
        EG:
            if lsp.CODE_ACTION in self._features
            and client supports it
        '''
        server_capabilities = {
            'codeActionProvider': True,
            'codeLensProvider': {
                'resolveProvider': True,  # We may need to make this configurable
            },
            'completionProvider': {
                'resolveProvider': True,  # We know everything ahead of time
                'triggerCharacters': ['.']
            },
            'documentFormattingProvider': True,
            'documentHighlightProvider': True,
            'documentRangeFormattingProvider': True,
            'documentSymbolProvider': True,
            'definitionProvider': True,
            'executeCommandProvider': {
                'commands': list(self._commands.keys())
            },
            'hoverProvider': True,
            'referencesProvider': True,
            'renameProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            'textDocumentSync': lsp.TextDocumentSyncKind.INCREMENTAL,
            'workspace': {
                'workspaceFolders': {
                    'supported': True,
                    'changeNotifications': True
                }
            }
        }
        log.info('Server capabilities: %s', server_capabilities)
        return server_capabilities

    def initialize(self, processId=None, rootUri=None, rootPath=None, initializationOptions=None, **_kwargs):
        log.debug('Language server initialized with %s %s %s %s',
                  processId, rootUri, rootPath, initializationOptions)
        if rootUri is None:
            rootUri = uris.from_fs_path(
                rootPath) if rootPath is not None else ''

        self.workspace = Workspace(rootUri, self._endpoint)

        workspace_folders = _kwargs['workspaceFolders'] or []
        for folder in workspace_folders:
            self.workspace_folders[folder['uri']] = folder

        # Get our capabilities
        return {'capabilities': self.capabilities()}

    def initialized(self):
        pass

    def text_document__did_close(self, textDocument=None, **_kwargs):
        self.workspace.rm_document(textDocument['uri'])
        # The same user defined method will be called here

    def text_document__did_open(self, textDocument=None, **_kwargs):
        self.workspace.put_document(
            textDocument['uri'], textDocument['text'], version=textDocument.get('version'))

    def text_document__did_change(self, contentChanges=None, textDocument=None, **_kwargs):
        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )

    def text_document__did_save(self, textDocument=None, **_kwargs):
        pass

    def text_document__rename(self, textDocument=None, position=None, newName=None, **_kwargs):
        return self.rename(textDocument['uri'], position, newName)

    def workspace__did_change_configuration(self, settings=None):
        pass

    def workspace__did_change_watched_files(self, **_kwargs):
        # Externally changed files may result in changed diagnostics
        pass

    def execute_command(self, command=None, arguments=None):
        try:
            return self._commands[command](arguments)
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

    def get_configuration(self, params):
        '''
        Get configuration for a specific file
        Figuring out how to get result from request future
        '''
        # rf = self._endpoint.request(lsp.CONFIGURATION, params)
        # return rf.result()
        pass
