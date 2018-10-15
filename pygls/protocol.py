##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import asyncio
import json
import logging
import re
import traceback
import uuid
from collections import namedtuple
from concurrent.futures import Future
from itertools import zip_longest
from multiprocessing.pool import ThreadPool

from .exceptions import ThreadDecoratorError
from .feature_manager import FeatureManager
from .features import WORKSPACE_EXECUTE_COMMAND
from .types import DidOpenTextDocumentParams, DidChangeTextDocumentParams, \
    DidChangeWorkspaceFoldersParams, DidCloseTextDocumentParams, \
    InitializeParams, InitializeResult, ExecuteCommandParams, \
    ServerCapabilities
from .uris import from_fs_path
from .utils import call_user_feature, to_lsp_name
from .workspace import Workspace

logger = logging.getLogger(__name__)


class JsonRPCNotification:
    '''
    Used for constructing notification message.

    Attributes:
        id(str): Message id
        jsonrpc(str): Version of a json rpc protocol
        method(str): Name of the method that should be executed
        params(dict): Parameters that should be passed to the method
    '''

    def __init__(self, jsonrpc=None, method=None, params=None):
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params


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
        self.jsonrpc = jsonrpc
        self.result = result
        self.error = error


def deserialize_message(data):
    if 'jsonrpc' in data:
        if 'id' in data:
            if 'method' in data:
                return JsonRPCRequestMessage(**data)
            else:
                return JsonRPCResponseMessage(**data)
        else:
            return JsonRPCNotification(**data)

    return namedtuple('Object',
                      data.keys())(*data.values())


