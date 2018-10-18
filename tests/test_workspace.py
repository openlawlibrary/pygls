##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import os
from pygls import uris
from pygls.workspace import Workspace
from pygls.types import TextDocumentItem, WorkspaceFolder

from .fixtures import workspace

DOC_URI = uris.from_fs_path(__file__)
DOC_TEXT = '''test'''
DOC = TextDocumentItem(DOC_URI, 'plaintext', '0', DOC_TEXT)


def test_add_folder(workspace):
    dir_uri = os.path.dirname(DOC_URI)
    dir_name = 'test'
    workspace.add_folder(WorkspaceFolder(dir_uri, dir_name))
    assert workspace.folders[dir_uri].name == dir_name


def test_get_document(workspace):
    workspace.put_document(DOC)

    assert workspace.get_document(DOC_URI).source == DOC_TEXT


def test_get_missing_document(tmpdir, workspace):
    doc_path = tmpdir.join("test_document.py")
    doc_path.write(DOC_TEXT)
    doc_uri = uris.from_fs_path(str(doc_path))
    assert workspace.get_document(doc_uri).source == DOC_TEXT


def test_put_document(workspace):
    workspace.put_document(DOC)
    assert DOC_URI in workspace._docs


def test_remove_folder(workspace):
    dir_uri = os.path.dirname(DOC_URI)
    dir_name = 'test'
    workspace.add_folder(WorkspaceFolder(dir_uri, dir_name))
    workspace.remove_folder(dir_uri)

    assert dir_uri not in workspace.folders


def test_remove_document(workspace):
    workspace.put_document(DOC)
    assert workspace.get_document(DOC_URI).source == DOC_TEXT
    workspace.remove_document(DOC_URI)
    assert workspace.get_document(DOC_URI)._source is None
