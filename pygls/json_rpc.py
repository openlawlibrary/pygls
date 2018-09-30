import asyncio
import json
import logging
import traceback

logger = logging.getLogger(__name__)


class ProcedureAlreadyRegisteredError(Exception):
    pass


class JsonRPCProtocol(asyncio.Protocol):
    DEFAULT_CHARSET = "utf-8"
    DEFAULT_CONTENT_TYPE = "application/jsonrpc"
    VERSION = "2.0"

    def __init__(self, **kwargs):
        self.charset = kwargs.get("content_type",
                                  self.DEFAULT_CHARSET)
        self.content_type = kwargs.get("content_type",
                                       self.DEFAULT_CONTENT_TYPE)
        self.deserializer = kwargs.get("deserializer",
                                       self.DEFAULT_CONTENT_TYPE)
        self.serializer = kwargs.get("serializer",
                                     self.DEFAULT_CONTENT_TYPE)

        self.procedure_options = {}
        self.procedures = {}
        self.transport = None

    def __call__(self):
        return self

    @staticmethod
    def extract_body(body):
        id = body.get("id", None)
        json_rpc_version = body.get("jsonrpc", None)
        method = body.get("method", None)
        params = body.get("params", None)

        return id, json_rpc_version, method, params

    def _procedure_handler(self, body):
        id, version, method, params = JsonRPCProtocol.extract_body(body)

        if version is not JsonRPCProtocol.VERSION:
            logger.warn("Unknown message {}".format(body))
            return

        if not id:
            logger.debug("Notification message received.")
        elif not method:
            logger.debug("Response message received.")
        else:
            logger.debug("Request message received.")

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        logger.debug("Received {}".format(data))

        if not data:
            return

        _, body = data.decode(self.charset).split("\r\n\r\n")

        try:
            self._procedure_handler(json.loads(body))
        except:
            pass

    def register_procedure(self, procedure_name, **options):
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
            content_length = len(data.encode("utf-8")) if data else 0
            body = json.dumps(data)  # add serializer

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
