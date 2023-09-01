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


async def test_inline_value(
    json_server_client: Tuple[LanguageClient, types.InitializeResult],
    uri_for,
):
    """Ensure that inline values are working as expected."""
    client, _ = json_server_client

    test_uri = uri_for("example.json")
    assert test_uri is not None

    document_content = '{\n"foo": "bar"\n}'
    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri=test_uri, language_id="json", version=1, text=document_content
            )
        )
    )

    result = await client.text_document_inline_value_async(
        types.InlineValueParams(
            text_document=types.TextDocumentIdentifier(test_uri),
            range=types.Range(
                start=types.Position(line=1, character=0),
                end=types.Position(line=1, character=6),
            ),
            context=types.InlineValueContext(
                frame_id=1,
                stopped_location=types.Range(
                    start=types.Position(line=1, character=0),
                    end=types.Position(line=1, character=6),
                ),
            ),
        )
    )
    assert result[0].text == "Inline value"
