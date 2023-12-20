How To Migrate to v1.0
======================

The most notable change of the ``v1.0`` release of ``pygls`` is the removal of its hand written LSP type and method definitions in favour of relying on the types provided by the `lsprotocol`_ library which are automatically generated from the LSP specification.
As as side effect this has also meant the removal of `pydantic`_ as a dependency, since ``lsprotocol`` uses `attrs`_ and `cattrs`_ for serialisation and validation.

This guide outlines how to adapt an existing server to the breaking changes introduced in this release.

Known Migrations
----------------
You may find insight and inspiration from these projects that have already successfully migrated to v1:

* `jedi-language-server`_
* `vscode-ruff`_
* `esbonio`_
* `yara-language-server`_

Updating Imports
----------------

The ``pygls.lsp.methods`` and ``pygls.lsp.types`` modules no longer exist.
Instead, all types and method names should now be imported from the ``lsprotocol.types`` module.

Additionally, the following types and constants have been renamed.

==================================================================  ==============
pygls                                                               lsprotocol
==================================================================  ==============
``CODE_ACTION``                                                     ``TEXT_DOCUMENT_CODE_ACTION``
``CODE_LENS``                                                       ``TEXT_DOCUMENT_CODE_LENS``
``COLOR_PRESENTATION``                                              ``TEXT_DOCUMENT_COLOR_PRESENTATION``
``COMPLETION``                                                      ``TEXT_DOCUMENT_COMPLETION``
``DECLARATION``                                                     ``TEXT_DOCUMENT_DECLARATION``
``DEFINITION``                                                      ``TEXT_DOCUMENT_DEFINITION``
``DOCUMENT_COLOR``                                                  ``TEXT_DOCUMENT_DOCUMENT_COLOR``
``DOCUMENT_HIGHLIGHT``                                              ``TEXT_DOCUMENT_DOCUMENT_HIGHLIGHT``
``DOCUMENT_LINK``                                                   ``TEXT_DOCUMENT_DOCUMENT_LINK``
``DOCUMENT_SYMBOL``                                                 ``TEXT_DOCUMENT_DOCUMENT_SYMBOL``
``FOLDING_RANGE``                                                   ``TEXT_DOCUMENT_FOLDING_RANGE``
``FORMATTING``                                                      ``TEXT_DOCUMENT_FORMATTING``
``HOVER``                                                           ``TEXT_DOCUMENT_HOVER``
``IMPLEMENTATION``                                                  ``TEXT_DOCUMENT_IMPLEMENTATION``
``LOG_TRACE_NOTIFICATION``                                          ``LOG_TRACE``
``ON_TYPE_FORMATTING``                                              ``TEXT_DOCUMENT_ON_TYPE_FORMATTING``
``PREPARE_RENAME``                                                  ``TEXT_DOCUMENT_PREPARE_RENAME``
``PROGRESS_NOTIFICATION``                                           ``PROGRESS``
``RANGE_FORMATTING``                                                ``TEXT_DOCUMENT_RANGE_FORMATTING``
``REFERENCES``                                                      ``TEXT_DOCUMENT_REFERENCES``
``RENAME``                                                          ``TEXT_DOCUMENT_RENAME``
``SELECTION_RANGE``                                                 ``TEXT_DOCUMENT_SELECTION_RANGE``
``SET_TRACE_NOTIFICATION``                                          ``SET_TRACE``
``SIGNATURE_HELP``                                                  ``TEXT_DOCUMENT_SIGNATURE_HELP``
``TEXT_DOCUMENT_CALL_HIERARCHY_INCOMING_CALLS``                     ``CALL_HIERARCHY_INCOMING_CALLS``
``TEXT_DOCUMENT_CALL_HIERARCHY_OUTGOING_CALLS``                     ``CALL_HIERARCHY_OUTGOING_CALLS``
``TEXT_DOCUMENT_CALL_HIERARCHY_PREPARE``                            ``TEXT_DOCUMENT_PREPARE_CALL_HIERARCHY``
``TYPE_DEFINITION``                                                 ``TEXT_DOCUMENT_TYPE_DEFINITION``
``WORKSPACE_FOLDERS``                                               ``WORKSPACE_WORKSPACE_FOLDERS``
``ApplyWorkspaceEditResponse``                                      ``ApplyWorkspaceEditResult``
``ClientInfo``                                                      ``InitializeParamsClientInfoType``
``CodeActionDisabled``                                              ``CodeActionDisabledType``
``CodeActionLiteralSupportActionKindClientCapabilities``            ``CodeActionClientCapabilitiesCodeActionLiteralSupportTypeCodeActionKindType``
``CodeActionLiteralSupportClientCapabilities``                      ``CodeActionClientCapabilitiesCodeActionLiteralSupportType``
``CompletionItemClientCapabilities``                                ``CompletionClientCapabilitiesCompletionItemType``
``CompletionItemKindClientCapabilities``                            ``CompletionClientCapabilitiesCompletionItemKindType``
``CompletionTagSupportClientCapabilities``                          ``CompletionClientCapabilitiesCompletionItemTypeTagSupportType``
``DocumentSymbolCapabilitiesTagSupport``                            ``DocumentSymbolClientCapabilitiesTagSupportType``
``InsertTextModeSupportClientCapabilities``                         ``CompletionClientCapabilitiesCompletionItemTypeInsertTextModeSupportType``
``MarkedStringType``                                                ``MarkedString``
``MarkedString``                                                    ``MarkedString_Type1``
``PrepareRename``                                                   ``PrepareRenameResult_Type1``
``PublishDiagnosticsTagSupportClientCapabilities``                  ``PublishDiagnosticsClientCapabilitiesTagSupportType``
``ResolveSupportClientCapabilities``                                ``CodeActionClientCapabilitiesResolveSupportType``
``SemanticTokensRequestsFull``                                      ``SemanticTokensRegistrationOptionsFullType1``
``SemanticTokensRequests``                                          ``SemanticTokensClientCapabilitiesRequestsType``
``ServerInfo``                                                      ``InitializeResultServerInfoType``
``ShowMessageRequestActionItem``                                    ``ShowMessageRequestClientCapabilitiesMessageActionItemType``
``SignatureHelpInformationClientCapabilities``                      ``SignatureHelpClientCapabilitiesSignatureInformationType``
``SignatureHelpInformationParameterInformationClientCapabilities``  ``SignatureHelpClientCapabilitiesSignatureInformationTypeParameterInformationType``
``TextDocumentContentChangeEvent``                                  ``TextDocumentContentChangeEvent_Type1``
``TextDocumentContentChangeTextEvent``                              ``TextDocumentContentChangeEvent_Type2``
``TextDocumentSyncOptionsServerCapabilities``                       ``TextDocumentSyncOptions``
``Trace``                                                           ``TraceValues``
``URI``                                                             ``str``
``WorkspaceCapabilitiesSymbolKind``                                 ``WorkspaceSymbolClientCapabilitiesSymbolKindType``
``WorkspaceCapabilitiesTagSupport``                                 ``WorkspaceSymbolClientCapabilitiesTagSupportType``
``WorkspaceFileOperationsServerCapabilities``                       ``FileOperationOptions``
``WorkspaceServerCapabilities``                                     ``ServerCapabilitiesWorkspaceType``
==================================================================  ==============

