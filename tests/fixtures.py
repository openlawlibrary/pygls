# Copyright 2017 Palantir Technologies, Inc.
import sys
from mock import Mock
import pytest

from pygls import uris
from pygls.ls import LanguageServer
from pygls.workspace import Workspace, Document
from pygls.feature_manager import FeatureManager
from io import StringIO


DOC_URI = uris.from_fs_path(__file__)
DOC = """import sys

def main():
    print sys.stdin.read()
"""


@pytest.fixture
def pygls(tmpdir):
    """ Return an initialized LS """
    ls = LanguageServer()
    ls.setup_streams(StringIO, StringIO)

    ls.initialize(
        processId=1,
        rootUri=uris.from_fs_path(str(tmpdir)),
        initializationOptions={}
    )

    return ls


@pytest.fixture
def feature_manager():
    """ Return a feature manager """
    return FeatureManager()


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(uris.from_fs_path(str(tmpdir)), Mock())


@pytest.fixture
def doc():
    return Document(DOC_URI, DOC)
