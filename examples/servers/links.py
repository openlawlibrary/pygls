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
"""This implements the :lsp:`textDocument/documentLink` and :lsp:`documentLink/resolve`
requests.

These allow you to add support for custom link syntax to your language.
In editors like VSCode, links will often be underlined and can be opened with a
:kbd:`Ctrl+Click`.

This server scans the document given to ``textDocument/documentLink`` for the
syntax ``<LINK_TYPE:PATH>`` and returns a document link desribing its location.
While we could easily compute the ``target`` and ``tooltip`` fields in the same
method, this example demonstrates how the ``documentLink/resolve`` method can be used
to defer this until it is actually necessary
"""

import logging
import re

from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer

LINK = re.compile(r"<(\w+):([^>]+)>")
server = LanguageServer("links-server", "v1")


@server.feature(
    types.TEXT_DOCUMENT_DOCUMENT_LINK,
)
def document_links(params: types.DocumentLinkParams):
    """Return a list of links contained in the document."""
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    for linum, line in enumerate(document.lines):
        for match in LINK.finditer(line):
            start_char, end_char = match.span()
            items.append(
                types.DocumentLink(
                    range=types.Range(
                        start=types.Position(line=linum, character=start_char),
                        end=types.Position(line=linum, character=end_char),
                    ),
                    data={"type": match.group(1), "target": match.group(2)},
                ),
            )

    return items


LINK_TYPES = {
    "github": ("https://github.com/{}", "Github - {}"),
    "pypi": ("https://pypi.org/project/{}", "PyPi - {}"),
}


@server.feature(types.DOCUMENT_LINK_RESOLVE)
def document_link_resolve(link: types.DocumentLink):
    """Given a link, fill in additional information about it"""
    logging.info("resolving link: %s", link)

    link_type = link.data.get("type", "<unknown>")
    link_target = link.data.get("target", "<unknown>")

    if (link_info := LINK_TYPES.get(link_type, None)) is None:
        logging.error("Unknown link type: '%s'", link_type)
        return link

    url, tooltip = link_info
    link.target = url.format(link_target)
    link.tooltip = tooltip.format(link_target)

    return link


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
