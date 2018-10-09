##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import asyncio
import json
import logging
import traceback
from collections import namedtuple
from itertools import zip_longest
from multiprocessing.pool import ThreadPool

from .exceptions import ThreadDecoratorError
from .feature_manager import FeatureManager
from .types import DidOpenTextDocumentParams, DidChangeTextDocumentParams, \
    DidChangeWorkspaceFoldersParams, DidCloseTextDocumentParams, \
    InitializeParams, InitializeResult, ExecuteCommandParams, \
    ServerCapabilities
from .uris import from_fs_path
from .workspace import Workspace

logger = logging.getLogger(__name__)


class JsonRPCRequestMessage:
    '''
    Used for deserialization of client message from json to object.

    Attributes:
        id(str): Message id
        jsonrpc(str): Version of a json rpc protocol
        method(str): Name of the method that should be executed
        params(dict): Parameters that should be passed to the method
    '''

    def __init__(self, id=None, jsonrpc=None, method=None, params=None):
        self.id = id
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params

    @classmethod
    def from_dict(cls, data):
        if 'jsonrpc' in data:
            return cls(**data)

        return namedtuple('Object',
                          data.keys())(*data.values())


class JsonRPCResponseMessage:
    '''
    Used for construction of response that will be send to the client

    Attributes:
        id(str): Message id (same as id from `JsonRPCRequestMessage`)
        jsonrpc(str): Version of a json rpc protocol
        result(str): Returned value from executed method
        error(str): Error object
    '''

    def __init__(self, id=None, jsonrpc=None, result=None, error=None):
        self.id = id
        self.version = jsonrpc
        self.result = result
        self.error = error