class JsonRPCProtocol(asyncio.Protocol):
    '''
    Json RPC protocol implementation using on top of `asyncio.Protocol`.
    Specification of the protocol can be found here:
        https://www.jsonrpc.org/specification

    This class provides bidirectional communication which is needed for LSP.
    '''
    BODY_PATTERN = re.compile(rb'\{.+?\}.*')

    CANCEL_REQUEST = '$/cancelRequest'

    CHARSET = 'utf-8'
    CONTENT_TYPE = 'application/vscode-jsonrpc'
    VERSION = '2.0'

    def __init__(self, server):
        # Lazy initialized
        self._pool = None
        self._server = server

        self._client_request_futures = {}
        self._server_request_futures = {}

        self.fm = FeatureManager()
        self.transport = None

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
        if method_name == JsonRPCProtocol.CANCEL_REQUEST:
            self._handle_cancel_notification(params.get('id'))
            return

        try:
            handler = self._get_handler(method_name)
            self._execute_notification(handler, params)
        except KeyError:
            logger.warn('Ignoring notification for unknown method {}'
                        .format(method_name))
        except Exception:
            logger.exception('Failed to handle notification {}: {}'
                             .format(method_name, params))

    def _handle_request(self, msg_id, method_name, params):
        '''Handles a request from the client.'''
        try:
            handler = self._get_handler(method_name)

            # workspace/executeCommand is a special case
            if method_name == WORKSPACE_EXECUTE_COMMAND:
                handler(params, msg_id)
            else:
                self._execute_request(msg_id, handler, params)
        except Exception:
            logger.exception('Failed to handle request {} {} {}'
                             .format(msg_id, method_name, params))
            # TODO: Send errors to the client

    def _handle_response(self, msg_id, result=None, error=None):
        '''Handles a response from the client.'''
        future = self._server_request_futures.pop(msg_id, None)

        if not future:
            logger.warn('Received response to unknown message id {}'
                        .format(msg_id))
            return

        if error is not None:
            logger.debug('Received error response to message {}: {}'
                         .format(msg_id, error))
            # future.set_exception(JsonRpcException.from_dict(error))

        logger.debug('Received result for message {}: {}'
                     .format(msg_id, result))
        future.set_result(result)

    def _execute_notification(self, handler, *params):
        if asyncio.iscoroutinefunction(handler):
            asyncio.ensure_future(handler(*params))
        else:
            if getattr(handler, 'execute_in_thread', False):
                self.get_thread_pool().apply_async(handler, (*params, ))
            else:
                handler(*params)

    def _execute_request(self, msg_id, handler, params):
        if asyncio.iscoroutinefunction(handler):
            future = asyncio.ensure_future(handler(params))
            self._client_request_futures[msg_id] = future
            future.add_done_callback(
                lambda res: self._send_response(msg_id, res.result()))
        else:
            # Can't be canceled
            if getattr(handler, 'execute_in_thread', False):
                self.get_thread_pool().apply_async(
                    handler, (params, ),
                    callback=lambda res: self._send_response(msg_id, res))
            else:
                self._send_response(msg_id, handler(params))

    def _procedure_handler(self, message):
        '''Delegates message to handlers depending on message type'''
        if message.jsonrpc != JsonRPCProtocol.VERSION:
            logger.warn('Unknown message {}'.format(message))
            return

        if isinstance(message, JsonRPCNotification):
            logger.debug('Notification message received.')
            self._handle_notification(message.method, message.params)
        elif isinstance(message, JsonRPCResponseMessage):
            logger.debug('Response message received.')
            self._handle_response(message.id, message.result, message.error)
        elif isinstance(message, JsonRPCRequestMessage):
            logger.debug('Request message received.')
            self._handle_request(message.id, message.method, message.params)

    def _get_handler(self, feature_name):
        '''
        Returns builtin feature by name if exists. If not, user defined
        feature will be returned.
        '''
        try:
            return self.fm.builtin_features[feature_name]
        except:
            try:
                return self.fm.features[feature_name]
            except:
                # TODO: raise MethodNotFoundError
                raise Exception()

    def _send_data(self, data):
        '''Sends data to the client'''
        if not data:
            return

        try:
            body = json.dumps(data, default=lambda o: o.__dict__)
            content_length = len(body.encode(self.CHARSET)) if body else 0

            response = (
                'Content-Length: {}\r\n'
                'Content-Type: {}; charset={}\r\n\r\n'
                '{}'.format(content_length,
                            self.CONTENT_TYPE,
                            self.CHARSET,
                            body)
            )

            logger.info('Sending data: {}'.format(body))

            self.transport.write(response.encode(self.CHARSET))
        except:
            logger.error(traceback.format_exc())

    def _send_response(self, msg_id, result=None, error=None):
        '''Sends a JSON RPC response to the client.

        Args:
            msg_id (str): Id from request
            result (any): Result returned by handler
            error (any): Error returned by handler
        '''
        response = JsonRPCResponseMessage(msg_id,
                                          JsonRPCProtocol.VERSION,
                                          result,
                                          error)
        self._send_data(response)

    def _send_request(self, method: str, params=None):
        '''Sends a JSON RPC request to the client.

        Args:
            method (str): The method name of the message to send
            params (any): The payload of the message

        Returns:
            Future that will resolve once a response has been received
        '''
        msg_id = str(uuid.uuid4())
        logger.debug('Sending request with id {}: {} {}'
                     .format(msg_id, method, params))

        request = JsonRPCRequestMessage(
            id=msg_id,
            jsonrpc=JsonRPCProtocol.VERSION,
            method=method,
            params=params
        )

        future = Future()

        self._server_request_futures[msg_id] = future
        self._send_data(request)

        return future

    def connection_made(self, transport: asyncio.Transport):
        '''Method from base class, called when connection is established'''
        self.transport = transport

    def data_received(self, data: bytes):
        '''Method from base class, called when server receives the data'''
        logger.debug('Received {}'.format(data))

        for part in data.split(b'Content-Length'):
            try:
                body = JsonRPCProtocol.BODY_PATTERN.findall(part)[0]
                self._procedure_handler(
                    json.loads(body.decode(self.CHARSET),
                               object_hook=deserialize_message))
            except:
                pass

    def notify(self, method: str, params=None):
        '''
        Sends a JSON RPC notification to the client.
        '''
        logger.debug('Sending notification: {} {}'.format(method, params))

        request = JsonRPCNotification(
            jsonrpc=JsonRPCProtocol.VERSION,
            method=method,
            params=params
        )

        self._send_data(request)

    def get_thread_pool(self):
        '''
        Returns thread pool instance (lazy initialization)
        '''
        # TODO: Specify number of processes
        if not self._pool:
            self._pool = ThreadPool()

        return self._pool

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


