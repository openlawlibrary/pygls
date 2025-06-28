How To Run the Pyodide Test Suite
=================================

.. highlight:: none

This guide outlines how to setup the environment needed to run the `Pyodide <https://pyodide.org/en/stable/>`__ test suite.

#. If you haven't done so already, install `uv <https://docs.astral.sh/uv/getting-started/installation>`__ to manage dependencies and tasks.

#. In order to run Pyodide outside of the browser you will need `NodeJs <https://nodejs.org/en>`__ installed.

#. Additionaly you will need to install the required node dependencies (which are specified in ``tests/pyodide/package.json``)::

     $ cd tests/pyodide
     tests/pyodide $ npm ci

#. To bootstrap the Python environment within the Pyodide runtime the test suite needs to install ``pygls`` from its wheel archive.
   From the repository root, use ``uv`` to package the current development version::

     $ uv build

   This will place the required ``*.whl`` file in the ``dist/`` folder

#. Finally, to run the end-to-end tests against Pyodide, pass the ``--lsp-runtime pyodide`` option to ``pytest``::

     $ uv run pytest --lsp-runtime pyodide
     ============================================ test session starts ============================================
     platform linux -- Python 3.13.0, pytest-8.3.3, pluggy-1.5.0
     rootdir: /var/home/alex/Projects/openlawlibrary/pygls/main
     configfile: pyproject.toml
     plugins: cov-5.0.0, asyncio-0.24.0
     asyncio: mode=Mode.AUTO, default_loop_scope=None
     pygls: runtime='pyodide', transport='stdio'
     collected 216 items

     tests/e2e/test_code_action.py .                                                                        [  0%]
     tests/e2e/test_code_lens.py ...                                                                        [  1%]
     tests/e2e/test_colors.py ..                                                                            [  2%]
     tests/e2e/test_completion.py .                                                                         [  3%]
     tests/e2e/test_declaration.py .                                                                        [  3%]
     tests/e2e/test_definition.py .                                                                         [  4%]
     tests/e2e/test_formatting.py ....                                                                      [  6%]
     tests/e2e/test_hover.py ...                                                                            [  7%]
     tests/e2e/test_implementation.py .                                                                     [  7%]
     tests/e2e/test_inlay_hints.py .                                                                        [  8%]
     tests/e2e/test_links.py ..                                                                             [  9%]
     tests/e2e/test_publish_diagnostics.py .                                                                [  9%]
     tests/e2e/test_pull_diagnostics.py ...                                                                 [ 11%]
     tests/e2e/test_references.py .                                                                         [ 11%]
     tests/e2e/test_rename.py ....                                                                          [ 13%]
     tests/e2e/test_semantic_tokens.py ......                                                               [ 16%]
     tests/e2e/test_symbols.py ...                                                                          [ 17%]
     tests/e2e/test_threaded_handlers.py .ss                                                                [ 18%]
     tests/e2e/test_type_definition.py .                                                                    [ 19%]
     tests/lsp/test_call_hierarchy.py .....                                                                 [ 21%]
     tests/lsp/test_document_highlight.py ...                                                               [ 23%]
     tests/lsp/test_errors.py .....                                                                         [ 25%]
     tests/lsp/test_folding_range.py ...                                                                    [ 26%]
     tests/lsp/test_linked_editing_range.py ...                                                             [ 28%]
     tests/lsp/test_moniker.py ...                                                                          [ 29%]
     tests/lsp/test_progress.py .......                                                                     [ 32%]
     tests/lsp/test_selection_range.py ...                                                                  [ 34%]
     tests/lsp/test_signature_help.py .ss                                                                   [ 35%]
     tests/lsp/test_type_hierarchy.py .....                                                                 [ 37%]
     tests/test_client.py ...                                                                               [ 39%]
     tests/test_document.py .......................                                                         [ 50%]
     tests/test_feature_manager.py .......................................                                  [ 70%]
     tests/test_language_server.py .......                                                                  [ 73%]
     tests/test_protocol.py ....................                                                            [ 82%]
     tests/test_server_connection.py ...                                                                    [ 84%]
     tests/test_types.py ...                                                                                [ 85%]
     tests/test_uris.py .......sssss                                                                        [ 91%]
     tests/test_workspace.py ...................                                                            [100%]
     ================================ 207 passed, 9 skipped in 102.04s (0:01:42) =================================


.. tip::

   You can find logs from the Pyodide environment in a file called ``pyodide.log`` in the repository root::

     $ tail -f
     Loading micropip, packaging
     Loaded micropip, packaging
     Loading attrs, six
     Loaded attrs, six
     Starting sync IO server
     Language server initialized InitializeParams(capabilities=ClientCapabilities(workspace=None, text_document=None, notebook_document=None, window=None, general=None, experimental=None), process_id=None, client_info=None, locale=None, root_path=None, root_uri='file:///workspace', initialization_options=None, trace=None, work_done_token=None, workspace_folders=None)
     Sending data: {"id": "5f4b70c6-fd2f-4806-985c-ce059c6a1c38", "jsonrpc": "2.0", "result": {"capabilities": {"positionEncoding": "utf-16", "textDocumentSync": {"openClose": true, "change": 2, "save": false}, "declarationProvider": true, "definitionProvider": true, "typeDefinitionProvider": true, "implementationProvider": true, "referencesProvider": true, "executeCommandProvider": {"commands": []}, "workspace": {"workspaceFolders": {"supported": true, "changeNotifications": true}, "fileOperations": {}}}, "serverInfo": {"name": "goto-server", "version": "v1"}}}
     Index: {'file:///workspace/code.txt': {'types': {'Rectangle': 0:5-0:14, 'Square': 1:5-1:11}, 'functions': {'area': 3:3-3:7, 'volume': 5:3-5:9}}}
     Sending data: {"id": "f61d6b6a-9dab-4c56-b2c4-f751bfbb52da", "jsonrpc": "2.0", "result": null}
     Sending data: {"id": "db8b8009-adca-4b48-86a5-b04b622d6426", "jsonrpc": "2.0", "result": {"uri": "file:///workspace/code.txt", "range": {"start": {"line": 0, "character": 5}, "end": {"line": 0, "character": 14}}}}
     Sending data: {"id": "e6de9938-5af2-45bf-a730-19e29e6a0465", "jsonrpc": "2.0", "result": null}
     Shutting down the server
