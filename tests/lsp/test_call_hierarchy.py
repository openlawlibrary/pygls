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

from lsprotocol.types import (
    CALL_HIERARCHY_INCOMING_CALLS,
    CALL_HIERARCHY_OUTGOING_CALLS,
    TEXT_DOCUMENT_PREPARE_CALL_HIERARCHY
)
from lsprotocol.types import (
    CallHierarchyIncomingCall, CallHierarchyIncomingCallsParams,
    CallHierarchyItem, CallHierarchyOptions, CallHierarchyOutgoingCall,
    CallHierarchyOutgoingCallsParams, CallHierarchyPrepareParams,
    Position, Range, SymbolKind, SymbolTag, TextDocumentIdentifier
)

from ..conftest import ClientServer

CALL_HIERARCHY_ITEM = CallHierarchyItem(
    name="test_name",
    kind=SymbolKind.File,
    uri="test_uri",
    range=Range(
        start=Position(line=0, character=0),
        end=Position(line=1, character=1),
    ),
    selection_range=Range(
        start=Position(line=1, character=1),
        end=Position(line=2, character=2),
    ),
    tags=[SymbolTag.Deprecated],
    detail="test_detail",
    data="test_data",
)


def check_call_hierarchy_item_response(item):
    assert item.name == 'test_name'
    assert item.kind == SymbolKind.File
    assert item.uri == 'test_uri'
    assert item.range.start.line == 0
    assert item.range.start.character == 0
    assert item.range.end.line == 1
    assert item.range.end.character == 1
    assert item.selection_range.start.line == 1
    assert item.selection_range.start.character == 1
    assert item.selection_range.end.line == 2
    assert item.selection_range.end.character == 2
    assert len(item.tags) == 1
    assert item.tags[0] == SymbolTag.Deprecated
    assert item.detail == 'test_detail'
    assert item.data == 'test_data'


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_PREPARE_CALL_HIERARCHY,
            CallHierarchyOptions(),
        )
        def f1(
            params: CallHierarchyPrepareParams
        ) -> Optional[List[CallHierarchyItem]]:
            if params.text_document.uri == 'file://return.list':
                return [CALL_HIERARCHY_ITEM]
            else:
                return None

        @self.server.feature(CALL_HIERARCHY_INCOMING_CALLS)
        def f2(
            params: CallHierarchyIncomingCallsParams
        ) -> Optional[List[CallHierarchyIncomingCall]]:
            return [
                CallHierarchyIncomingCall(
                    from_=params.item,
                    from_ranges=[
                        Range(
                            start=Position(line=2, character=2),
                            end=Position(line=3, character=3),
                        ),
                    ],
                ),
            ]

        @self.server.feature(CALL_HIERARCHY_OUTGOING_CALLS)
        def f3(
            params: CallHierarchyOutgoingCallsParams
        ) -> Optional[List[CallHierarchyOutgoingCall]]:
            return [
                CallHierarchyOutgoingCall(
                    to=params.item,
                    from_ranges=[
                        Range(
                            start=Position(line=3, character=3),
                            end=Position(line=4, character=4),
                        ),
                    ],
                ),
            ]


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities
    assert capabilities.call_hierarchy_provider


@ConfiguredLS.decorate()
def test_call_hierarchy_prepare_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_PREPARE_CALL_HIERARCHY,
        CallHierarchyPrepareParams(
            text_document=TextDocumentIdentifier(uri='file://return.list'),
            position=Position(line=0, character=0),
        )
    ).result()

    check_call_hierarchy_item_response(response[0])


@ConfiguredLS.decorate()
def test_call_hierarchy_prepare_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_PREPARE_CALL_HIERARCHY,
        CallHierarchyPrepareParams(
            text_document=TextDocumentIdentifier(uri='file://return.none'),
            position=Position(line=0, character=0),
        )
    ).result()

    assert response is None


@ConfiguredLS.decorate()
def test_call_hierarchy_incoming_calls_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        CALL_HIERARCHY_INCOMING_CALLS,
        CallHierarchyIncomingCallsParams(item=CALL_HIERARCHY_ITEM)
    ).result()

    item = response[0]

    check_call_hierarchy_item_response(item.from_)

    assert item.from_ranges[0].start.line == 2
    assert item.from_ranges[0].start.character == 2
    assert item.from_ranges[0].end.line == 3
    assert item.from_ranges[0].end.character == 3


@ConfiguredLS.decorate()
def test_call_hierarchy_outgoing_calls_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        CALL_HIERARCHY_OUTGOING_CALLS,
        CallHierarchyOutgoingCallsParams(item=CALL_HIERARCHY_ITEM)
    ).result()

    item = response[0]

    check_call_hierarchy_item_response(item.to)

    assert item.from_ranges[0].start.line == 3
    assert item.from_ranges[0].start.character == 3
    assert item.from_ranges[0].end.line == 4
    assert item.from_ranges[0].end.character == 4