class LSPMeta(type):
    '''
    Metaclass for language server protocol.
    Purpose:
        Wrap LSP base methods with decorator which will call the user
        registered method with the same LSP name.
    '''

    def __new__(self, cls_name, cls_bases, cls):
        for attr_name, attr_val in cls.items():
            if callable(attr_val) and attr_name.startswith('bf_'):
                method_name = to_lsp_name(attr_name[3:])
                cls[attr_name] = call_user_feature(attr_val, method_name)

                logger.debug('Added decorator for lsp method: {}'
                             .format(attr_name))

        return super().__new__(self, cls_name, cls_bases, cls)


class LanguageServerProtocol(JsonRPCProtocol, metaclass=LSPMeta):
    def __init__(self, server):
        super().__init__(server)

        self._shutdown = False

        self.workspace = None

        self._register_builtin_features()

    def _register_builtin_features(self):
        '''
        Registers generic LSP features from this class.
        '''
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and name.startswith('bf_'):
                lsp_name = to_lsp_name(name[3:])
                self.fm.add_builtin_feature(lsp_name, attr)
                logger.debug('Registered generic feature {}'.format(name))

    def get_configuration(self, params, callback=None):
        '''
        Gets the configuration settings from the client.
        This method is asynchronous and the callback function
        will be called after the response is received.

        Args:
            params(dict): ConfigurationParams from lsp specs
            callback(callable): Callabe which will be called after
                response from the client is received
        '''
        if callback:
            def configuration(future):
                result = future.result()
                logger.info('Configuration for {} received: {}'
                            .format(params, result))
                return callback(result)

            future = self._send_request('workspace/configuration', params)
            future.add_done_callback(configuration)
        else:
            return self._send_request('workspace/configuration', params)

    def bf_exit(self, *args):
        '''
        Stops the server process. Should only work if _shutdown flag is setted
        '''
        self.transport.close()
        self.get_thread_pool().terminate()
        self._server.shutdown()

    def bf_initialize(self, initialize_params: InitializeParams):
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

    def bf_initialized(self, *args):
        pass

    def bf_shutdown(self, *args):
        '''
        Request from client which asks server to shutdown.
        '''
        self._shutdown = True
        return None

    def bf_text_document__did_change(self,
                                     params: DidChangeTextDocumentParams):
        '''
        Updates document's content.
        (Incremental (from server capabilities); not configurable for now)
        '''
        for change in params.contentChanges:
            self.workspace.update_document(params.textDocument, change)

    def bf_text_document__did_close(self,
                                    params: DidCloseTextDocumentParams):
        '''
        Removes document from workspace.
        '''
        self.workspace.rm_document(params.textDocument.uri)

    def bf_text_document__did_open(self,
                                   params: DidOpenTextDocumentParams):
        '''
        Puts document to the workspace.
        '''
        self.workspace.put_document(params.textDocument)

    def bf_workspace__did_change_workspace_folders(
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

    def bf_workspace__execute_command(self,
                                      params: ExecuteCommandParams,
                                      msg_id):
        '''
        Executes commands with passed arguments and returns a value.
        '''
        command = params.command
        args = params.arguments
        try:
            cmd_handler = self.fm.commands[command]
            self._execute_request(msg_id, cmd_handler, args)
        except:
            logger.error('Error while executing command `{}`: {}'
                         .format(command, traceback.format_exc()))
            self.workspace.show_message('Error while executing command: {} {}'
                                        .format(command, args))
