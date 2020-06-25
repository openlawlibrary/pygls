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
from typing import List, Union

import pygls.lsp.methods as m
import pygls.lsp.types as t

# Holds lsp methods and their appropriate types. It is used for type-checking.
# {
#   'COMPLETION': (CompletionOptions, CompletionParams, Union[List[CompletionItem], CompletionList, None])
# }
# where:
#   - CompletionOptions is used when registering a method:
#   - CompletionParams are received from the client
#   - Union[List[CompletionItem], CompletionList, None] should be returned by the server
#
#       @json_server.feature(COMPLETION, CompletionOptions(trigger_characters=[',']))
#       def completions(params: CompletionParams = None) -> Union[List[CompletionItem], CompletionList, None]:
#           """Returns completion items."""
LSP_METHOD_MAP = {
    m.COMPLETION: (
        t.CompletionOptions,
        t.CompletionParams,
        Union[List[t.CompletionItem], t.CompletionList, None],
    ),
}
