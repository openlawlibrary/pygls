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
from typing import Optional, Union

from pygls.lsp.methods import (TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                               TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL_DELTA,
                               TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE)
from pygls.lsp.types import (Position, Range, SemanticTokens, SemanticTokensDeltaParams, 
                             SemanticTokensLegend, SemanticTokensParams, 
                             SemanticTokensPartialResult, SemanticTokensRequestsFull,
                             SemanticTokensRangeParams, TextDocumentIdentifier)

from ..conftest import CALL_TIMEOUT, ClientServer


class TestSemanticTokensFullMissingLegend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)
        def f(params: SemanticTokensParams) -> Union[SemanticTokensPartialResult, Optional[SemanticTokens]]:
            return SemanticTokens(data=[0,0,3,0,0])

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.semantic_tokens_provider is None


class TestSemanticTokensFull(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
            SemanticTokensLegend(
                token_types=["keyword", "operator"],
                token_modifiers=["readonly"]
            )
        )
        def f(params: SemanticTokensParams) -> Optional[Union[SemanticTokensPartialResult, Optional[SemanticTokens]]]:
            if params.text_document.uri == "file://return.tokens":
                return SemanticTokens(data=[0,0,3,0,0])

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.semantic_tokens_provider.full
        assert capabilities.semantic_tokens_provider.legend.token_types == ["keyword", "operator"]
        assert capabilities.semantic_tokens_provider.legend.token_modifiers == ["readonly"]

    def test_semantic_tokens_full_return_tokens(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
            SemanticTokensParams(
                text_document=TextDocumentIdentifier(uri='file://return.tokens')
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response
        
        assert response['data'] == [0, 0, 3, 0, 0]


    def test_semantic_tokens_full_return_none(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
            SemanticTokensParams(
                text_document=TextDocumentIdentifier(uri='file://return.none')
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None
        

class TestSemanticTokensFullDeltaMissingLegend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL_DELTA)
        def f(params: SemanticTokensDeltaParams) -> Union[SemanticTokensPartialResult, Optional[SemanticTokens]]:
            return SemanticTokens(data=[0,0,3,0,0])

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.semantic_tokens_provider is None
  

class TestSemanticTokensFullDeltaMissingLegend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL_DELTA, 
            SemanticTokensLegend(
                token_types=["keyword", "operator"],
                token_modifiers=["readonly"]
            )
        )
        def f(params: SemanticTokensDeltaParams) -> Union[SemanticTokensPartialResult, Optional[SemanticTokens]]:
            if params.text_document.uri == 'file://return.tokens':
                return SemanticTokens(data=[0,0,3,0,0])

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.semantic_tokens_provider.full == SemanticTokensRequestsFull(delta=True)
        assert capabilities.semantic_tokens_provider.legend.token_types == ["keyword", "operator"]
        assert capabilities.semantic_tokens_provider.legend.token_modifiers == ["readonly"]

    def test_semantic_tokens_full_delta_return_tokens(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL_DELTA,
            SemanticTokensDeltaParams(
                text_document=TextDocumentIdentifier(uri='file://return.tokens'),
                previous_result_id='id'
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response
        
        assert response['data'] == [0, 0, 3, 0, 0]

    def test_semantic_tokens_full_delta_return_none(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL_DELTA,
            SemanticTokensDeltaParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                previous_result_id='id'
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None

class TestSemanticTokensRangeMissingLegend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE)
        def f(params: SemanticTokensParams) -> Union[SemanticTokensPartialResult, Optional[SemanticTokens]]:
            return SemanticTokens(data=[0,0,3,0,0])

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.semantic_tokens_provider is None


class TestSemanticTokensRange(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE,
            SemanticTokensLegend(
                token_types=["keyword", "operator"],
                token_modifiers=["readonly"]
            )
        )
        def f(params: SemanticTokensRangeParams) -> Optional[Union[SemanticTokensPartialResult, Optional[SemanticTokens]]]:
            if params.text_document.uri == "file://return.tokens":
                return SemanticTokens(data=[0,0,3,0,0])

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.semantic_tokens_provider.range
        assert capabilities.semantic_tokens_provider.legend.token_types == ["keyword", "operator"]
        assert capabilities.semantic_tokens_provider.legend.token_modifiers == ["readonly"]

    def test_semantic_tokens_range_return_tokens(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE,
            SemanticTokensRangeParams(
                text_document=TextDocumentIdentifier(uri='file://return.tokens'),
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=80)
                )
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response
        
        assert response['data'] == [0, 0, 3, 0, 0]


    def test_semantic_tokens_range_return_none(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE,
            SemanticTokensRangeParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=80)
                )
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None        