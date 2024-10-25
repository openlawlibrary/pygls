"""This server does nothing but print invalid JSON."""

import sys
import threading

from pygls.io_ import run
from pygls.protocol import JsonRPCProtocol, default_converter


class InvalidJsonProtocol(JsonRPCProtocol):
    """A protocol that only sends messages containing invalid JSON."""

    def handle_message(self, message):
        content = 'Content-Length: 5\r\n\r\n{"ll}'.encode("utf8")
        sys.stdout.buffer.write(content)
        sys.stdout.flush()


def main():
    run(
        threading.Event(),
        sys.stdin.buffer,
        InvalidJsonProtocol(None, default_converter()),
    )


if __name__ == "__main__":
    main()
