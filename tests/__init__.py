##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
from pygls import IS_WIN
import pytest

unix_only = pytest.mark.skipif(IS_WIN, reason="Unix only")
windows_only = pytest.mark.skipif(not IS_WIN, reason="Windows only")

CMD_ASYNC = 'cmd_async'
CMD_SYNC = 'cmd_sync'
CMD_THREAD = 'cmd_thread'

FEATURE_ASYNC = 'feature_async'
FEATURE_SYNC = 'feature_sync'
FEATURE_THREAD = 'feature_thread'
