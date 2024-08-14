############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
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
from typing import List, Optional

from lsprotocol import types as lsp

from ..conftest import ClientServer


TYPE_HIERARCHY_ITEM = lsp.TypeHierarchyItem(
    name="test_name",
    kind=lsp.SymbolKind.Class,
    uri="test_uri",
    range=lsp.Range(
        start=lsp.Position(line=0, character=0),
        end=lsp.Position(line=0, character=6),
    ),
    selection_range=lsp.Range(
        start=lsp.Position(line=0, character=0),
        end=lsp.Position(line=0, character=6),
    ),
)


def check_type_hierarchy_item_response(item):
    assert item.name == TYPE_HIERARCHY_ITEM.name
    assert item.kind == TYPE_HIERARCHY_ITEM.kind
    assert item.uri == TYPE_HIERARCHY_ITEM.uri
    assert item.range == TYPE_HIERARCHY_ITEM.range
    assert item.selection_range == TYPE_HIERARCHY_ITEM.selection_range


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(lsp.TEXT_DOCUMENT_PREPARE_TYPE_HIERARCHY)
        def f1(
            params: lsp.TypeHierarchyPrepareParams,
        ) -> Optional[List[lsp.TypeHierarchyItem]]:
            if params.text_document.uri == "file://return.list":
                return [TYPE_HIERARCHY_ITEM]
            else:
                return None

        @self.server.feature(lsp.TYPE_HIERARCHY_SUPERTYPES)
        def f2(
            params: lsp.TypeHierarchySupertypesParams,
        ) -> Optional[List[lsp.TypeHierarchyItem]]:
            return [TYPE_HIERARCHY_ITEM]

        @self.server.feature(lsp.TYPE_HIERARCHY_SUBTYPES)
        def f3(
            params: lsp.TypeHierarchySubtypesParams,
        ) -> Optional[List[lsp.TypeHierarchyItem]]:
            return [TYPE_HIERARCHY_ITEM]


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities
    assert capabilities.type_hierarchy_provider


@ConfiguredLS.decorate()
def test_type_hierarchy_prepare_return_list(client_server):
    client, _ = client_server
    response = client.protocol.send_request(
        lsp.TEXT_DOCUMENT_PREPARE_TYPE_HIERARCHY,
        lsp.TypeHierarchyPrepareParams(
            text_document=lsp.TextDocumentIdentifier(uri="file://return.list"),
            position=lsp.Position(line=0, character=0),
        ),
    ).result()

    check_type_hierarchy_item_response(response[0])


@ConfiguredLS.decorate()
def test_type_hierarchy_prepare_return_none(client_server):
    client, _ = client_server
    response = client.protocol.send_request(
        lsp.TEXT_DOCUMENT_PREPARE_TYPE_HIERARCHY,
        lsp.TypeHierarchyPrepareParams(
            text_document=lsp.TextDocumentIdentifier(uri="file://return.none"),
            position=lsp.Position(line=0, character=0),
        ),
    ).result()

    assert response is None


@ConfiguredLS.decorate()
def test_type_hierarchy_supertypes(client_server):
    client, _ = client_server
    response = client.protocol.send_request(
        lsp.TYPE_HIERARCHY_SUPERTYPES,
        lsp.TypeHierarchySupertypesParams(item=TYPE_HIERARCHY_ITEM),
    ).result()

    check_type_hierarchy_item_response(response[0])


@ConfiguredLS.decorate()
def test_type_hierarchy_subtypes(client_server):
    client, _ = client_server
    response = client.protocol.send_request(
        lsp.TYPE_HIERARCHY_SUBTYPES,
        lsp.TypeHierarchySubtypesParams(item=TYPE_HIERARCHY_ITEM),
    ).result()

    check_type_hierarchy_item_response(response[0])
