"""Script for generating the interactive semantic token display for the docs."""

from __future__ import annotations

import argparse
import enum
import operator
import pathlib
import string
import textwrap
import typing
from dataclasses import dataclass, field
from functools import reduce

if typing.TYPE_CHECKING:
    from typing import List, Optional, Tuple, Type


class TokenModifier(enum.IntFlag):
    """Represents a token modifier"""

    deprecated = enum.auto()
    readonly = enum.auto()
    defaultLibrary = enum.auto()
    definition = enum.auto()


@dataclass
class Token:
    line: int
    offset: int
    text: str

    tok_type: str
    tok_modifiers: List[TokenModifier] = field(default_factory=list)

    @property
    def tok_id(self):
        return f"tok-{self.text}-{id(self)}"

    def __iter__(self):
        return iter(self.text)

    def __len__(self):
        return len(self.text)


POSITIONS_LAYOUT = string.Template(
    """\
<div id="tok-positions" style="display: flex; justify-content: space-between;">
  <div style="flex-grow: 1;">
    <ul style="display: grid; grid-template-columns: repeat(4, 1fr); margin-right: 1em;">
      <li>
        <span>Token</span>
        <span>Line</span>
        <span>Offset</span>
        <span>Length</span>
      </li>
${tokenList}
    </ul>
  </div>
  <div style="display: flex; gap: 1em; flex-direction: column;">
    <table style="font-family: monospace; font-size: 24px; align-self: flex-start;">
      <tbody>
${table}
      </tbody>
    </table>
    <div id="tok-positions-calcs">
${tokenCalcs}
    </div>
  </div>
</div>
<style>
  #tok-positions {
    --tok-border-color: gray;
    --tok-highlight-color: lightgray;
    --tok-before-color: olive;
    --tok-after-color: blue;
  }

  #tok-positions .index {
    color: var(--tok-border-color);
    font-size: 18px;
    text-align: center;
    vertical-align: middle;
  }

  #tok-positions .char {
    border: dashed 1px lightgray;
    text-align: center;
    width: 1em;
  }

  #tok-positions li {
    display: grid;
    grid-template-columns: subgrid;
    align-items: baseline;
    grid-column: span 4;
    margin: 0;
  }

  #tok-positions span {
    margin: 0;
    padding: 0 0.5em;
    justify-self: center;
  }

  #tok-positions-calcs {
    display: grid;
    gap: 0.5em;
    grid-template-columns: min-content min-content max-content min-content min-content;
  }

  #tok-positions-calcs p {
    margin: 0;
    display: none;
    grid-template-columns: subgrid;
    grid-column: span 5;
  }

  #tok-positions-calcs span {
    margin: 0;
    padding: 0;
    justify-self: start;
  }

${tokenStyles}
</style>
"""
)

TYPES_LAYOUT = string.Template(
    """\
<div id="tok-types" style="display: flex; justify-content: space-between;">
  <div style="flex-grow: 1;">
    <ul style="display: grid; grid-template-columns: repeat(5, 1fr); margin-right: 1em;">
      <li>
        <span>Token</span>
        <span>Line</span>
        <span>Offset</span>
        <span>Length</span>
        <span>Type</span>
      </li>
${tokenList}
    </ul>
  </div>
  <div style="display: flex; gap: 1em; flex-direction: column;">
    <ul style="display: grid; grid-template-columns: repeat(2, 1fr); margin-right: 1em;">
      <li>
        <span>Index</span>
        <span>Type</span>
      </li>
${tokenTypes}
    </ul>
  </div>
</div>
<style>
#tok-types {
  --tok-border-color: gray;
  --tok-highlight-color: lightgray;
  --tok-before-color: olive;
  --tok-after-color: blue;
}

#tok-types li {
  display: grid;
  grid-template-columns: subgrid;
  align-items: baseline;
  grid-column: span 5;
  margin: 0;
}

#tok-types span {
  margin: 0;
  padding: 0 0.5em;
  justify-self: center;
}

${tokenStyles}
</style>
"""
)