Custom Models
-------------

One of the most obvious changes is the switch to `attrs`_ and `cattrs`_ for serialization and deserialisation.
This means that any custom models used by your language server will need to be converted to an ``attrs`` style class.

.. code-block:: python

   # Before
   from pydantic import BaseModel, Field

   class ExampleConfig(BaseModel):
       build_dir: Optional[str] = Field(None, alias="buildDir")

       builder_name: str = Field("html", alias="builderName")

       conf_dir: Optional[str] = Field(None, alias="confDir")

.. code-block:: python

   # After
   import attrs

   @attrs.define
   class ExampleConfig:
       build_dir: Optional[str] = attrs.field(default=None)

       builder_name: str = attrs.field(default="html")

       conf_dir: Optional[str] = attrs.field(default=None)


Pygls provides a default `converter`_ that it will use when converting your models to/from JSON, which should be sufficient for most scenarios.

.. code-block:: pycon

   >>> from pygls.protocol import default_converter
   >>> converter = default_converter()

   >>> config = ExampleConfig(builder_name='epub', conf_dir='/path/to/conf')
   >>> converter.unstructure(config)
   {'builderName': 'epub', 'confDir': '/path/to/conf'}   # Note how snake_case is converted to camelCase

   >>> converter.structure({'builderName': 'epub', 'confDir': '/path/to/conf'}, ExampleConfig)
   ExampleConfig(build_dir=None, builder_name='epub', conf_dir='/path/to/conf')

