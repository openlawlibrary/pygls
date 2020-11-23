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
from typing import Optional

from pygls.lsp.methods import SIGNATURE_HELP
from pygls.lsp.types import (ParameterInformation, Position, SignatureHelp, SignatureHelpContext,
                             SignatureHelpOptions, SignatureHelpParams, SignatureHelpTriggerKind,
                             SignatureInformation, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestSignatureHelp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            SIGNATURE_HELP,
            SignatureHelpOptions(
                trigger_characters=['a', 'b'],
                retrigger_characters=['c', 'd'],
            ),
        )
        def f(params: SignatureHelpParams) -> Optional[SignatureHelp]:
            if params.text_document.uri == 'file://return.signature_help':
                return SignatureHelp(
                    signatures=[
                        SignatureInformation(
                            label='label',
                            documentation='documentation',
                            parameters=[
                                ParameterInformation(
                                    label=(0, 0),
                                    documentation='documentation',
                                ),
                            ]
                        ),
                    ],
                    active_signature=0,
                    active_parameter=0,
                )
            else:
                return None

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.signature_help_provider
        assert capabilities.signature_help_provider.trigger_characters == ['a', 'b']
        assert capabilities.signature_help_provider.retrigger_characters == ['c', 'd']

    def test_signature_help_return_signature_help(self):
        response = self.client.lsp.send_request(
            SIGNATURE_HELP,
            SignatureHelpParams(
                text_document=TextDocumentIdentifier(uri='file://return.signature_help'),
                position=Position(line=0, character=0),
                context=SignatureHelpContext(
                    trigger_kind=SignatureHelpTriggerKind.TriggerCharacter,
                    is_retrigger=True,
                    trigger_character='a',
                    active_signature_help=SignatureHelp(
                        signatures=[
                            SignatureInformation(
                                label='label',
                                documentation='documentation',
                                parameters=[
                                    ParameterInformation(
                                        label=(0, 0),
                                        documentation='documentation',
                                    ),
                                ]
                            ),
                        ],
                        active_signature=0,
                        active_parameter=0,
                    ),
                ),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['activeParameter'] == 0
        assert response['activeSignature'] == 0

        assert response['signatures'][0]['label'] == 'label'
        assert response['signatures'][0]['documentation'] == 'documentation'
        assert response['signatures'][0]['parameters'][0]['label'] == [0, 0]
        assert response['signatures'][0]['parameters'][0]['documentation'] == 'documentation'

    def test_signature_help_return_none(self):
        response = self.client.lsp.send_request(
            SIGNATURE_HELP,
            SignatureHelpParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
                context=SignatureHelpContext(
                    trigger_kind=SignatureHelpTriggerKind.TriggerCharacter,
                    is_retrigger=True,
                    trigger_character='a',
                    active_signature_help=SignatureHelp(
                        signatures=[
                            SignatureInformation(
                                label='label',
                                documentation='documentation',
                                parameters=[
                                    ParameterInformation(
                                        label=(0, 0),
                                        documentation='documentation',
                                    ),
                                ]
                            ),
                        ],
                        active_signature=0,
                        active_parameter=0,
                    ),
                ),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None


if __name__ == '__main__':
    unittest.main()

