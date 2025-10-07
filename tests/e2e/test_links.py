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
from __future__ import annotations

import typing

import pytest
import pytest_asyncio
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def links(get_client_for):
    async for result in get_client_for("links.py"):
        yield result


def range_from_str(range_: str) -> types.Range:
    start, end = range_.split("-")
    start_line, start_char = start.split(":")
    end_line, end_char = end.split(":")

    return types.Range(
        start=types.Position(line=int(start_line), character=int(start_char)),
        end=types.Position(line=int(end_line), character=int(end_char)),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_document_link(
    links: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example links server is working as expected."""
    client, initialize_result = links

    document_link_options = initialize_result.capabilities.document_link_provider
    assert document_link_options.resolve_provider is True

    test_uri = uri_for("links.txt")
    response = await client.text_document_document_link_async(
        types.DocumentLinkParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri)
        )
    )

    assert tuple(response) == (
        types.DocumentLink(
            range=range_from_str("0:6-0:35"),
            data=dict(type="github", target="openlawlibrary/pygls"),
        ),
        types.DocumentLink(
            range=range_from_str("1:30-1:42"),
            data=dict(type="pypi", target="pygls"),
        ),
        types.DocumentLink(
            range=range_from_str("1:73-1:90"),
            data=dict(type="pypi", target="lsprotocol"),
        ),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_document_link_resolve(
    links: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the server can resolve document links correctly."""

    client, _ = links
    link = types.DocumentLink(
        range=range_from_str("0:6-0:35"),
        data=dict(type="github", target="openlawlibrary/pygls"),
    )

    response = await client.document_link_resolve_async(link)

    assert response == types.DocumentLink(
        range=range_from_str("0:6-0:35"),
        target="https://github.com/openlawlibrary/pygls",
        tooltip="Github - openlawlibrary/pygls",
        data=dict(type="github", target="openlawlibrary/pygls"),
    )
