import asyncio
import json
import logging
import traceback

logger = logging.getLogger(__name__)


class ProcedureAlreadyRegisteredError(Exception):
    pass


class JsonRPCRequestMessage:
    def __init__(self, id=None, jsonrpc=None, method=None, params=None):
        self.id = id
        self.version = jsonrpc
        self.method = method
        self.params = params

    @classmethod
    def from_dict(cls, data):
        if 'jsonrpc' not in data:
            return data

        return cls(**data)


class JsonRPCResponseMessage:
    def __init__(self, id=None, jsonrpc=None, result=None, error=None):
        self.id = id
        self.version = jsonrpc
        self.result = result
        self.error = error


class JsonRPCProtocol(asyncio.Protocol):
    CANCEL_METHOD = "$/cancelRequest"
    DEFAULT_CHARSET = "utf-8"
    DEFAULT_CONTENT_TYPE = "application/jsonrpc"
    VERSION = "2.0"

    def __init__(self, **kwargs):
        self.charset = kwargs.get("content_type",
                                  self.DEFAULT_CHARSET)
        self.content_type = kwargs.get("content_type",
                                       self.DEFAULT_CONTENT_TYPE)

        self.procedure_options = {}
        self.procedures = {}
        self.transport = None

        self._client_request_futures = {}
        self._server_request_futures = {}

        self._pool = ThreadPool()

    def __call__(self):
        return self

    def _handle_cancel_notification(self, msg_id):
        """Handle a cancel notification from the client."""
        request_future = self._client_request_futures.pop(msg_id, None)

        if not request_future:
            logger.warn("Cancel notification for unknown message id {}"
                        .format(msg_id))
            return

        # Will only work if the request hasn't started executing
        if request_future.cancel():
            logger.debug("Cancelled request with id {}".format(msg_id))

    def _handle_notification(self, method_name, params):
        """Handle a notification from the client."""
        if method_name == JsonRPCProtocol.CANCEL_METHOD:
            self._handle_cancel_notification(params.get('id'))
            return

        try:
            handler = self.procedures[method_name]

            if asyncio.iscoroutinefunction(handler):
                asyncio.ensure_future(handler(params))
            else:
                self._pool.apply_async(handler, (params, ))

        except KeyError:
            logger.warn("Ignoring notification for unknown method {}"
                        .format(method_name))
        except Exception:
            logger.exception("Failed to handle notification {}: {}"
                             .format(method_name, params))

    def _handle_request(self, msg_id, method_name, params):
        """Handle a request from the client."""
        try:
            handler = self.procedures[method_name]

            if asyncio.iscoroutinefunction(handler):
                future = asyncio.ensure_future(handler(params))
                self._client_request_futures[msg_id] = future
                future.add_done_callback(lambda res: self.send_data(res.result()))
            else:
                # Can't be canceled
                self._pool.apply_async(
                    handler,
                    callback=lambda res: self.send_data(
                        JsonRPCResponseMessage(msg_id,
                                               JsonRPCProtocol.VERSION,
                                               res,
                                               None)))
        except Exception:
            logger.exception("Failed to handle request {} {} {}"
                             .format(msg_id, method_name, params))

    def _procedure_handler(self, message: JsonRPCRequestMessage):
        if message.version != JsonRPCProtocol.VERSION:
            logger.warn("Unknown message {}".format(message))
            return

        if message.id is None:
            logger.debug("Notification message received.")
            self._handle_notification(message.method, message.params)
        elif message.method is None:
            logger.debug("Response message received.")
        else:
            logger.debug("Request message received.")
            self._handle_request(message.id, message.method, message.params)

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

    def data_received(self, data: bytes):
        logger.debug("Received {}".format(data))

        if not data:
            return

        _, body = data.decode(self.charset).split("\r\n\r\n")

        try:
            self._procedure_handler(json.loads(body, object_hook=JsonRPCRequestMessage.from_dict))
        except:
            pass

    def register_procedure(self, procedure_name: str, **options: dict):
        def decorator(f):
            if procedure_name in self.procedures:
                msg = "Procedure {} is already registered." \
                    .format(procedure_name)

                logger.error(msg)
                raise ProcedureAlreadyRegisteredError(msg)

            self.procedures[procedure_name] = f

            if options:
                self.procedure_options[procedure_name] = options

            logger.info("Registered procedure {} with options {}"
                        .format(procedure_name, options))

            return f
        return decorator

    def send_data(self, data):
        try:
            body = json.dumps(data, default=lambda o: o.__dict__)
            content_length = len(body.encode("utf-8")) if body else 0

            response = (
                "Content-Length: {}\r\n"
                "Content-Type: {}; charset={}\r\n\r\n"
                "{}".format(content_length,
                            self.content_type,
                            self.charset,
                            body)
            )

            logger.info("Sending data: {}".format(body))

            self.transport.write(response.encode(self.charset))
        except:
            logger.error(traceback.format_exc())
