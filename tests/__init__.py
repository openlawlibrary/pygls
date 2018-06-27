##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import pytest
from pygls import IS_WIN

DUMMY_FEATURE = 'dummy_feature'
TRIGGER_CHARS = ['#', '!']
COMMANDS = ['add', 'test']

unix_only = pytest.mark.skipif(IS_WIN, reason="Unix only")
windows_only = pytest.mark.skipif(not IS_WIN, reason="Windows only")
