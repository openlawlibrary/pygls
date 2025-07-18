# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import importlib.metadata
import os
import pathlib
import re
import sys

from docutils import nodes

sys.path.insert(0, os.path.abspath("./ext"))


# -- Project information -----------------------------------------------------

project = "pygls"
copyright = "Open Law Library"
author = "Open Law Library"

# The short X.Y version
version = importlib.metadata.version("pygls")
# The full version, including alpha/beta/rc tags
release = version

title = "pygls Documentation"
description = "a pythonic generic language server"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Built-in extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    # 3rd party extensions
    "myst_parser",
    "sphinx_design",
    # Local extensions
    "examples",
]

autodoc_member_order = "groupwise"
autodoc_typehints = "description"
autodoc_typehints_description_target = "all"

example_server_dir = (
    pathlib.Path(__file__).parent.parent.parent / "examples" / "servers"
)

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pyodide": ("https://pyodide.org/en/stable", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_title = f"pygls v{version}"
html_theme_options = {
    "source_repository": "https://github.com/openlawlibrary/pygls/",
    "source_branch": "main",
    "source_directory": "docs/source",
    "announcement": (
        "This is the documentation for the in-development v2.0 release of pygls. "
        '<a href="/en/stable">Click here</a> to view the documentation for the current stable version'
    ),
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "pyglsdoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "pygls.tex", title, author, "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "pygls", description, [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, "pygls", title, author, "pygls", description, "Miscellaneous"),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


def lsp_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Link to sections within the lsp specification."""

    anchor = text.replace("$/", "").replace("/", "_")
    ref = f"https://microsoft.github.io/language-server-protocol/specification.html#{anchor}"

    node = nodes.reference(rawtext, text, refuri=ref, **options)
    return [node], []


CODE_FENCE_PATTERN = re.compile(r"```(\w+)?")
LINK_PATTERN = re.compile(r"\{@link ([^}]+)\}")
LITERAL_PATTERN = re.compile(r"(?<![`:])`([^`]+)`(?!_)")
MD_LINK_PATTERN = re.compile(r"\[`?([^\]]+?)`?\]\(([^)]+)\)")
SINCE_PATTERN = re.compile(r"@since ([\d\.]+)")


def process_docstring(app, what, name, obj, options, lines):
    """Fixup LSP docstrings so that they work with reStructuredText syntax

    - Replaces ``@since <version>`` with ``**LSP v<version>**``

    - Replaces ``{@link <item>}`` with ``:class:`~lsprotocol.types.<item>` ``

    - Replaces markdown hyperlink with reStructuredText equivalent

    - Replaces inline markdown code (single "`") with reStructuredText inline code
      (double "`")

    - Inserts the required newline before a bulleted list

    - Replaces code fences with code blocks

    - Fixes indentation
    """

    line_breaks = []
    code_fences = []

    for i, line in enumerate(lines):
        if line.startswith("- "):
            line_breaks.append(i)

        # Does the line need dedenting?
        if line.startswith(" " * 4) and not lines[i - 1].startswith(" "):
            # Be sure to modify the original list *and* the line the rest of the
            # loop will use.
            line = lines[i][4:]
            lines[i] = line

        if (match := SINCE_PATTERN.search(line)) is not None:
            start, end = match.span()
            lines[i] = "".join([line[:start], f"**LSP v{match.group(1)}**", line[end:]])

        if (match := LINK_PATTERN.search(line)) is not None:
            start, end = match.span()
            item = match.group(1)

            lines[i] = "".join(
                [line[:start], f":class:`~lsprotocol.types.{item}`", line[end:]]
            )

        if (match := MD_LINK_PATTERN.search(line)) is not None:
            start, end = match.span()
            text = match.group(1)
            target = match.group(2)

            line = "".join([line[:start], f"`{text} <{target}>`__", line[end:]])
            lines[i] = line

        if (match := LITERAL_PATTERN.search(line)) is not None:
            start, end = match.span()
            lines[i] = "".join([line[:start], f"`{match.group(0)}` ", line[end:]])

        if (match := CODE_FENCE_PATTERN.match(line)) is not None:
            open_ = len(code_fences) % 2 == 0
            lang = match.group(1) or ""

            if open_:
                code_fences.append((i, lang))
                line_breaks.extend([i, i + 1])
            else:
                code_fences.append(i)

    # Rewrite fenced code blocks
    open_ = -1
    for fence in code_fences:
        if isinstance(fence, tuple):
            open_ = fence[0] + 1
            lines[fence[0]] = f".. code-block:: {fence[1]}"
        else:
            # Indent content
            for j in range(open_, fence):
                lines[j] = f"   {lines[j]}"

            lines[fence] = ""

    # Insert extra line breaks
    for offset, line in enumerate(line_breaks):
        lines.insert(line + offset, "")


def setup(app):
    app.add_role("lsp", lsp_role)
    app.connect("autodoc-process-docstring", process_docstring)
