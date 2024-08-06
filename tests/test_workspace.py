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

import pytest
from lsprotocol import types

from pygls import uris
from pygls.workspace import Workspace

DOC_URI = uris.from_fs_path(__file__)
DOC_TEXT = """test"""
DOC = types.TextDocumentItem(
    uri=DOC_URI, language_id="plaintext", version=0, text=DOC_TEXT
)
NOTEBOOK = types.NotebookDocument(
    uri="file:///path/to/notebook.ipynb",
    notebook_type="jupyter-notebook",
    version=0,
    cells=[
        types.NotebookCell(
            kind=types.NotebookCellKind.Code,
            document="nb-cell-scheme://path/to/notebook.ipynb#cv32321",
        ),
        types.NotebookCell(
            kind=types.NotebookCellKind.Code,
            document="nb-cell-scheme://path/to/notebook.ipynb#cp897h32",
        ),
    ],
)
NB_CELL_1 = types.TextDocumentItem(
    uri="nb-cell-scheme://path/to/notebook.ipynb#cv32321",
    language_id="python",
    version=0,
    text="# cell 1",
)
NB_CELL_2 = types.TextDocumentItem(
    uri="nb-cell-scheme://path/to/notebook.ipynb#cp897h32",
    language_id="python",
    version=0,
    text="# cell 2",
)
NB_CELL_3 = types.TextDocumentItem(
    uri="nb-cell-scheme://path/to/notebook.ipynb#cq343eeds",
    language_id="python",
    version=0,
    text="# cell 3",
)


def test_add_folder(workspace):
    dir_uri = os.path.dirname(DOC_URI)
    dir_name = "test"
    workspace.add_folder(types.WorkspaceFolder(uri=dir_uri, name=dir_name))
    assert workspace.folders[dir_uri].name == dir_name


def test_get_notebook_document_by_uri(workspace):
    """Ensure that we can get a notebook given its uri."""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook == NOTEBOOK


@pytest.mark.parametrize(
    "cell,expected",
    [
        (NB_CELL_1, NOTEBOOK),
        (NB_CELL_2, NOTEBOOK),
        (NB_CELL_3, None),
        (DOC, None),
    ],
)
def test_get_notebook_document_by_cell_uri(workspace, cell, expected):
    """Ensure that we can get a notebook given a uri of one of its cells"""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    notebook = workspace.get_notebook_document(cell_uri=cell.uri)
    assert notebook == expected


def test_get_text_document(workspace):
    workspace.put_text_document(DOC)

    assert workspace.get_text_document(DOC_URI).source == DOC_TEXT


def test_get_missing_document(tmpdir, workspace):
    doc_path = tmpdir.join("test_document.py")
    doc_path.write(DOC_TEXT)
    doc_uri = uris.from_fs_path(str(doc_path))
    assert workspace.get_text_document(doc_uri).source == DOC_TEXT


def test_put_notebook_document(workspace):
    """Ensure that we can add notebook documents to the workspace correctly."""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    assert NOTEBOOK.uri in workspace._notebook_documents
    assert NB_CELL_1.uri in workspace._text_documents
    assert NB_CELL_2.uri in workspace._text_documents


def test_put_text_document(workspace):
    workspace.put_text_document(DOC)
    assert DOC_URI in workspace._text_documents


def test_remove_folder(workspace):
    dir_uri = os.path.dirname(DOC_URI)
    dir_name = "test"
    workspace.add_folder(types.WorkspaceFolder(uri=dir_uri, name=dir_name))
    workspace.remove_folder(dir_uri)

    assert dir_uri not in workspace.folders


