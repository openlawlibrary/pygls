.. _howto-use-custom-converter:

How To Use a Custom Converter
=============================

.. admonition:: Help Wanted
   :class: tip

   This page needs reworking slightly, it currently gives an approach for handling invalid data, but it should also be made clear that this approach can also be used to handle custom data types.

``pygls`` relies on `lsprotocol <https://github.com/microsoft/lsprotocol/>`__ for all of its type definitions.
``lsprotocol`` in turn builds on `attrs <https://www.attrs.org/en/stable/>`__ and `cattrs <https://catt.rs/en/stable/>`__ to provide the serialisation and deserialisation of types to/from JSON.

This is done through a ``converter`` object::

   >>> from lsprotocol.types import Position
   >>> from pygls.protocol import default_converter

   >>> converter = default_converter()
   >>> p = converter.structure({"line": 1, "character": 2}, Position)
   >>> p.line
   1
   >>> p.character
   2

Each language client/server receives a :func:`~pygls.protocol.default_converter` which is derived from the converter provided by ``lsprotocol``.
This means it will follow the Language Server Protocol exactly.

.. highlight:: python

Therefore, clients/servers written with *pygls* are pedantic and will complain loudly when given data they consider to be invalid

.. dropdown:: Example Data
   :open:

   .. code-block:: json

      {
          "jsonrpc": "2.0",
          "id": 10,
          "method": "textDocument/codeAction",
          "params": {
              "textDocument": {
                  "uri": "file:///path/to/file.txt"
              },
              "range": {
                  "start": { "line": 7, "character": 14 },
                  "end": { "line": 7, "character": 14 }
              },
              "context": {
                  "diagnostics": [
                      {
                          "range": {
                              "start": {
                                  "line": null,   // Invalid!
                                  "character": 0
                              },
                              "end":{
                                  "line": 1,
                                  "character": 65535
                              }
                          },
                          "message": "an example message",
                          "severity": 2,
                          "source": "example"
                      }
                  ]
              }
          }
      }

.. dropdown:: Example Error

   ::

      ERROR:pygls.protocol:Error receiving data
        + Exception Group Traceback (most recent call last):
        |    ...
        | cattrs.errors.ClassValidationError: While structuring TextDocumentCodeActionRequest (1 sub-exception)
        +-+---------------- 1 ----------------
          | Exception Group Traceback (most recent call last):
          |    ...
          | cattrs.errors.ClassValidationError: While structuring CodeActionParams (1 sub-exception)
          | Structuring class TextDocumentCodeActionRequest @ attribute params
          +-+---------------- 1 ----------------
            | Exception Group Traceback (most recent call last):
            |    ...
            | cattrs.errors.ClassValidationError: While structuring CodeActionContext (1 sub-exception)
            | Structuring class CodeActionParams @ attribute context
            +-+---------------- 1 ----------------
              | Exception Group Traceback (most recent call last):
              |    ...
              | cattrs.errors.IterableValidationError: While structuring typing.List[lsprotocol.types.Diagnostic] (2 sub-exceptions)
              | Structuring class CodeActionContext @ attribute diagnostics
              +-+---------------- 1 ----------------
                | Exception Group Traceback (most recent call last):
                |    ...
                | cattrs.errors.ClassValidationError: While structuring Diagnostic (1 sub-exception)
                | Structuring typing.List[lsprotocol.types.Diagnostic] @ index 0
                +-+---------------- 1 ----------------
                  | Exception Group Traceback (most recent call last):
                  |    ...
                  | cattrs.errors.ClassValidationError: While structuring Range (2 sub-exceptions)
                  | Structuring class Diagnostic @ attribute range
                  +-+---------------- 1 ----------------
                    | Exception Group Traceback (most recent call last):
                    |    ...
                    | cattrs.errors.ClassValidationError: While structuring Position (1 sub-exception)
                    | Structuring class Range @ attribute start
                    +-+---------------- 1 ----------------
                      | Traceback (most recent call last):
                      |    ...
                      | TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
                      | Structuring class Position @ attribute line
                      +------------------------------------

      The above exception was the direct cause of the following exception:

      Traceback (most recent call last):
         ...
      pygls.exceptions.JsonRpcInvalidParams: Invalid Params

Structure Hooks
---------------

By registering your own `structure hooks <https://catt.rs/en/stable/structuring.html#registering-custom-structuring-hooks>`__ you can take control over how malformed types should be handled.

Using the example data above, let's define a custom converter which includes a hook to silently ignore any diagnostics that are rejected when parsing the ``context`` field of a :lsp:`textDocument/codeAction` request.

.. code-block:: python

   from lsprotocol import types
   from pygls.protocol import default_converter

   def my_converter_factory():
       converter = default_converter()

       def code_action_context_hook(obj, type_):
           diagnostics = []
           raw_diagnostics = obj.get("diagnostics", []) or []

           for d in raw_diagnostics:
               try:
                   diagnostics.append(converter.structure(d, Diagnostic))
               except Exception:
                   pass

           return CodeActionContext(diagnostics=diagnostics)

       converter.register_structure_hook(CodeActionContext, code_action_context_hook)

       return converter

To use this custom converter with a language server set ``my_converter_factory`` as the server's ``converter_factory``.

.. code-block:: python

   server = LanguageServer(
       name="my-language-server",
       version="v1.0",
       converter_factory=my_converter_factory,
   )