MODIFIER_LAYOUT = string.Template(
    """\
<div id="tok-modifiers" style="display: flex; justify-content: space-between;">
  <div style="flex-grow: 1;">
    <ul style="display: grid; grid-template-columns: repeat(6, 1fr); margin-right: 1em;">
      <li>
        <span>Token</span>
        <span>Line</span>
        <span>Offset</span>
        <span>Length</span>
        <span>Type</span>
        <span>Modifier</span>
      </li>
${tokenList}
    </ul>
  </div>
  <div style="display: flex; gap: 1em; flex-direction: column;">
    <ul style="display: grid; grid-template-columns: repeat(2, 1fr); margin-right: 1em;">
      <li>
        <span>Index</span>
        <span>Type</span>
      </li>
${tokenModifiers}
    </ul>
    <table>
      <tbody>
${modifierTable}
      </tbody>
    </table>
    <div id="tok-modifier-calcs">
${tokenModifierCalcs}
    </div>
  </div>
</div>
<style>
#tok-modifiers {
  --tok-border-color: gray;
  --tok-highlight-color: lightgray;
  --tok-before-color: olive;
  --tok-after-color: blue;
}

#tok-modifiers li {
  display: grid;
  grid-template-columns: subgrid;
  align-items: baseline;
  grid-column: span 6;
  margin: 0;
}

#tok-modifiers span {
  margin: 0;
  padding: 0 0.5em;
  justify-self: center;
}

#tok-modifier-calcs p {
  display: none;
}

${tokenStyles}
</style>
"""
)


def main(dest: pathlib.Path):
    token_types = ["variable", "number", "operator", "function"]
    tokens = [
        Token(0, 0, "c", "variable", [TokenModifier.definition]),
        Token(0, 2, "=", "operator"),
        Token(
            0,
            2,
            "sqrt",
            "function",
            [TokenModifier.deprecated, TokenModifier.defaultLibrary],
        ),
        Token(0, 4, "(", "operator"),
        Token(1, 2, "a", "variable"),
        Token(0, 1, "^", "operator"),
        Token(0, 1, "2", "number"),
        Token(0, 2, "+", "operator"),
        Token(0, 2, "b", "variable", [TokenModifier.readonly]),
        Token(0, 1, "^", "operator"),
        Token(0, 1, "2", "number"),
        Token(1, 0, ")", "operator"),
    ]

    calcs, styles = render_token_position_calcs_and_styles(tokens)

    positions = dest / "positions.html"
    positions.write_text(
        POSITIONS_LAYOUT.substitute(
            {
                "table": textwrap.indent(render_table(tokens), indent(4)),
                "tokenCalcs": textwrap.indent(calcs, indent(3)),
                "tokenList": textwrap.indent(render_token_list(tokens), indent(3)),
                "tokenStyles": textwrap.indent(styles, indent(1)),
            }
        )
    )

    types = dest / "types.html"
    types.write_text(
        TYPES_LAYOUT.substitute(
            {
                "tokenTypes": textwrap.indent(
                    render_token_types(token_types), indent(3)
                ),
                "tokenList": textwrap.indent(
                    render_token_list(tokens, token_types), indent(3)
                ),
                "tokenStyles": textwrap.indent(
                    render_token_type_styles(tokens, token_types), indent(3)
                ),
            }
        )
    )

    modifier_list, modifier_table = render_token_modifiers(TokenModifier)
    modifier_calcs, modifier_styles = render_token_modifier_calcs_and_styles(
        tokens, TokenModifier
    )

    modifiers = dest / "modifiers.html"
    modifiers.write_text(
        MODIFIER_LAYOUT.substitute(
            {
                "tokenModifiers": textwrap.indent(modifier_list, indent(3)),
                "modifierTable": textwrap.indent(modifier_table, indent(3)),
                "tokenList": textwrap.indent(
                    render_token_list(tokens, token_types, include_modifiers=True),
                    indent(3),
                ),
                "tokenStyles": textwrap.indent(modifier_styles, indent(3)),
                "tokenModifierCalcs": textwrap.indent(modifier_calcs, indent(3)),
            }
        )
    )


cli = argparse.ArgumentParser()
cli.add_argument(
    "-o", "--output", type=pathlib.Path, default="-", help="the directory to write to"
)


def indent(level: int) -> str:
    return level * 2 * " "


def tokens_to_lines(tokens: list[Token]) -> list[list[str | Token]]:
    """Convert a list of tokens into the corresponding text"""
    text: list[list[str | Token]] = []
    current_line: list[str | Token] = []

    for token in tokens:
        if token.line > 0:
            text.append(current_line)
            current_line = []

        prev_token = current_line[-1] if len(current_line) > 0 else ""
        if (padding := token.offset - len(prev_token)) > 0:
            current_line.append(padding * " ")

        current_line.append(token)

    # Commit the final line
    text.append(current_line)

    return text


def render_header_row(width: int) -> str:
    """Render the width of the table, render the character indices."""
    result = ["<tr>"]

    # Padding for the line number
    result.append(f'{indent(1)}<td class="index"></td>')

    # Render the column numbers
    for idx in range(width - 1):
        result.append(f'{indent(1)}<td class="index" data-offset="{idx}">{idx}</td>')

    result.append("</tr>")

    return "\n".join(result)


