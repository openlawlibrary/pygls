############################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.                 #
# Original work licensed under the MIT License.                            #
# See ThirdPartyNotices.txt in the project root for license information.   #
# All modifications Copyright (c) Open Law Library. All rights reserved.   #
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
"""This module contains Language Server Protocol types
https://microsoft.github.io/language-server-protocol/specification

-- Language Features - Signature Help --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import Any, List, Optional, Tuple, Union

from pygls.types.basic_structures import (MarkupContent, MarkupKind, NumType, Position,
                                          ProgressToken, Range, TextDocumentIdentifier,
                                          TextDocumentPositionParams, WorkDoneProgressOptions,
                                          WorkDoneProgressParams)


class SignatureHelpClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 signature_information: Optional['SignatureHelpInformationClientCapabilities'] = None,
                 contextSupport: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.signatureInformation = signature_information


class SignatureHelpInformationClientCapabilities:
    def __init__(self,
                 documentation_format: Optional[List[MarkupKind]] = None,
                 parameter_information: Optional['SignatureHelpInformationParameterInformationClientCapabilities'] = None):
        self.documentationFormat = documentation_format
        self.parameterInformation = parameter_information


class SignatureHelpInformationParameterInformationClientCapabilities:
    def __init__(self, label_offset_support: Optional[bool] = False):
        self.labelOffsetSupport = label_offset_support


class SignatureHelpOptions(WorkDoneProgressOptions):
    def __init__(self,
                 trigger_characters: Optional[List[str]] = None,
                 retrigger_characters: Optional[List[str]] = None,
                 work_done_progress: Optional[ProgressToken] = None
                 ):
        super().__init__(work_done_progress)
        self.triggerCharacters = trigger_characters
        self.retriggerCharacters = retrigger_characters


class SignatureHelpParams(TextDocumentPositionParams, WorkDoneProgressParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position,
                 work_done_token: Optional[bool] = None,
                 context: Optional['SignatureHelpContext'] = None):
        TextDocumentPositionParams.__init__(self, text_document, position)
        WorkDoneProgressParams.__init__(self, work_done_token)
        self.context = context


class SignatureHelpTriggerKind(enum.IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    ContentChange = 3


class SignatureHelpContext:
    def __init__(self,
                 trigger_kind: SignatureHelpTriggerKind,
                 is_retrigger: bool,
                 trigger_character: Optional[str] = None,
                 active_signature_help: Optional['SignatureHelp'] = None):
        self.triggerKind = trigger_kind
        self.isRetrigger = is_retrigger
        self.triggerCharacter = trigger_character
        self.activeSignatureHelp = active_signature_help


class SignatureHelp:
    def __init__(self,
                 signatures: List[SignatureInformation],
                 active_signature: Optional[NumType] = None,
                 active_parameter: Optional[NumType] = None):
        self.signatures = signatures
        self.activeSignature = active_signature
        self.activeParameter = active_parameter


class SignatureInformation:
    def __init__(self,
                 label: str,
                 documentation: Optional[Union[str, MarkupContent]] = None,
                 parameters: Optional[List['ParameterInformation']] = None):
        self.label = label
        self.documentation = documentation
        self.pararmeters = parameters


class ParameterInformation:
    def __init__(self,
                 label: Union[str, Tuple[int, int]],
                 documentation: Optional[Union[str, MarkupContent]] = None):
        self.label = label
        self.documentation = documentation
