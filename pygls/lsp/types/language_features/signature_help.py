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
from typing import List, Optional, Tuple, Union

from pygls.lsp.types.basic_structures import (MarkupContent, MarkupKind, Model, NumType,
                                              TextDocumentPositionParams, WorkDoneProgressOptions,
                                              WorkDoneProgressParams)


class SignatureHelpInformationParameterInformationClientCapabilities(Model):
    label_offset_support: Optional[bool] = False


class SignatureHelpInformationClientCapabilities(Model):
    documentation_format: Optional[List[MarkupKind]] = None
    parameter_information: Optional[SignatureHelpInformationParameterInformationClientCapabilities] = None


class SignatureHelpClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False
    signature_information: Optional[SignatureHelpInformationClientCapabilities] = None
    context_support: Optional[bool] = False


class SignatureHelpOptions(WorkDoneProgressOptions):
    trigger_characters: Optional[List[str]] = None
    retrigger_characters: Optional[List[str]] = None


class SignatureHelpTriggerKind(enum.IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    ContentChange = 3


class ParameterInformation(Model):
    label: Union[str, Tuple[int, int]]
    documentation: Optional[Union[str, MarkupContent]] = None


class SignatureInformation(Model):
    label: str
    documentation: Optional[Union[str, MarkupContent]] = None
    parameters: Optional[List[ParameterInformation]] = None


class SignatureHelp(Model):
    signatures: List[SignatureInformation]
    active_signature: Optional[NumType] = None
    active_parameter: Optional[NumType] = None


class SignatureHelpContext(Model):
    trigger_kind: SignatureHelpTriggerKind
    is_retrigger: bool
    trigger_character: Optional[str] = None
    active_signature_help: Optional[SignatureHelp] = None


class SignatureHelpParams(TextDocumentPositionParams, WorkDoneProgressParams):
    context: Optional[SignatureHelpContext] = None