class JsonRPCProtocol(asyncio.Protocol):
    '''
    Json RPC protocol implementation using on top of `asyncio.Protocol`.
    Specification of the protocol can be found here:
        https://www.jsonrpc.org/specification

    This class provides bidirectional communication which is needed for LSP.
    '''
    CANCEL_METHOD = '$/cancelRequest'

    DEFAULT_CHARSET = 'utf-8'
    DEFAULT_CONTENT_TYPE = 'application/jsonrpc'
    VERSION = '2.0'

    def __init__(self, **kwargs):
        self._client_request_futures = {}
        self._server_request_futures = {}

        self.charset = kwargs.get('charset',
                                  self.DEFAULT_CHARSET)
        self.content_type = kwargs.get('content_type',
                                       self.DEFAULT_CONTENT_TYPE)

        self.fm = FeatureManager()
        self.transport = None

        # Lazy initialized if at least one function is decorated with
        # @ls.thread()
        self._pool = None

    def __call__(self):
        return self

    def _handle_cancel_notification(self, msg_id):
        '''Handles a cancel notification from the client.'''
        request_future = self._client_request_futures.pop(msg_id, None)

        if not request_future:
            logger.warn('Cancel notification for unknown message id {}'
                        .format(msg_id))
            return

        # Will only work if the request hasn't started executing
        if request_future.cancel():
            logger.debug('Cancelled request with id {}'.format(msg_id))

    def _handle_notification(self, method_name, params):
        '''Handles a notification from the client.'''
        if method_name == JsonRPCProtocol.CANCEL_METHOD:
            self._handle_cancel_notification(params.get('id'))
            return

        try:
            handler = self.fm.get_feature_handler(method_name)

            if asyncio.iscoroutinefunction(handler):
                asyncio.ensure_future(handler(params))
            else:
                if getattr(handler, 'execute_in_thread', False):
                    self.thread_pool.apply_async(handler, (params, ))
                else:
                    handler(params)

        except KeyError:
            logger.warn('Ignoring notification for unknown method {}'
                        .format(method_name))
        except Exception:
            logger.exception('Failed to handle notification {}: {}'
                             .format(method_name, params))

    def _handle_request(self, msg_id, method_name, params):
        '''Handles a request from the client.'''
        try:
            handler = self.fm.get_feature_handler(method_name)

            if asyncio.iscoroutinefunction(handler):
                future = asyncio.ensure_future(handler(params))
                self._client_request_futures[msg_id] = future
                future.add_done_callback(
                    lambda res: self.send_data(res.result()))
            else:
                # Can't be canceled
                if getattr(handler, 'execute_in_thread', False):
                    self.thread_pool.apply_async(
                        handler, (params, ),
                        callback=lambda res: self.send_data(
                            JsonRPCResponseMessage(msg_id,
                                                   JsonRPCProtocol.VERSION,
                                                   res,
                                                   None)))
                else:
                    self.send_data(
                        JsonRPCResponseMessage(msg_id,
                                               JsonRPCProtocol.VERSION,
                                               handler(params),
                                               None))

        except Exception:
            logger.exception('Failed to handle request {} {} {}'
                             .format(msg_id, method_name, params))
            # TODO: Send errors to the client

    def _procedure_handler(self, message: JsonRPCRequestMessage):
        if message.jsonrpc != JsonRPCProtocol.VERSION:
            logger.warn('Unknown message {}'.format(message))
            return

        if message.id is None:
            logger.debug('Notification message received.')
            self._handle_notification(message.method, message.params)
        elif message.method is None:
            logger.debug('Response message received.')
        else:
            logger.debug('Request message received.')
            self._handle_request(message.id, message.method, message.params)

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

    def data_received(self, data: bytes):
        logger.debug('Received {}'.format(data))

        if not data:
            return

        _, body = data.decode(self.charset).split('\r\n\r\n')

        try:
            self._procedure_handler(
                json.loads(body, object_hook=JsonRPCRequestMessage.from_dict))
        except:
            pass

    @property
    def thread_pool(self):
        '''
        Returns thread pool instance
        '''
        # TODO: Specify number of processes
        if not self._pool:
            self._pool = ThreadPool()

        return self._pool

    def send_data(self, data):
        try:
            body = json.dumps(data, default=lambda o: o.__dict__)
            content_length = len(body.encode(self.charset)) if body else 0

            response = (
                'Content-Length: {}\r\n'
                'Content-Type: {}; charset={}\r\n\r\n'
                '{}'.format(content_length,
                            self.content_type,
                            self.charset,
                            body)
            )

            logger.info('Sending data: {}'.format(body))

            self.transport.write(response.encode(self.charset))
        except:
            logger.error(traceback.format_exc())

    def thread(self):
        '''
        Mark function to execute it in a thread pool
        '''
        def decorator(f):
            if asyncio.iscoroutinefunction(f):
                raise ThreadDecoratorError(
                    "Thread decorator can't be used with async function `{}`"
                    .format(f.__name__))

            f.execute_in_thread = True
            return f
        return decorator


