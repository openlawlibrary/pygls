.. _pygls-logging:

Logging
~~~~~~~

Logs are useful for tracing client requests, finding out errors and
measuring time needed to return results to the client.

*pygls* uses the built-in python :external+python:py:mod:`logging` module which has to be configured before server is started.
Below is a minimal setup to setup logging in *pygls*:

.. code:: python

    import logging
    from pygls.lsp.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    if __name__ == '__main__':
        logging.basicConfig(message="[%(levelname)s]: %(message)s", level=logging.DEBUG)
        server.start_io()