def render_text_row(line: int, text: list[str | Token], width: int) -> str:
    """Render the given line of text as a row of table cells."""
    result = ["<tr>"]

    # Render the line number
    result.append(f'{indent(1)}<td class="index" data-line="{line}">{line}</td>')

    # Render the text
    for token in text:
        for char in token:
            token_id = f' data-tok="{token.tok_id}"' if isinstance(token, Token) else ""
            result.append(f'{indent(1)}<td class="char"{token_id}>{char.strip()}</td>')

    # Don't forget to pad the line to the max line length.
    remaining_cols = width - (sum(map(len, text)) + 1)
    for _ in range(remaining_cols):
        result.append(f'{indent(1)}<td class="char"></td>')

    result.append("</tr>")

    return "\n".join(result)


def render_table(tokens: list[Token]) -> str:
    """Given a list of tokens, render the corresponding text as a grid of  characters."""
    text = tokens_to_lines(tokens)
    width = max(sum(map(len, line)) for line in text) + 1

    rows = [render_header_row(width)]
    for linum, line in enumerate(text):
        rows.append(render_text_row(linum + 1, line, width))

    return "\n".join(rows)


def render_token_list(
    tokens: list[Token],
    token_types: Optional[List[str]] = None,
    include_modifiers: bool = False,
) -> str:
    """Render the list of tokens.

    Parameters
    ----------
    tokens
       The list of tokens to render

    token_types
       If set, also render a column depicting the token's type

    include_modifiers
       If ``True``, also render a column depicting the token's modifiers
    """
    lines = []

    for token in tokens:
        lines.append(f'<li data-tok="{token.tok_id}">')
        lines.append(f"{indent(1)}<span>{token.text}</span>")
        lines.append(f"{indent(1)}<span data-line>{token.line}</span>")
        lines.append(f"{indent(1)}<span data-offset>{token.offset}</span>")
        lines.append(f"{indent(1)}<span>{len(token)}</span>")

        if token_types is not None:
            tok_type = token_types.index(token.tok_type)
            lines.append(f'{indent(1)}<span data-type="{tok_type}">{tok_type}</span>')

        if include_modifiers:
            value = 0
            if len(token.tok_modifiers) > 0:
                value = reduce(operator.or_, token.tok_modifiers)

            lines.append(f"{indent(1)}<span>{value}</span>")

        lines.append("</li>")

    return "\n".join(lines)


def render_token_types(token_types: List[str]) -> str:
    """Render the list of token types."""
    lines = []

    for idx, tok_type in enumerate(token_types):
        lines.append(f'<li data-type="{idx}">')
        lines.append(f"{indent(1)}<span>{idx}</span>")
        lines.append(f'{indent(1)}<span style="justify-self: end">{tok_type}</span>')
        lines.append("</li>")

    return "\n".join(lines)


def render_token_modifiers(modifiers: Type[enum.IntFlag]) -> Tuple[str, str]:
    """Render the list of token modifiers."""
    list_lines = []

    for idx, modifier in enumerate(modifiers):
        list_lines.append(f'<li data-mod="{idx}">')
        list_lines.append(f"{indent(1)}<span>{idx}</span>")
        list_lines.append(
            f'{indent(1)}<span style="justify-self: end">{modifier.name}</span>'
        )
        list_lines.append("</li>")

    idx_cells: List[str] = []
    value_cells: List[str] = []

    for idx, modifier in enumerate(modifiers):
        idx_cells.insert(0, f'<td style="text-align: center">{idx}</td>')
        value_cells.insert(
            0, f'<td style="text-align: center" data-mod="{idx}">{modifier.value}</td>'
        )

    idx_cells.insert(0, "<td>Index</td>")
    value_cells.insert(0, "<td>2<sup>Index</sup></td>")

    table_lines = [
        "<tr>",
        textwrap.indent("\n".join(idx_cells), indent(1)),
        "</tr>",
        "<tr>",
        textwrap.indent("\n".join(value_cells), indent(1)),
        "</tr>",
    ]

    return "\n".join(list_lines), "\n".join(table_lines)


def render_token_type_styles(tokens: List[Token], token_types: List[str]) -> str:
    """Render the CSS styles for the list of token types."""
    lines = []

    for token in tokens:
        tok_id = token.tok_id
        tok_type = token_types.index(token.tok_type)
        lines.extend(
            [
                f'#tok-types li[data-tok="{tok_id}"]:hover,',
                f'#tok-types:has([data-tok="{tok_id}"]:hover) li[data-type="{tok_type}"] {{',
                f"{indent(1)}border: solid 1px;",
                f"{indent(1)}background: var(--tok-highlight-color);",
                "}",
                "",
            ]
        )
    return "\n".join(lines)