class LanguageServerProtocol(JsonRPCProtocol):
    CONTENT_TYPE = 'application/vscode-jsonrpc'

    def __init__(self):
        super().__init__(content_type=LanguageServerProtocol.CONTENT_TYPE)

        self.workspace = None

        self._shutdown = False

        # TODO: Naming convention for builtin methods for easier registration
        self.fm.add_builtin_feature('initialize', self.gf_initialize)
        self.fm.add_builtin_feature(
            'textDocument/didOpen',
            self.gf_text_document__did_open)
        self.fm.add_builtin_feature(
            'textDocument/didChange',
            self.gf_text_document__did_change)
        self.fm.add_builtin_feature(
            'workspace/didChangeWorkspaceFolders',
            self.gf_workspace__did_change_workspace_folders)
        self.fm.add_builtin_feature(
            'textDocument/didClose',
            self.gf_text_document__did_close)
        self.fm.add_builtin_feature(
            'workspace/executeCommand',
            self.gf_workspace__execute_command)

        # self._register_builtin_features()

    # def _register_builtin_features(self):
    #     '''
    #     Registers generic LSP features from this class.
    #     Convention for feature names iss described in class doc.
    #     '''
    #     for name in dir(self):
    #         attr = getattr(self, name)
    #         if callable(attr) and name.startswith('gf_'):
    #             lsp_name = _utils.to_lsp_name(name[3:])
    #             self._generic_features[lsp_name] = attr
    #             logger.debug(f"Registered generic feature {name}")

    # def get_configuration(self, config_params, callback):
    #     '''
    #     Gets the configuration settings from the client.
    #     This method is asynchronous and the callback function
    #     will be called after the response is received.

    #     Args:
    #         config_params(dict): ConfigurationParams from lsp specs
    #         callback(callable): Callabe which will be called after
    #             response from the client is received
    #     '''
    #     def configuration(future):
    #         result = future.result()
    # logger.info(f'Configuration for {config_params} received: {result}')
    #         return callback(result)

    #     future = self._endpoint.request(
    #         lsp.WORKSPACE_CONFIGURATION, config_params)
    #     future.add_done_callback(configuration)

    # def gf_exit(self, **_kwargs):
    #     '''
    #     Stops the server process. Should only work if _shutdown flag is True
    #     '''
    #     self._endpoint.shutdown()
    #     self._jsonrpc_stream_reader.close()
    #     self._jsonrpc_stream_writer.close()

    def gf_exit(self):
        '''
        Clean resources
        '''
        self.thread_pool.terminate()
        # TODO: Shutdown server

    def gf_initialize(self, initialize_params: InitializeParams):
        '''
        This method is called once, after the client activates server.
        It will compute and return server capabilities based on
        registered features.
        '''
        logger.info('Language server initialized {}'
                    .format(initialize_params._asdict()))

        client_capabilities = initialize_params.capabilities
        root_uri = initialize_params.rootUri
        root_path = initialize_params.rootPath
        workspace_folders = initialize_params.workspaceFolders or []

        if root_uri is None:
            root_uri = from_fs_path(root_path) if root_path is not None else ''

        self.workspace = Workspace(root_uri, self)

        for folder in workspace_folders:
            self.workspace.add_folder(folder)

        server_capabilities = ServerCapabilities(self.fm.features.keys(),
                                                 self.fm.feature_options,
                                                 self.fm.commands,
                                                 client_capabilities)

        logger.debug('Server capabilities: {}'
                     .format(server_capabilities.__dict__))

        return InitializeResult(server_capabilities)

    def gf_shutdown(self):
        '''
        Request from client which asks server to shutdown.
        '''
        self._shutdown = True
        return None

    def gf_text_document__did_change(self,
                                     params: DidChangeTextDocumentParams):
        '''
        Updates document's content.
        (Incremental (from server capabilities); not configurable for now)
        '''
        for change in params.contentChanges:
            self.workspace.update_document(params.textDocument, change)

    def gf_text_document__did_close(self,
                                    params: DidCloseTextDocumentParams):
        '''
        Removes document from workspace.
        '''
        self.workspace.rm_document(params.textDocument.uri)

    def gf_text_document__did_open(self,
                                   params: DidOpenTextDocumentParams):
        '''
        Puts document to the workspace.
        '''
        self.workspace.put_document(params.textDocument)

    def gf_workspace__did_change_workspace_folders(
            self,
            params: DidChangeWorkspaceFoldersParams):
        '''
        Adds/Removes folders from the workspace
        '''
        logger.info('Workspace folders changed: {}'.format(params._asdict()))

        added_folders = params.event.added or []
        removed_folders = params.event.removed or []

        for f_add, f_remove in zip_longest(added_folders, removed_folders):
            if f_add:
                self.workspace.add_folder(f_add)
            if f_remove:
                self.workspace.remove_folder(f_remove)

    def gf_workspace__execute_command(self, params: ExecuteCommandParams):
        '''
        Executes commands with passed arguments and returns a value.
        '''
        command = params.command
        args = params.arguments
        try:
            # Same execution logic as request (create execution functions)
            return self.fm.commands[command](self, args)
        except:
            logger.error('Error while executing command `{}`: {}'
                         .format(command, traceback.format_exc()))
            # self.workspace.show_message(
            #     'Error while executing command: {}'.format(command))

    # def send_notification(self, notification_name, params):
    #     self._endpoint.notify(notification_name, params)
