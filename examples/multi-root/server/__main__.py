##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import argparse

from .server import ls


def add_arguments(parser):
    parser.description = "multi-root example"

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


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.tcp:
        ls.start_tcp(args.host, args.port)
    else:
        ls.start_io()


if __name__ == '__main__':
    main()
