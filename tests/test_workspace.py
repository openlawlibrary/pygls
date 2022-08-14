############################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.                 #
# Original work licensed under the MIT License.                            #
# See ThirdPartyNotices.txt in the project root for license information.   #
# All modifications Copyright (c) Open Law Library. All rights reserved.   #
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
import os

from pygls import uris
from lsprotocol.types import TextDocumentItem, WorkspaceFolder
from pygls.workspace import Workspace

DOC_URI = uris.from_fs_path(__file__)
DOC_TEXT = """test"""
DOC = TextDocumentItem(
    uri=DOC_URI,
    language_id="plaintext",
    version=0,
    text=DOC_TEXT
)


def test_add_folder(workspace):
    dir_uri = os.path.dirname(DOC_URI)
    dir_name = "test"
    workspace.add_folder(WorkspaceFolder(uri=dir_uri, name=dir_name))
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
    dir_name = "test"
    workspace.add_folder(WorkspaceFolder(uri=dir_uri, name=dir_name))
    workspace.remove_folder(dir_uri)

    assert dir_uri not in workspace.folders


def test_remove_document(workspace):
    workspace.put_document(DOC)
    assert workspace.get_document(DOC_URI).source == DOC_TEXT
    workspace.remove_document(DOC_URI)
    assert workspace.get_document(DOC_URI)._source is None


def test_workspace_folders():
    wf1 = WorkspaceFolder(uri="/ws/f1", name="ws1")
    wf2 = WorkspaceFolder(uri="/ws/f2", name="ws2")

    workspace = Workspace("/ws", workspace_folders=[wf1, wf2])

    assert workspace.folders["/ws/f1"] is wf1
    assert workspace.folders["/ws/f2"] is wf2
