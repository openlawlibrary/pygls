##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import sys
import pytest
from mock import Mock

from pygls import uris
from pygls.feature_manager import FeatureManager
from pygls.server import LanguageServer
from pygls.workspace import Workspace, Document

DOC = """document
for
testing
"""
DOC_URI = uris.from_fs_path(__file__)


@pytest.fixture
def doc():
    return Document(DOC_URI, DOC)


@pytest.fixture
def feature_manager():
    """ Return a feature manager """
    return FeatureManager()


# @pytest.fixture
# def pygls(tmpdir):
#     """ Return an initialized LS """
#     ls = LanguageServer()
#     ls.setup_streams(StringIO, StringIO)

#     ls.gf_initialize(
#         processId=1,
#         rootUri=uris.from_fs_path(str(tmpdir)),
#         initializationOptions={}
#     )

#     return ls


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(uris.from_fs_path(str(tmpdir)), Mock())
