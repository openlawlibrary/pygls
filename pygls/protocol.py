##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import asyncio
import json
import logging
import re
import sys
import traceback
import uuid
from collections import namedtuple
from concurrent.futures import Future
from functools import partial
from itertools import zip_longest

from .exceptions import (JsonRpcException, JsonRpcInternalError,
                         JsonRpcMethodNotFound, JsonRpcRequestCancelled,
                         ThreadDecoratorError)
from .feature_manager import FeatureManager
from .features import WORKSPACE_CONFIGURATION, WORKSPACE_EXECUTE_COMMAND
from .types import (DidChangeTextDocumentParams,
                    DidChangeWorkspaceFoldersParams,
                    DidCloseTextDocumentParams, DidOpenTextDocumentParams,
                    ExecuteCommandParams, InitializeParams, InitializeResult,
                    ServerCapabilities)
from .uris import from_fs_path
from .utils import call_user_feature, to_lsp_name
from .workspace import Workspace

logger = logging.getLogger(__name__)


class JsonRPCNotification:
    """A class that represents json rpc notification message.

    Attributes:
        jsonrpc(str): Version of a json rpc protocol
        method(str): Name of the method that should be executed
        params(dict): Parameters that should be passed to the method
    """

    def __init__(self, jsonrpc=None, method=None, params=None):
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params


class JsonRPCRequestMessage:
    """A class that represents json rpc request message.

    Attributes:
        id(str): Message id
        jsonrpc(str): Version of a json rpc protocol
        method(str): Name of the method that should be executed
        params(dict): Parameters that should be passed to the method
    """

    def __init__(self, id=None, jsonrpc=None, method=None, params=None):
        self.id = id
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params


class JsonRPCResponseMessage:
    """A class that represents json rpc response message.

    Attributes:
        id(str): Message id (same as id from `JsonRPCRequestMessage`)
        jsonrpc(str): Version of a json rpc protocol
        result(str): Returned value from executed method
        error(str): Error object
    """

    def __init__(self, id=None, jsonrpc=None, result=None, error=None):
        self.id = id
        self.jsonrpc = jsonrpc
        self.result = result
        self.error = error