def test_remove_notebook_document(workspace):
    """Ensure that we can correctly remove a document from the workspace."""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    assert NOTEBOOK.uri in workspace._notebook_documents
    assert NB_CELL_1.uri in workspace._text_documents
    assert NB_CELL_2.uri in workspace._text_documents

    params = types.DidCloseNotebookDocumentParams(
        notebook_document=types.NotebookDocumentIdentifier(uri=NOTEBOOK.uri),
        cell_text_documents=[
            types.TextDocumentIdentifier(uri=NB_CELL_1.uri),
            types.TextDocumentIdentifier(uri=NB_CELL_2.uri),
        ],
    )
    workspace.remove_notebook_document(params)

    assert NOTEBOOK.uri not in workspace._notebook_documents
    assert NB_CELL_1.uri not in workspace._text_documents
    assert NB_CELL_2.uri not in workspace._text_documents


def test_remove_text_document(workspace):
    workspace.put_text_document(DOC)
    assert workspace.get_text_document(DOC_URI).source == DOC_TEXT
    workspace.remove_text_document(DOC_URI)
    assert workspace.get_text_document(DOC_URI)._source is None


def test_update_notebook_metadata(workspace):
    """Ensure we can update a notebook's metadata correctly."""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 0
    assert notebook.metadata is None

    params = types.DidChangeNotebookDocumentParams(
        notebook_document=types.VersionedNotebookDocumentIdentifier(
            uri=NOTEBOOK.uri, version=31
        ),
        change=types.NotebookDocumentChangeEvent(
            metadata={"custom": "metadata"},
        ),
    )
    workspace.update_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 31
    assert notebook.metadata == {"custom": "metadata"}


def test_update_notebook_cell_data(workspace):
    """Ensure we can update a notebook correctly when cell data changes."""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 0

    cell_1 = notebook.cells[0]
    assert cell_1.metadata is None
    assert cell_1.execution_summary is None

    cell_2 = notebook.cells[1]
    assert cell_2.metadata is None
    assert cell_2.execution_summary is None

    params = types.DidChangeNotebookDocumentParams(
        notebook_document=types.VersionedNotebookDocumentIdentifier(
            uri=NOTEBOOK.uri, version=31
        ),
        change=types.NotebookDocumentChangeEvent(
            cells=types.NotebookDocumentCellChanges(
                data=[
                    types.NotebookCell(
                        kind=types.NotebookCellKind.Code,
                        document=NB_CELL_1.uri,
                        metadata={"slideshow": {"slide_type": "skip"}},
                        execution_summary=types.ExecutionSummary(
                            execution_order=2, success=True
                        ),
                    ),
                    types.NotebookCell(
                        kind=types.NotebookCellKind.Code,
                        document=NB_CELL_2.uri,
                        metadata={"slideshow": {"slide_type": "note"}},
                        execution_summary=types.ExecutionSummary(
                            execution_order=3, success=False
                        ),
                    ),
                ]
            )
        ),
    )
    workspace.update_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 31

    cell_1 = notebook.cells[0]
    assert cell_1.metadata == {"slideshow": {"slide_type": "skip"}}
    assert cell_1.execution_summary == types.ExecutionSummary(
        execution_order=2, success=True
    )

    cell_2 = notebook.cells[1]
    assert cell_2.metadata == {"slideshow": {"slide_type": "note"}}
    assert cell_2.execution_summary == types.ExecutionSummary(
        execution_order=3, success=False
    )