def render_position_calculation(
    name: str, token_id: str, previous: int, delta: int
) -> str:
    """Render the given calculation."""
    current = previous + delta
    lines = [
        f'<p data-tok="{token_id}">',
        f"{indent(1)}<span>{name}</span>",
        f"{indent(1)}<span>=</span>",
        f"{indent(1)}<span>",
        f'{indent(2)}<span style="color: var(--tok-after-color)">{current}</span>',
        f"{indent(2)}-",
        f'{indent(2)}<span style="color: var(--tok-before-color)">{previous}</span>',
        f"{indent(1)}</span>",
        f"{indent(1)}<span>=</span>",
        f"{indent(1)}<span>{current - previous}</span>",
        "</p>",
    ]

    return "\n".join(lines)


def render_token_position_calcs_and_styles(tokens: list[Token]) -> Tuple[str, str]:
    """Render the set of line and offset calculations."""
    calc_lines = []
    style_lines = []

    prev_line = 1
    prev_offset = 0

    for token in tokens:
        tok_id = token.tok_id

        style_lines.extend(
            [
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) li[data-tok="{tok_id}"],',
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) td[data-tok="{tok_id}"] {{',
                f"{indent(1)}border: solid 1px;",
                f"{indent(1)}background: var(--tok-highlight-color);",
                "}",
                "",
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) td[data-line="{prev_line}"] {{',
                f"{indent(1)}background: var(--tok-before-color);",
                f"{indent(1)}color: white;",
                "}",
                "",
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) td[data-line="{prev_line + token.line}"] {{',
                f"{indent(1)}background: var(--tok-after-color);",
                f"{indent(1)}color: white;",
                "}",
                "",
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) p[data-tok="{tok_id}"] {{',
                f"{indent(1)}display: grid;",
                "}",
                "",
            ]
        )

        calc_lines.append(
            render_position_calculation("Line", tok_id, prev_line, token.line)
        )

        if token.line > 0:
            prev_line += token.line
            prev_offset = 0

        style_lines.extend(
            [
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) td[data-offset="{prev_offset}"] {{',
                f"{indent(1)}background: var(--tok-before-color);",
                f"{indent(1)}color: white;",
                "}",
                "",
                f'#tok-positions:has([data-tok="{tok_id}"]:hover) td[data-offset="{prev_offset + token.offset}"] {{',
                f"{indent(1)}background: var(--tok-after-color);",
                f"{indent(1)}color: white;",
                "}",
                "",
            ]
        )

        calc_lines.append(
            render_position_calculation("Offset", tok_id, prev_offset, token.offset)
        )
        prev_offset += token.offset

    return "\n".join(calc_lines), "\n".join(style_lines)


def render_token_modifier_calcs_and_styles(
    tokens: list[Token], modifiers: Type[enum.IntFlag]
) -> Tuple[str, str]:
    """Render the set of modifier calculations."""
    calc_lines = []
    style_lines = []
    mod_index = {mod.value: i for i, mod in enumerate(modifiers)}

    for token in tokens:
        tok_id = token.tok_id

        style_lines.extend(
            [
                f'#tok-modifiers:has([data-tok="{tok_id}"]:hover) li[data-tok="{tok_id}"] {{',
                f"{indent(1)}border: solid 1px;",
                f"{indent(1)}background: var(--tok-highlight-color);",
                "}",
                "",
            ]
        )

        if len(token.tok_modifiers) > 0:
            total = reduce(operator.or_, token.tok_modifiers)
            sum_ = " + ".join(str(m.value) for m in token.tok_modifiers)
            calc_lines.append(f'<p data-tok="{tok_id}">{total} = {sum_}</p>')

            style_lines.extend(
                [
                    f'#tok-modifiers:has([data-tok="{tok_id}"]:hover) #tok-modifier-calcs p[data-tok="{tok_id}"] {{',
                    f"{indent(1)}display: block;",
                    "}",
                    "",
                ]
            )

        for modifier in token.tok_modifiers:
            mod_id = mod_index[modifier.value]
            style_lines.extend(
                [
                    f'#tok-modifiers:has([data-tok="{tok_id}"]:hover) li[data-mod="{mod_id}"],',
                    f'#tok-modifiers:has([data-tok="{tok_id}"]:hover) td[data-mod="{mod_id}"] {{',
                    f"{indent(1)}border: solid 1px;",
                    f"{indent(1)}background: var(--tok-highlight-color);",
                    "}",
                    "",
                ]
            )

    return "\n".join(calc_lines), "\n".join(style_lines)


if __name__ == "__main__":
    args = cli.parse_args()

    main(args.output)