def deserialize_message(data):
    """Function used to deserialize data received from client."""
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
    """Json RPC protocol implementation using on top of `asyncio.Protocol`.

    Specification of the protocol can be found here:
        https://www.jsonrpc.org/specification

    This class provides bidirectional communication which is needed for LSP.
    """
    BODY_PATTERN = re.compile(rb'\{.+?\}.*')

    CANCEL_REQUEST = '$/cancelRequest'

    CHARSET = 'utf-8'
    CONTENT_TYPE = 'application/vscode-jsonrpc'
    VERSION = '2.0'

    def __init__(self, server):
        self._pool = None  # Lazy initialized
        self._server = server

        self._client_request_futures = {}
        self._server_request_futures = {}

        self.fm = FeatureManager(server)
        self.transport = None

    def __call__(self):
        return self

    def _execute_notification(self, handler, *params):
        """Executes notification message handler."""
        if asyncio.iscoroutinefunction(handler):
            future = asyncio.ensure_future(handler(*params))
            future.add_done_callback(self._execute_notification_callback)
        else:
            if getattr(handler, 'execute_in_thread', False):
                self._server.thread_pool.apply_async(handler, (*params, ))
            else:
                handler(*params)

    def _execute_notification_callback(self, future):
        """Success callback used for coroutine notification message."""
        if future.exception():
            error = JsonRpcInternalError.of(sys.exc_info()).to_dict()
            logger.exception('Exception occurred in notification: {}'
                             .format(error))

            # Revisit. Client does not support response with msg_id = None
            # https://stackoverflow.com/questions/31091376/json-rpc-2-0-allow-notifications-to-have-an-error-response
            # self._send_response(None, error=error)

    def _execute_request(self, msg_id, handler, params):
        """Executes request message handler."""
        if asyncio.iscoroutinefunction(handler):
            future = asyncio.ensure_future(handler(params))
            self._client_request_futures[msg_id] = future
            future.add_done_callback(partial(self._execute_request_callback,
                                             msg_id))
        else:
            # Can't be canceled
            if getattr(handler, 'execute_in_thread', False):
                self._server.thread_pool.apply_async(
                    handler, (params, ),
                    callback=lambda res: self._send_response(msg_id, res),
                    error_callback=partial(self._execute_request_err_callback,
                                           msg_id))
            else:
                self._send_response(msg_id, handler(params))

    def _execute_request_callback(self, msg_id, future):
        """Success callback used for coroutine request message."""
        try:
            if not future.cancelled():
                self._send_response(msg_id, result=future.result())
            else:
                self._send_response(
                    msg_id,
                    error=JsonRpcRequestCancelled(
                        f"Request with id {msg_id} is canceled"))
            self._client_request_futures.pop(msg_id, None)
        except Exception:
            error = JsonRpcInternalError.of(sys.exc_info()).to_dict()
            logger.exception('Exception occurred for message {}: {}'
                             .format(msg_id, error))
            self._send_response(msg_id, error=error)

    def _execute_request_err_callback(self, msg_id, exc):
        """Error callback used for coroutine request message."""
        exc_info = (type(exc), exc, None)
        error = JsonRpcInternalError.of(exc_info).to_dict()
        logger.exception('Exception occurred for message {}: {}'
                         .format(msg_id, error))
        self._send_response(msg_id, error=error)

    def _get_handler(self, feature_name):
        """Returns builtin or used defined feature by name if exists."""
        try:
            return self.fm.builtin_features[feature_name]
        except KeyError:
            try:
                return self.fm.features[feature_name]
            except KeyError:
                raise JsonRpcMethodNotFound.of(feature_name)

    def _handle_cancel_notification(self, msg_id):
        """Handles a cancel notification from the client."""
        future = self._client_request_futures.pop(msg_id, None)

        if not future:
            logger.warning('Cancel notification for unknown message id {}'
                           .format(msg_id))
            return

        # Will only work if the request hasn't started executing
        if future.cancel():
            logger.info('Cancelled request with id {}'.format(msg_id))

    def _handle_notification(self, method_name, params):
        """Handles a notification from the client."""
        if method_name == JsonRPCProtocol.CANCEL_REQUEST:
            self._handle_cancel_notification(params.get('id'))
            return

        try:
            handler = self._get_handler(method_name)
            self._execute_notification(handler, params)
        except KeyError:
            logger.warning('Ignoring notification for unknown method {}'
                           .format(method_name))
        except Exception:
            logger.exception('Failed to handle notification {}: {}'
                             .format(method_name, params))

    def _handle_request(self, msg_id, method_name, params):
        """Handles a request from the client."""
        try:
            handler = self._get_handler(method_name)

            # workspace/executeCommand is a special case
            if method_name == WORKSPACE_EXECUTE_COMMAND:
                handler(params, msg_id)
            else:
                self._execute_request(msg_id, handler, params)

        except JsonRpcException as e:
            logger.exception('Failed to handle request {} {} {}'
                             .format(msg_id, method_name, params))
            self._send_response(msg_id, None, e.to_dict())
        except Exception:
            logger.exception('Failed to handle request {} {} {}'
                             .format(msg_id, method_name, params))
            err = JsonRpcInternalError.of(sys.exc_info()).to_dict()
            self._send_response(msg_id, None, err)

    def _handle_response(self, msg_id, result=None, error=None):
        """Handles a response from the client."""
        future = self._server_request_futures.pop(msg_id, None)

        if not future:
            logger.warning('Received response to unknown message id {}'
                           .format(msg_id))
            return

        if error is not None:
            logger.debug('Received error response to message {}: {}'
                         .format(msg_id, error))
            future.set_exception(JsonRpcException.from_dict(error))

        logger.debug('Received result for message {}: {}'
                     .format(msg_id, result))
        future.set_result(result)

    def _procedure_handler(self, message):
        """Delegates message to handlers depending on message type."""
        if message.jsonrpc != JsonRPCProtocol.VERSION:
            logger.warning('Unknown message {}'.format(message))
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

    def _send_data(self, data):
        """Sends data to the client."""
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
        except Exception:
            logger.error(traceback.format_exc())

    def _send_response(self, msg_id, result=None, error=None):
        """Sends a JSON RPC response to the client.

        Args:
            msg_id(str): Id from request
            result(any): Result returned by handler
            error(any): Error returned by handler
        """
        response = JsonRPCResponseMessage(msg_id,
                                          JsonRPCProtocol.VERSION,
                                          result,
                                          error)
        self._send_data(response)

    def connection_made(self, transport: asyncio.Transport):
        """Method from base class, called when connection is established"""
        self.transport = transport

    def data_received(self, data: bytes):
        """Method from base class, called when server receives the data"""
        logger.debug('Received {}'.format(data))

        for part in data.split(b'Content-Length'):
            try:
                body = JsonRPCProtocol.BODY_PATTERN.findall(part)[0]
                self._procedure_handler(
                    json.loads(body.decode(self.CHARSET),
                               object_hook=deserialize_message))
            except IndexError:
                pass

    def notify(self, method: str, params=None):
        """Sends a JSON RPC notification to the client."""
        logger.debug('Sending notification: {} {}'.format(method, params))

        request = JsonRPCNotification(
            jsonrpc=JsonRPCProtocol.VERSION,
            method=method,
            params=params
        )

        self._send_data(request)

    def send_request(self, method, params=None):
        """Sends a JSON RPC request to the client.

        Args:
            method(str): The method name of the message to send
            params(any): The payload of the message

        Returns:
            Future that will be resolved once a response has been received
        """
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

    def thread(self):
        """Marks function to execute it in a thread pool."""
        def decorator(f):
            if asyncio.iscoroutinefunction(f):
                raise ThreadDecoratorError(
                    "Thread decorator can't be used with async function `{}`"
                    .format(f.__name__))

            f.execute_in_thread = True
            return f
        return decorator


