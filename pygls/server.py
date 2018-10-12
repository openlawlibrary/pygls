import asyncio
import logging

from .protocol import LanguageServerProtocol

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, protocol_cls):
        assert issubclass(protocol_cls, asyncio.Protocol)
        self.loop = asyncio.get_event_loop()

        self.lsp = protocol_cls(self)
        self.server = None

    def shutdown(self):
        self.server.close()
        # TODO: Gracefully shutdown event loops

    def start_tcp(self, host, port):
        self.server = self.loop.run_until_complete(
            self.loop.create_server(self.lsp, host, port)
        )
        self.loop.run_forever()


class LanguageServer(Server):
    def __init__(self):
        super().__init__(LanguageServerProtocol)

    def command(self, command_name):
        '''
        Registers new command (delegating to FeatureManager).

        Args:
            command_name(str): Name of the command to register
        '''
        return self.lsp.fm.command(command_name)

    def feature(self, *feature_names, **options):
        '''
        Registers one or more LSP features (delegating to FeatureManager).

        Args:
            *feature_names(tuple): One or more features to register
                NOTE: All possible LSP features are listed in lsp module
            **options(dict): Options for registered feature
                E.G. triggerCharacters=['.']
        '''
        return self.lsp.fm.feature(*feature_names, **options)

    def thread(self):
        return self.lsp.thread()