def test_update_notebook_cell_content(workspace):
    """Ensure we can update a notebook correctly when the cell contents change."""
    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 0

    cell_1 = workspace.get_text_document(NB_CELL_1.uri)
    assert cell_1.version == 0
    assert cell_1.source == "# cell 1"

    cell_2 = workspace.get_text_document(NB_CELL_2.uri)
    assert cell_2.version == 0
    assert cell_2.source == "# cell 2"

    params = types.DidChangeNotebookDocumentParams(
        notebook_document=types.VersionedNotebookDocumentIdentifier(
            uri=NOTEBOOK.uri, version=31
        ),
        change=types.NotebookDocumentChangeEvent(
            cells=types.NotebookDocumentCellChanges(
                text_content=[
                    types.NotebookDocumentCellContentChanges(
                        document=types.VersionedTextDocumentIdentifier(
                            uri=NB_CELL_1.uri, version=13
                        ),
                        changes=[
                            types.TextDocumentContentChangePartial(
                                text="new text",
                                range=types.Range(
                                    start=types.Position(line=0, character=0),
                                    end=types.Position(line=0, character=8),
                                ),
                            )
                        ],
                    ),
                    types.NotebookDocumentCellContentChanges(
                        document=types.VersionedTextDocumentIdentifier(
                            uri=NB_CELL_2.uri, version=21
                        ),
                        changes=[
                            types.TextDocumentContentChangePartial(
                                text="",
                                range=types.Range(
                                    start=types.Position(line=0, character=0),
                                    end=types.Position(line=0, character=8),
                                ),
                            ),
                            types.TextDocumentContentChangePartial(
                                text="other text",
                                range=types.Range(
                                    start=types.Position(line=0, character=0),
                                    end=types.Position(line=0, character=0),
                                ),
                            ),
                        ],
                    ),
                ]
            )
        ),
    )
    workspace.update_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 31

    cell_1 = workspace.get_text_document(NB_CELL_1.uri)
    assert cell_1.version == 13
    assert cell_1.source == "new text"

    cell_2 = workspace.get_text_document(NB_CELL_2.uri)
    assert cell_2.version == 21
    assert cell_2.source == "other text"


def test_update_notebook_new_cells(workspace):
    """Ensure that we can correctly add new cells to an existing notebook."""

    params = types.DidOpenNotebookDocumentParams(
        notebook_document=NOTEBOOK,
        cell_text_documents=[
            NB_CELL_1,
            NB_CELL_2,
        ],
    )
    workspace.put_notebook_document(params)

    notebook = workspace.get_notebook_document(notebook_uri=NOTEBOOK.uri)
    assert notebook.version == 0

    cell_uris = [c.document for c in notebook.cells]
    assert cell_uris == [NB_CELL_1.uri, NB_CELL_2.uri]

    cell_1 = workspace.get_text_document(NB_CELL_1.uri)
    assert cell_1.version == 0
    assert cell_1.source == "# cell 1"

    cell_2 = workspace.get_text_document(NB_CELL_2.uri)
    assert cell_2.version == 0
    assert cell_2.source == "# cell 2"

    params = types.DidChangeNotebookDocumentParams(
        notebook_document=types.VersionedNotebookDocumentIdentifier(
            uri=NOTEBOOK.uri, version=31
        ),
        change=types.NotebookDocumentChangeEvent(
            cells=types.NotebookDocumentCellChanges(
                structure=types.NotebookDocumentCellChangeStructure(
                    array=types.NotebookCellArrayChange(
                        start=1,
                        delete_count=0,
                        cells=[
                            types.NotebookCell(
                                kind=types.NotebookCellKind.Code, document=NB_CELL_3.uri
                            )
                        ],
                    ),
                    did_open=[NB_CELL_3],
                )
            )
        ),
    )
    workspace.update_notebook_document(params)

    notebook = workspace.get_notebook_document(cell_uri=NB_CELL_3.uri)
    assert notebook.uri == NOTEBOOK.uri
    assert NB_CELL_3.uri in workspace._text_documents

    cell_uris = [c.document for c in notebook.cells]
    assert cell_uris == [NB_CELL_1.uri, NB_CELL_3.uri, NB_CELL_2.uri]


def test_workspace_folders():
    wf1 = types.WorkspaceFolder(uri="/ws/f1", name="ws1")
    wf2 = types.WorkspaceFolder(uri="/ws/f2", name="ws2")

    workspace = Workspace("/ws", workspace_folders=[wf1, wf2])

    assert workspace.folders["/ws/f1"] is wf1
    assert workspace.folders["/ws/f2"] is wf2


def test_null_workspace():
    workspace = Workspace(None)

    assert workspace.root_uri is None
    assert workspace.root_path is None