class LSPMeta(type):
    """Wraps LSP built-in features (`bf_` naming convention).

    Built-in features cannot be overridden but user defined features with
    the same LSP name will be called after them.
    """
    def __new__(mcs, cls_name, cls_bases, cls):
        for attr_name, attr_val in cls.items():
            if callable(attr_val) and attr_name.startswith('bf_'):
                method_name = to_lsp_name(attr_name[3:])
                cls[attr_name] = call_user_feature(attr_val, method_name)

                logger.debug('Added decorator for lsp method: {}'
                             .format(attr_name))

        return super().__new__(mcs, cls_name, cls_bases, cls)


class LanguageServerProtocol(JsonRPCProtocol, metaclass=LSPMeta):
    """A class that represents language server protocol.

    It contains implementations for generic LSP features.

    Attributes:
        _shutdown(bool): Set to true if server received shutdown request
        workspace(Workspace): In memory workspace
    """

    def __init__(self, server):
        super().__init__(server)

        self._shutdown = False

        self.workspace = None

        self._register_builtin_features()

    def _register_builtin_features(self):
        """Registers generic LSP features from this class."""
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and name.startswith('bf_'):
                lsp_name = to_lsp_name(name[3:])
                self.fm.add_builtin_feature(lsp_name, attr)

    def bf_exit(self, *args):
        """Stops the server process."""
        self.transport.close()
        sys.exit(1)

    def bf_initialize(self, params: InitializeParams):
        """Method that initializes language server.
        It will compute and return server capabilities based on
        registered features.
        """
        logger.info('Language server initialized {}'.format(params))

        client_capabilities = params.capabilities
        root_uri = params.rootUri
        root_path = params.rootPath
        workspace_folders = params.workspaceFolders or []

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
        """Notification received when client and server are connected."""
        pass

    def bf_shutdown(self, *args):
        """Request from client which asks server to shutdown."""
        for future in self._client_request_futures.values():
            future.cancel()

        for future in self._server_request_futures.values():
            future.cancel()

        self._shutdown = True
        return None

    def bf_text_document__did_change(self,
                                     params: DidChangeTextDocumentParams):
        """Updates document's content.
        (Incremental(from server capabilities); not configurable for now)
        """
        for change in params.contentChanges:
            self.workspace.update_document(params.textDocument, change)

    def bf_text_document__did_close(self,
                                    params: DidCloseTextDocumentParams):
        """Removes document from workspace."""
        self.workspace.remove_document(params.textDocument.uri)

    def bf_text_document__did_open(self,
                                   params: DidOpenTextDocumentParams):
        """Puts document to the workspace."""
        self.workspace.put_document(params.textDocument)

    def bf_workspace__did_change_workspace_folders(
            self,
            params: DidChangeWorkspaceFoldersParams):
        """Adds/Removes folders from the workspace."""
        logger.info('Workspace folders changed: {}'.format(params))

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
        """Executes commands with passed arguments and returns a value."""
        cmd_handler = self.fm.commands[params.command]
        self._execute_request(msg_id, cmd_handler, params.arguments)

    def get_configuration(self, params, callback=None):
        """Gets the configuration settings from the client.

        This method is asynchronous and the callback function
        will be called after the response is received.

        Args:
            params(dict): ConfigurationParams from lsp specs
            callback(callable): Callabe which will be called after
                                response from the client is received
        Returns:
            Future that will be resolved once a response has been received
            NOTE: Calling `future.result()` blocks the main thread, so it
                  should be used for features/commands marked with
                  `@ls.thread()` decorator
        """
        if callback:
            def configuration(future: Future):
                result = future.result()
                logger.info('Configuration for {} received: {}'
                            .format(params, result))
                return callback(result)

            request_future = self.send_request(WORKSPACE_CONFIGURATION, params)
            request_future.add_done_callback(configuration)
        else:
            return self.send_request(WORKSPACE_CONFIGURATION, params)
