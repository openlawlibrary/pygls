# Copyright 2017 Palantir Technologies, Inc.
import os
from pygls import uris
from .fixtures import pygls

DOC_URI = uris.from_fs_path(__file__)


def test_local(pygls):
    """ Since the workspace points to the test directory """
    assert pygls.workspace.is_local()


def test_put_document(pygls):
    pygls.workspace.put_document(DOC_URI, 'content')
    assert DOC_URI in pygls.workspace._docs


def test_get_document(pygls):
    pygls.workspace.put_document(DOC_URI, 'TEXT')
    assert pygls.workspace.get_document(DOC_URI).source == 'TEXT'


def test_get_missing_document(tmpdir, pygls):
    source = 'TEXT'
    doc_path = tmpdir.join("test_document.py")
    doc_path.write(source)
    doc_uri = uris.from_fs_path(str(doc_path))
    assert pygls.workspace.get_document(doc_uri).source == 'TEXT'


def test_rm_document(pygls):
    pygls.workspace.put_document(DOC_URI, 'TEXT')
    assert pygls.workspace.get_document(DOC_URI).source == 'TEXT'
    pygls.workspace.rm_document(DOC_URI)
    assert pygls.workspace.get_document(DOC_URI)._source is None


def test_non_root_project(pygls):
    repo_root = os.path.join(pygls.workspace.root_path, 'repo-root')
    os.mkdir(repo_root)
    project_root = os.path.join(repo_root, 'project-root')
    os.mkdir(project_root)

    with open(os.path.join(project_root, 'setup.py'), 'w+') as f:
        f.write('# setup.py')

    test_uri = uris.from_fs_path(os.path.join(project_root, 'hello/test.py'))
    pygls.workspace.put_document(test_uri, 'assert True')
    test_doc = pygls.workspace.get_document(test_uri)
    assert project_root in test_doc.sys_path()
