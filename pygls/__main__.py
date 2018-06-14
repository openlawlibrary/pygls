'''
This module won't be part of pygls library.
For now, we are using it to test the basic idea.
'''
import argparse
import json
import logging
import logging.config
import sys
from .ls import LanguageServer

from . import lsp

LOG_FORMAT = "%(asctime)s UTC - %(levelname)s - %(name)s - %(message)s"


def add_arguments(parser):
    parser.description = "Python Language Server"

    parser.add_argument(
        "--tcp", action="store_true",
        help="Use TCP server instead of stdio"
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Bind to this address"
    )
    parser.add_argument(
        "--port", type=int, default=2087,
        help="Bind to this port"
    )

    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "--log-config",
        help="Path to a JSON file containing Python logging config."
    )
    log_group.add_argument(
        "--log-file",
        help="Redirect logs to the given file instead of writing to stderr."
        "Has no effect if used with --log-config."
    )

    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="Increase verbosity of log output, overrides log config file"
    )


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    _configure_logger(args.verbose, args.log_config, args.log_file)

    ls = LanguageServer()

    @ls.register(lsp.COMPLETION, triggerCharacters=['.'])
    def completions(ls, textDocument=None, position=None, **_kwargs):
        return {
            'isIncomplete': False,
            'items': [{'label': 'AAA'}, {'label': 'BBB'}]
        }

    @ls.register('textDocument/codeLens')
    def code_lens(textDocument=None, doc_uri=None, **_kwargs):
        # try:
        #     res = ls.get_configuration({'items': [
        #         {'scopeUri': textDocument['uri']}]})
        # except Exception as e:
        #     pass
        pass

    @ls.register(lsp.TEXT_DOC_DID_OPEN)
    def tx_doc_did_open(textDocument=None, **_kwargs):
        # This will be called after generic textDocument/didOpen method
        # NOTE: Not implemented yet
        # NOTE: * For easier testing
        # All registered features should have LS instance as first param,
        # rather then using LS instance from outside the function
        #
        pass

    @ls.register(lsp.REGISTER_COMMAND, name='custom.Command')
    def custom_command(params):
        # Commands are registered with required 'name' argument
        pass

    if args.tcp:
        ls.start_tcp(args.host, args.port)
    else:
        ls.start_io()


def _configure_logger(verbose=0, log_config=None, log_file=None):
    root_logger = logging.root

    if log_config:
        with open(log_config, 'r') as f:
            logging.config.dictConfig(json.load(f))
    else:
        formatter = logging.Formatter(LOG_FORMAT)
        if log_file:
            log_handler = logging.handlers.RotatingFileHandler(
                log_file, mode='a', maxBytes=50*1024*1024,
                backupCount=10, encoding=None, delay=0
            )
        else:
            log_handler = logging.StreamHandler()
        log_handler.setFormatter(formatter)
        root_logger.addHandler(log_handler)

    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    root_logger.setLevel(level)


if __name__ == '__main__':
    main()
