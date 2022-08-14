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
from typing import Optional, Union

from lsprotocol.types import (
    TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE,
)
from lsprotocol.types import (
    SemanticTokens,
    SemanticTokensParams,
    SemanticTokensPartialResult,
)

from ...conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_RANGE)
        def f(
            params: SemanticTokensParams,
        ) -> Union[SemanticTokensPartialResult, Optional[SemanticTokens]]:
            return SemanticTokens(data=[0, 0, 3, 0, 0])


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.semantic_tokens_provider is None