However, depending on the complexity of your type definitions you may find the default converter fail to parse some of your types.

.. code-block:: pycon

   >>> from typing import Literal, Union

   >>> @attrs.define
   ... class ExampleConfig:
   ...     num_jobs: Union[Literal["auto"], int] = attrs.field(default='auto')
   ...

   >>> converter.structure({'numJobs': 'auto'}, ExampleConfig)
     + Exception Group Traceback (most recent call last):
     |   File "<stdin>", line 1, in <module>
     |   File "/.../python3.10/site-packages/cattrs/converters.py", li
   ne 309, in structure
     |     return self._structure_func.dispatch(cl)(obj, cl)
     |   File "<cattrs generated structure __main__.ExampleConfig-2>", line 10, in structure_ExampleConfig
     |     if errors: raise __c_cve('While structuring ' + 'ExampleConfig', errors, __cl)
     | cattrs.errors.ClassValidationError: While structuring ExampleConfig (1 sub-exception)
     +-+---------------- 1 ----------------
       | Traceback (most recent call last):
       |   File "<cattrs generated structure __main__.ExampleConfig-2>", line 6, in structure_ExampleConfig
       |     res['num_jobs'] = __c_structure_num_jobs(o['numJobs'], __c_type_num_jobs)
       |   File "/.../python3.10/site-packages/cattrs/converters.py",
   line 377, in _structure_error
       |     raise StructureHandlerNotFoundError(msg, type_=cl)
       | cattrs.errors.StructureHandlerNotFoundError: Unsupported type: typing.Union[typing.Literal['auto'], int].
    Register a structure hook for it.
       | Structuring class ExampleConfig @ attribute num_jobs
       +------------------------------------

In which case you can extend the converter provided by ``pygls`` with your own `structure hooks`_

.. code-block:: python

   from pygls.protocol import default_converter

   def custom_converter():
       converter = default_converter()
       converter.register_structure_hook(Union[Literal['auto', int], lambda obj, _: obj)

       return converter

You can then override the default converter used by ``pygls`` when constructing your language server instance

.. code-block:: python

   server = LanguageServer(
       name="my-language-server", version="v1.0", converter_factory=custom_converter
   )

See the `hooks.py`_ module in ``lsprotocol`` for some example structure hooks

Miscellaneous
-------------

Mandatory ``name`` and ``version``
""""""""""""""""""""""""""""""""""

It is now necessary to provide a name and version when constructing an instance of the ``LanguageServer`` class

.. code-block:: python

   from pygls.server import LanguageServer

   server = LanguageServer(name="my-language-server", version="v1.0")


``ClientCapabilities.get_capability`` is now ``get_capability``
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: python

   # Before
   from pygls.lsp.types import ClientCapabilities

   client_capabilities = ClientCapabilities()
   commit_character_support = client_capabilities.get_capability(
      "text_document.completion.completion_item.commit_characters_support", False
   )

.. code-block:: python

   # After
   from lsprotocol.types import ClientCapabilities
   from pygls.capabilities import get_capability

   client_capabilities = ClientCapabilities()
   commit_character_support = get_capability(
      client_capabilities,
      "text_document.completion.completion_item.commit_characters_support",
      False
   )

.. _attrs: https://www.attrs.org/en/stable/index.html
.. _cattrs: https://cattrs.readthedocs.io/en/stable/
.. _converter: https://cattrs.readthedocs.io/en/stable/converters.html
.. _hooks.py: https://github.com/microsoft/lsprotocol/blob/main/lsprotocol/_hooks.py
.. _lsprotocol: https://github.com/microsoft/lsprotocol
.. _pydantic: https://pydantic-docs.helpmanual.io/
.. _structure hooks: https://cattrs.readthedocs.io/en/stable/structuring.html#registering-custom-structuring-hooks
.. _jedi-language-server: https://github.com/pappasam/jedi-language-server/pull/230
.. _yara-language-server: https://github.com/avast/yls/pull/34
.. _vscode-ruff: https://github.com/charliermarsh/vscode-ruff/pull/37
.. _esbonio: https://github.com/swyddfa/esbonio/pull/484
