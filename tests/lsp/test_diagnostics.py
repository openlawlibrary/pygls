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
import json
from typing import Tuple

from lsprotocol import types


from ..client import LanguageClient


async def test_diagnostics(
    json_server_client: Tuple[LanguageClient, types.InitializeResult],
    uri_for,
):
    """Ensure that diagnostics are working as expected."""
    client, _ = json_server_client

    test_uri = uri_for("example.json")
    assert test_uri is not None

    # Get the expected error message
    document_content = "text"
    try:
        json.loads(document_content)
    except json.JSONDecodeError as err:
        expected_message = err.msg

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri=test_uri, language_id="json", version=1, text=document_content
            )
        )
    )

    await client.wait_for_notification(types.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)

    diagnostics = client.diagnostics[test_uri]
    assert diagnostics[0].message == expected_message

    result = await client.text_document_diagnostic_async(
        types.DocumentDiagnosticParams(
            text_document=types.TextDocumentIdentifier(test_uri)
        )
    )
    diagnostics = result.items
    assert diagnostics[0].message == expected_message
