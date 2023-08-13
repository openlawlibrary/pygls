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


async def test_completion(
    json_server_client: Tuple[LanguageClient, types.InitializeResult],
    uri_for,
):
    """Ensure that the completion methods are working as expected."""
    client, initialize_result = json_server_client

    completion_provider = initialize_result.capabilities.completion_provider
    assert completion_provider
    assert completion_provider.trigger_characters == [","]
    assert completion_provider.all_commit_characters == [":"]

    test_uri = uri_for("example.json")
    assert test_uri is not None

    response = await client.text_document_completion_async(
        types.CompletionParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            position=types.Position(line=0, character=0),
        )
    )

    labels = {i.label for i in response.items}
    assert labels == set(['"', "[", "]", "{", "}"])
