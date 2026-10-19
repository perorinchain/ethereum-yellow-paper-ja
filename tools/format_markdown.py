#!/usr/bin/env python3
"""Normalize the canonical Markdown for portable preview rendering."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


HEADING = re.compile(r"^(#{1,6}) (.+?) \{#([^}]+)\}$", re.MULTILINE)
TABU = re.compile(r'<div class="tabu\*?">\n(.*?)\n</div>', re.DOTALL)
ROW_START = re.compile(
    r"^(?:\*\*値\*\*|(?:l|r|c|X\\\[j\\\])(?:\s+(?:l|r|c|X\\\[j\\\]))*\s+"
    r"(?:名前|記号)|0x[0-9a-f]{2}|\$[GRJ]_\{|\$\\bigvee|&\s*&\s*⋮)"
)


def normalize_headings(markdown: str) -> str:
    """Use portable HTML anchors instead of Pandoc-only heading attributes."""
    return HEADING.sub(
        lambda match: (
            f'<span id="{match.group(3)}"></span>\n\n'
            f'{match.group(1)} {match.group(2)}'
        ),
        markdown,
    )


def normalize_display_math(markdown: str) -> str:
    """Use GitHub's fenced display-math syntax."""
    parts = markdown.split("$$")
    if len(parts) % 2 == 0:
        raise ValueError("unbalanced display-math delimiters")
    output = parts[0]
    for index, part in enumerate(parts[1:], 1):
        if index % 2:
            # Blank paragraphs terminate math in Pandoc and common Markdown
            # previews, even when the surrounding $$ delimiters are balanced.
            part = re.sub(r"\n(?:[ \t]*\n)+", "\n", part)
        delimiter = "\n\n```math\n" if index % 2 else "\n```\n\n"
        output = output.rstrip() + delimiter + part.lstrip()
    return re.sub(r"\n{3,}", "\n\n", output).rstrip() + "\n"


def normalize_inline_math_spacing(markdown: str) -> str:
    """Use GitHub's collision-safe inline-math syntax."""
    output: list[str] = []
    in_display = False
    for line in markdown.splitlines():
        if line.strip() == "```math":
            in_display = True
            output.append(line)
            continue
        if in_display and line.strip() == "```":
            in_display = False
            output.append(line)
            continue
        if in_display:
            output.append(line)
            continue

        delimiters = [
            index for index, character in enumerate(line)
            if character == "$" and (index == 0 or line[index - 1] != "\\")
        ]
        if len(delimiters) % 2:
            raise ValueError(f"unbalanced inline-math delimiters: {line!r}")
        for opening, closing in reversed(list(zip(delimiters[::2], delimiters[1::2]))):
            if line[opening + 1:opening + 2] != "`" or line[closing - 1:closing] != "`":
                line = line[:closing] + "`" + line[closing:]
                line = line[:opening + 1] + "`" + line[opening + 1:]
        output.append(line)
    if in_display:
        raise ValueError("unbalanced display-math delimiters")
    return "\n".join(output) + "\n"


def split_row(line: str, columns: int) -> list[str]:
    """Split only the structural ampersands of a pseudo-LaTeX table row."""
    line = re.sub(
        r"^(?:(?:l|r|c|X\\\[j\\\])\s+)+(\*\*値\*\*|名前|記号)",
        r"\1",
        line,
    )
    cells = re.split(r"\s*&\s*", line, maxsplit=columns - 1)
    return [cell.strip() for cell in cells]


def table_to_markdown(match: re.Match[str]) -> str:
    """Convert one extracted LaTeX-style table to a Markdown table."""
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    while lines and re.fullmatch(r"[lrcX\\\[\]j* ]+", lines[0]):
        lines.pop(0)
    if not lines:
        raise ValueError("empty tabu table")

    if re.search(r"(?:\*\*値\*\*|名前\s*&|記号\s*&)", lines[0]):
        header_line = lines.pop(0)
        header_line = re.sub(
            r"^(?:(?:l|r|c|X\\\[j\\\])\s+)+(\*\*値\*\*|名前|記号)",
            r"\1",
            header_line,
        )
        header = [cell.strip().strip("*") for cell in re.split(r"\s*&\s*", header_line)]
    else:
        header = ["値", "ニーモニック", "$\\delta$", "$\\alpha$", "説明"]
    columns = len(header)
    if columns < 3:
        raise ValueError(f"table header has too few columns: {header!r}")

    rows: list[list[str]] = []
    for line in lines:
        if ROW_START.match(line):
            row = split_row(line, columns)
            if len(row) > columns:
                raise ValueError(f"table row has too many columns: {line!r}")
            row.extend([""] * (columns - len(row)))
            rows.append(row)
            continue
        if not rows:
            raise ValueError(f"table continuation precedes first row: {line!r}")
        continuation = re.sub(r"^&{2,4}\s*", "", line)
        rows[-1][-1] = (rows[-1][-1] + " " + continuation).strip()

    def safe(cell: str) -> str:
        # A literal pipe would terminate a Markdown-table cell. In these
        # extracted tables it occurs only as a mathematical vertical bar.
        return re.sub(r"\s+", " ", cell).replace("|", r"\vert ")

    rendered = [
        "| " + " | ".join(map(safe, header)) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    rendered.extend("| " + " | ".join(map(safe, row)) + " |" for row in rows)
    return "\n".join(rendered)


def format_markdown(markdown: str) -> str:
    markdown = normalize_headings(markdown)
    markdown = TABU.sub(table_to_markdown, markdown)
    markdown = normalize_display_math(markdown)
    markdown = normalize_inline_math_spacing(markdown)
    markdown = re.sub(r"\^\*(?!\})", r"^{*}", markdown)
    markdown = re.sub(r"\^(\\mathbf\{[^{}]*\})", r"^{\1}", markdown)
    return markdown


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    original = args.source.read_text(encoding="utf-8")
    formatted = format_markdown(original)
    if args.check:
        if formatted != original:
            raise SystemExit(f"Markdown is not normalized: {args.source}")
    else:
        args.source.write_text(formatted, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
