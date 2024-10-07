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
"""This implements the various semantic token requests from the specification

Tokens are sent to the client as a long list of numbers, each group of 5 numbers describe
a single token.

- The first 3 numbers describe the token's line number, character index and length,
  **relative to the start of the previous token**
- Thr 4th number describes a token's type
- The 5th number specifies zero or more modifiers to apply to a token

.. seealso::

   :ref:`howto-semantic-tokens`
      For a detailed guide on how tokens are represented
"""

import enum
import logging
import operator
import re
from functools import reduce
from typing import Dict
from typing import List
from typing import Optional

import attrs
from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument


class TokenModifier(enum.IntFlag):
    deprecated = enum.auto()
    readonly = enum.auto()
    defaultLibrary = enum.auto()
    definition = enum.auto()


@attrs.define
class Token:
    line: int
    offset: int
    text: str

    tok_type: str = ""
    tok_modifiers: List[TokenModifier] = attrs.field(factory=list)


TokenTypes = ["keyword", "variable", "function", "operator", "parameter", "type"]

SYMBOL = re.compile(r"\w+")
OP = re.compile(r"->|[\{\}\(\)\.,+:*-=]")
SPACE = re.compile(r"\s+")

KEYWORDS = {"type", "fn"}


def is_type(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == "type" and token.tok_type == "keyword"


def is_fn(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == "fn" and token.tok_type == "keyword"


def is_lparen(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == "(" and token.tok_type == "operator"


def is_rparen(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == ")" and token.tok_type == "operator"


def is_lbrace(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == "{" and token.tok_type == "operator"


def is_rbrace(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == "}" and token.tok_type == "operator"


def is_colon(token: Optional[Token]) -> bool:
    if token is None:
        return False

    return token.text == ":" and token.tok_type == "operator"


class SemanticTokensServer(LanguageServer):
    """Language server demonstrating the semantic token methods from the LSP
    specification."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokens: Dict[str, List[Token]] = {}

    def parse(self, doc: TextDocument):
        """Convert the given document into a list of tokens"""
        tokens = self.lex(doc)
        self.classify_tokens(tokens)

        # logging.info("%s", tokens)
        self.tokens[doc.uri] = tokens

    def classify_tokens(self, tokens: List[Token]):
        """Given a list of tokens, determine their type and modifiers."""

        def prev(idx):
            """Get the previous token, if possible"""
            if idx < 0:
                return None

            return tokens[idx - 1]

        def next(idx):
            """Get the next token, if possible"""
            if idx >= len(tokens) - 1:
                return None

            return tokens[idx + 1]

        in_brace = False
        in_paren = False

        for idx, token in enumerate(tokens):
            if token.tok_type == "operator":
                if is_lparen(token):
                    in_paren = True

                elif is_rparen(token):
                    in_paren = False

                elif is_lbrace(token):
                    in_brace = True

                elif is_rbrace(token):
                    in_brace = False

                continue

            if token.text in KEYWORDS:
                token.tok_type = "keyword"

            elif token.text[0].isupper():
                token.tok_type = "type"

                if is_type(prev(idx)):
                    token.tok_modifiers.append(TokenModifier.definition)

            elif is_fn(prev(idx)) or is_lparen(next(idx)):
                token.tok_type = "function"
                token.tok_modifiers.append(TokenModifier.definition)

            elif is_colon(next(idx)) and in_brace:
                token.tok_type = "parameter"

            elif is_colon(prev(idx)) and in_paren:
                token.tok_type = "type"
                token.tok_modifiers.append(TokenModifier.defaultLibrary)

            else:
                token.tok_type = "variable"

    def lex(self, doc: TextDocument) -> List[Token]:
        """Convert the given document into a list of tokens"""
        tokens = []

        prev_line = 0
        prev_offset = 0

        for current_line, line in enumerate(doc.lines):
            prev_offset = current_offset = 0
            chars_left = len(line)

            while line:
                if (match := SPACE.match(line)) is not None:
                    # Skip whitespace
                    current_offset += len(match.group(0))
                    line = line[match.end() :]

                elif (match := SYMBOL.match(line)) is not None:
                    tokens.append(
                        Token(
                            line=current_line - prev_line,
                            offset=current_offset - prev_offset,
                            text=match.group(0),
                        )
                    )

                    line = line[match.end() :]
                    prev_offset = current_offset
                    prev_line = current_line
                    current_offset += len(match.group(0))

                elif (match := OP.match(line)) is not None:
                    tokens.append(
                        Token(
                            line=current_line - prev_line,
                            offset=current_offset - prev_offset,
                            text=match.group(0),
                            tok_type="operator",
                        )
                    )

                    line = line[match.end() :]
                    prev_offset = current_offset
                    prev_line = current_line
                    current_offset += len(match.group(0))

                else:
                    raise RuntimeError(f"No match: {line!r}")

                # Make sure we don't hit an infinite loop
                if (n := len(line)) == chars_left:
                    raise RuntimeError("Inifite loop detected")
                else:
                    chars_left = n

        return tokens


server = SemanticTokensServer("semantic-tokens-server", "v1")


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: SemanticTokensServer, params: types.DidOpenTextDocumentParams):
    """Parse each document when it is opened"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: SemanticTokensServer, params: types.DidOpenTextDocumentParams):
    """Parse each document when it is changed"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(
    types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    types.SemanticTokensLegend(
        token_types=TokenTypes,
        token_modifiers=[m.name for m in TokenModifier],
    ),
)
def semantic_tokens_full(ls: SemanticTokensServer, params: types.SemanticTokensParams):
    """Return the semantic tokens for the entire document"""
    data = []
    tokens = ls.tokens.get(params.text_document.uri, [])

    for token in tokens:
        data.extend(
            [
                token.line,
                token.offset,
                len(token.text),
                TokenTypes.index(token.tok_type),
                reduce(operator.or_, token.tok_modifiers, 0),
            ]
        )

    return types.SemanticTokens(data=data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
