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
from typing import Tuple

from lsprotocol import types

from ..client import LanguageClient


async def test_code_actions(
    code_action_client: Tuple[LanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example code action server is working as expected."""
    client, initialize_result = code_action_client

    code_action_options = initialize_result.capabilities.code_action_provider
    assert code_action_options.code_action_kinds == [types.CodeActionKind.QuickFix]

    test_uri = uri_for("sums.txt")
    assert test_uri is not None

    response = await client.text_document_code_action_async(
        types.CodeActionParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=types.Position(line=1, character=0),
            ),
            context=types.CodeActionContext(diagnostics=[]),
        )
    )

    assert len(response) == 1
    code_action = response[0]

    assert code_action.title == "Evaluate '1 + 1 ='"
    assert code_action.kind == types.CodeActionKind.QuickFix

    fix = code_action.edit.changes[test_uri][0]
    expected_range = types.Range(
        start=types.Position(line=0, character=0),
        end=types.Position(line=0, character=7),
    )

    assert fix.range == expected_range
    assert fix.new_text == "1 + 1 = 2!"
