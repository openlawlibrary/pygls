############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
import threading

from tests import (CMD_ASYNC, CMD_SYNC, CMD_THREAD, FEATURE_ASYNC,
                   FEATURE_SYNC, FEATURE_THREAD)


def setup_ls_features(server):

    # Commands
    @server.command(CMD_ASYNC)
    async def cmd_test3(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @server.thread()
    @server.command(CMD_THREAD)
    def cmd_test1(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @server.command(CMD_SYNC)
    def cmd_test2(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    # Features
    @server.feature(FEATURE_ASYNC)
    async def feature_async(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @server.feature(FEATURE_SYNC)
    def feature_sync(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @server.feature(FEATURE_THREAD)
    @server.thread()
    def feature_thread(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()
