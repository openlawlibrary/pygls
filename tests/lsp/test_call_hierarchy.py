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
import unittest
from typing import List, Optional

from pygls.lsp.methods import (TEXT_DOCUMENT_CALL_HIERARCHY_INCOMING_CALLS,
                               TEXT_DOCUMENT_CALL_HIERARCHY_OUTGOING_CALLS,
                               TEXT_DOCUMENT_CALL_HIERARCHY_PREPARE)
from pygls.lsp.types import (CallHierarchyIncomingCall, CallHierarchyIncomingCallsParams,
                             CallHierarchyItem, CallHierarchyOptions, CallHierarchyOutgoingCall,
                             CallHierarchyOutgoingCallsParams, CallHierarchyPrepareParams,
                             Position, Range, SymbolKind, SymbolTag, TextDocumentIdentifier)

from ..conftest import CALL_TIMEOUT, ClientServer

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
        assert item['name'] == 'test_name'
        assert item['kind'] == SymbolKind.File
        assert item['uri'] == 'test_uri'
        assert item['range']['start']['line'] == 0
        assert item['range']['start']['character'] == 0
        assert item['range']['end']['line'] == 1
        assert item['range']['end']['character'] == 1
        assert item['selectionRange']['start']['line'] == 1
        assert item['selectionRange']['start']['character'] == 1
        assert item['selectionRange']['end']['line'] == 2
        assert item['selectionRange']['end']['character'] == 2
        assert len(item['tags']) == 1
        assert item['tags'][0] == SymbolTag.Deprecated
        assert item['detail'] == 'test_detail'
        assert item['data'] == 'test_data'


class TestCallHierarchy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server


        @cls.server.feature(
            TEXT_DOCUMENT_CALL_HIERARCHY_PREPARE,
            CallHierarchyOptions(),
        )
        def f(params: CallHierarchyPrepareParams) -> Optional[List[CallHierarchyItem]]:
            if params.text_document.uri == 'file://return.list':
                return [CALL_HIERARCHY_ITEM]
            else:
                return None

        @cls.server.feature(TEXT_DOCUMENT_CALL_HIERARCHY_INCOMING_CALLS)
        def f(params: CallHierarchyIncomingCallsParams) -> Optional[List[CallHierarchyIncomingCall]]:
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

        @cls.server.feature(TEXT_DOCUMENT_CALL_HIERARCHY_OUTGOING_CALLS)
        def f(params: CallHierarchyOutgoingCallsParams) -> Optional[List[CallHierarchyOutgoingCall]]:
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

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.call_hierarchy_provider

    def test_call_hierarchy_prepare_return_list(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_CALL_HIERARCHY_PREPARE,
            CallHierarchyPrepareParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                position=Position(line=0, character=0),
            )
        ).result(timeout=CALL_TIMEOUT)

        check_call_hierarchy_item_response(response[0])

    def test_call_hierarchy_prepare_return_none(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_CALL_HIERARCHY_PREPARE,
            CallHierarchyPrepareParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None

    def test_call_hierarchy_incoming_calls_return_list(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_CALL_HIERARCHY_INCOMING_CALLS,
            CallHierarchyIncomingCallsParams(item=CALL_HIERARCHY_ITEM)
        ).result(timeout=CALL_TIMEOUT)

        item = response[0]

        check_call_hierarchy_item_response(item['from'])

        assert item['fromRanges'][0]['start']['line'] == 2
        assert item['fromRanges'][0]['start']['character'] == 2
        assert item['fromRanges'][0]['end']['line'] == 3
        assert item['fromRanges'][0]['end']['character'] == 3

    def test_call_hierarchy_outgoing_calls_return_list(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_CALL_HIERARCHY_OUTGOING_CALLS,
            CallHierarchyOutgoingCallsParams(item=CALL_HIERARCHY_ITEM)
        ).result(timeout=CALL_TIMEOUT)

        item = response[0]

        check_call_hierarchy_item_response(item['to'])

        assert item['fromRanges'][0]['start']['line'] == 3
        assert item['fromRanges'][0]['start']['character'] == 3
        assert item['fromRanges'][0]['end']['line'] == 4
        assert item['fromRanges'][0]['end']['character'] == 4


if __name__ == '__main__':
    unittest.main()
