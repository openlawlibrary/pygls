"""Documentation for the example servers"""

from __future__ import annotations

import importlib.util as imutil
import os
import pathlib
import typing

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

if typing.TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = getLogger(__name__)


class ExampleServerDirective(SphinxDirective):
    """Automate the process of documenting example servers.

    Currently, this doesn't do *that* much, it

    - Inserts the code using a ``.. literalinclude::`` directive.
    - Extracts the server module's docstring and inserts it into the page as nicely
      rendered text.

    But perhaps we can do something more interesting in the future!
    """

    required_arguments = 1
    option_spec = {
        "start-at": directives.unchanged,
    }

    def get_docstring(self, filename: pathlib.Path):
        """Given the filepath to a module, return its docstring."""

        base = filename.stem
        spec = imutil.spec_from_file_location(f"examples.{base}", filename)

        try:
            module = imutil.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            logger.exception("Unable to import example server")
            return []

        if (docstring := module.__doc__) is not None:
            return docstring.splitlines()

        return []

    def run(self):
        server_dir = self.config.example_server_dir
        name = self.arguments[0]

        if not (filename := pathlib.Path(server_dir, name)).exists():
            raise RuntimeError(f"Unable to find example server: {filename}")

        # Tell Sphinx to rebuild a document if this file changes
        self.env.note_dependency(str(filename))

        # An "absolute" path given to `literalinclude` is actually relative to the
        # projects srcdir
        relpath = os.path.relpath(str(filename), start=str(self.env.app.srcdir))
        content = [
            f".. literalinclude:: /{relpath}",
            "   :language: python",
        ]

        if (start_at := self.options.get("start-at")) is not None:
            content.append(f"   :start-at: {start_at}")

        # Confusingly, these are processed in reverse order...
        self.state_machine.insert_input(content, "<examples>")
        self.state_machine.insert_input(self.get_docstring(filename), str(filename))

        return []


def setup(app: Sphinx):
    app.add_config_value("example_server_dir", "", rebuild="env")
    app.add_directive("example-server", ExampleServerDirective)
