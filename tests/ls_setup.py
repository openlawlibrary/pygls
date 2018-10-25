##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import threading

from tests import (CMD_ASYNC, CMD_SYNC, CMD_THREAD, FEATURE_ASYNC,
                   FEATURE_SYNC, FEATURE_THREAD)


def setup_ls_features(ls):

    # Commands
    @ls.command(CMD_ASYNC)
    async def cmd_test3(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @ls.thread()
    @ls.command(CMD_THREAD)
    def cmd_test1(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @ls.command(CMD_SYNC)
    def cmd_test2(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    # Features
    @ls.feature(FEATURE_ASYNC)
    async def feature_async(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @ls.feature(FEATURE_SYNC)
    def feature_sync(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @ls.feature(FEATURE_THREAD)
    @ls.thread()
    def feature_thread(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()
