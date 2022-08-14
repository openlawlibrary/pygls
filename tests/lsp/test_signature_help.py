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

from typing import Optional

import pytest

from lsprotocol.types import TEXT_DOCUMENT_SIGNATURE_HELP
from lsprotocol.types import (
    ParameterInformation,
    Position,
    SignatureHelp,
    SignatureHelpContext,
    SignatureHelpOptions,
    SignatureHelpParams,
    SignatureHelpTriggerKind,
    SignatureInformation,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_SIGNATURE_HELP,
            SignatureHelpOptions(
                trigger_characters=["a", "b"],
                retrigger_characters=["c", "d"],
            ),
        )
        def f(params: SignatureHelpParams) -> Optional[SignatureHelp]:
            if params.text_document.uri == "file://return.signature_help":
                return SignatureHelp(
                    signatures=[
                        SignatureInformation(
                            label="label",
                            documentation="documentation",
                            parameters=[
                                ParameterInformation(
                                    label=(0, 0),
                                    documentation="documentation",
                                ),
                            ],
                        ),
                    ],
                    active_signature=0,
                    active_parameter=0,
                )
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    provider = capabilities.signature_help_provider
    assert provider
    assert provider.trigger_characters == ["a", "b"]
    assert provider.retrigger_characters == ["c", "d"]


@ConfiguredLS.decorate()
@pytest.mark.skip
def test_signature_help_return_signature_help(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_SIGNATURE_HELP,
        SignatureHelpParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.signature_help"
            ),
            position=Position(line=0, character=0),
            context=SignatureHelpContext(
                trigger_kind=SignatureHelpTriggerKind.TriggerCharacter,
                is_retrigger=True,
                trigger_character="a",
                active_signature_help=SignatureHelp(
                    signatures=[
                        SignatureInformation(
                            label="label",
                            documentation="documentation",
                            parameters=[
                                ParameterInformation(
                                    label=(0, 0),
                                    documentation="documentation",
                                ),
                            ],
                        ),
                    ],
                    active_signature=0,
                    active_parameter=0,
                ),
            ),
        ),
    ).result()

    assert response

    assert response["activeParameter"] == 0
    assert response["activeSignature"] == 0

    assert response["signatures"][0]["label"] == "label"
    assert response["signatures"][0]["documentation"] == "documentation"
    assert response["signatures"][0]["parameters"][0]["label"] == [0, 0]
    assert (
        response["signatures"][0]["parameters"][0]["documentation"]
        == "documentation"
    )


@ConfiguredLS.decorate()
@pytest.mark.skip
def test_signature_help_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_SIGNATURE_HELP,
        SignatureHelpParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
            context=SignatureHelpContext(
                trigger_kind=SignatureHelpTriggerKind.TriggerCharacter,
                is_retrigger=True,
                trigger_character="a",
                active_signature_help=SignatureHelp(
                    signatures=[
                        SignatureInformation(
                            label="label",
                            documentation="documentation",
                            parameters=[
                                ParameterInformation(
                                    label=(0, 0),
                                    documentation="documentation",
                                ),
                            ],
                        ),
                    ],
                    active_signature=0,
                    active_parameter=0,
                ),
            ),
        ),
    ).result()

    assert response is None
