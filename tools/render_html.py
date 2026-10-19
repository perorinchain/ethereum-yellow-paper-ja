#!/usr/bin/env python3
"""Render a Japanese Markdown edition as standalone MathML HTML."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
CHECKER = Path(__file__).with_name("check_html.py")


def math_variant(character: str) -> str | None:
    """Return the MathML variant encoded by a mathematical Unicode glyph."""
    name = unicodedata.name(character, "")
    if not name.startswith("MATHEMATICAL "):
        return None
    for marker, variant in (
        ("SANS-SERIF BOLD ITALIC", "sans-serif-bold-italic"),
        ("SANS-SERIF BOLD", "sans-serif-bold"),
        ("SANS-SERIF ITALIC", "sans-serif-italic"),
        ("SANS-SERIF", "sans-serif"),
        ("BOLD FRAKTUR", "bold-fraktur"),
        ("BOLD SCRIPT", "bold-script"),
        ("BOLD ITALIC", "bold-italic"),
        ("DOUBLE-STRUCK", "double-struck"),
        ("MONOSPACE", "monospace"),
        ("FRAKTUR", "fraktur"),
        ("SCRIPT", "script"),
        ("BOLD", "bold"),
        ("ITALIC", "italic"),
    ):
        if marker in name:
            return variant
    return None


def normalise_mathml_variants(output: Path) -> None:
    """Normalise generated HTML without changing its document semantics."""
    html = output.read_text(encoding="utf-8")
    pattern = re.compile(r"<(mi|mn|mtext)([^>]*)>([^<]+)</\1>")

    def replace(match: re.Match[str]) -> str:
        tag, attributes, content = match.groups()
        variants = {math_variant(ch) for ch in content if not ch.isspace()}
        if None in variants or len(variants) != 1:
            return match.group(0)
        variant = variants.pop()
        base = "".join(unicodedata.normalize("NFKD", ch) for ch in content)
        if "mathvariant=" not in attributes:
            attributes += f' mathvariant="{variant}"'
        return f"<{tag}{attributes}>{base}</{tag}>"

    html = pattern.sub(replace, html)

    def encode_math(match: re.Match[str]) -> str:
        return "".join(
            ch if ord(ch) < 128 else f"&#x{ord(ch):X};"
            for ch in match.group(0)
        )

    html = re.sub(r"<math\b.*?</math>", encode_math, html, flags=re.DOTALL)
    html, toc_count = re.subn(
        r'<nav id="TOC" role="doc-toc">\n(.*?)\n</nav>',
        r'<details id="TOC" role="doc-toc" open>\n'
        r'<summary>目次</summary>\n\1\n</details>',
        html,
        count=1,
        flags=re.DOTALL,
    )
    if '<nav id="TOC"' in html or ("--toc" in sys.argv and toc_count != 1):
        raise RuntimeError("failed to convert the generated table of contents")
    # Pandoc's native Notes remain the original footnotes, numbered 1..12.
    # The independent translator-note links never enter that counter.
    html, footnote_count = re.subn(
        r'(<aside id="footnotes"[^>]*>)\n',
        r'\1\n<h2 id="original-footnotes-title">原文の脚注</h2>\n',
        html,
        count=1,
    )
    if footnote_count != 1:
        raise RuntimeError("expected the original footnotes as one native note list")
    original_notes = re.search(r'<aside id="footnotes"[^>]*>.*?</aside>', html, re.DOTALL)
    if original_notes is None or '<div id="translator-notes"' not in html:
        raise RuntimeError("the original and translator note areas must be separate")
    note_markup = original_notes.group(0)
    html = html[:original_notes.start()] + html[original_notes.end():]
    position = html.index('<div id="translator-notes"')
    html = html[:position] + note_markup + "\n" + html[position:]
    # Pandoc emits an empty citation rule even when no declarations apply.
    # Empty rules are harmless, but VS Code's CSS validator reports them.
    html = re.sub(r"^[ \t]*[^{}\n]+\{[ \t]*\}[ \t]*\n", "", html, flags=re.MULTILINE)
    output.write_text(html.replace("\N{NO-BREAK SPACE}", "&nbsp;"), encoding="utf-8")


class Arguments(argparse.Namespace):
    source: Path
    output: Path
    title: str
    reader: str
    lua_filter: list[Path]
    include_in_header: list[Path]
    css: list[Path]
    data_dir: Path | None
    bibliography: list[Path]
    resource_path: Path | None
    wrap: str | None
    toc: bool
    toc_depth: int | None
    number_sections: bool
    embed_resources: bool
    citeproc: bool
    no_highlight: bool
    check: bool
    strict_math: bool


def repository_path(value: str) -> Path:
    path = Path(value)
    return (Path.cwd() / path).resolve() if not path.is_absolute() else path.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=repository_path)
    parser.add_argument("output", type=repository_path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--from", dest="reader", default="gfm+tex_math_dollars")
    parser.add_argument("--lua-filter", action="append", default=[], type=repository_path)
    parser.add_argument("--include-in-header", action="append", default=[], type=repository_path)
    parser.add_argument("--css", action="append", default=[], type=repository_path)
    parser.add_argument("--data-dir", type=repository_path)
    parser.add_argument("--bibliography", action="append", default=[], type=repository_path)
    parser.add_argument("--resource-path", type=repository_path)
    parser.add_argument("--wrap", choices=("auto", "none", "preserve"))
    parser.add_argument("--toc", action="store_true")
    parser.add_argument("--toc-depth", type=int)
    parser.add_argument("--number-sections", action="store_true")
    parser.add_argument("--embed-resources", action="store_true")
    parser.add_argument("--citeproc", action="store_true")
    parser.add_argument("--no-highlight", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict-math", action="store_true")
    args = parser.parse_args(namespace=Arguments())

    if not args.source.is_file():
        parser.error(f"Markdown source does not exist: {args.source}")
    if not args.source.is_relative_to(ROOT) or not args.output.is_relative_to(ROOT):
        parser.error("source and output must be inside the repository")

    command: list[str] = [
        "pandoc", str(args.source),
        "--from=" + args.reader,
        "--to=html5", "--standalone", "--mathml", "--fail-if-warnings",
        "--variable=lang:ja", "--metadata=pagetitle:" + args.title,
        "--output=" + str(args.output),
    ]
    for path in args.lua_filter:
        command.append("--lua-filter=" + str(path))
    for path in args.include_in_header:
        command.append("--include-in-header=" + str(path))
    for path in args.css:
        command.append("--css=" + str(path))
    if args.data_dir:
        command.append("--data-dir=" + str(args.data_dir))
    for path in args.bibliography:
        command.append("--bibliography=" + str(path))
    if args.resource_path:
        command.append("--resource-path=" + str(args.resource_path))
    if args.wrap:
        command.append("--wrap=" + args.wrap)
    if args.toc:
        command.append("--toc")
    if args.toc_depth is not None:
        command.append("--toc-depth=" + str(args.toc_depth))
    if args.number_sections:
        command.append("--number-sections")
    if args.embed_resources:
        command.append("--embed-resources")
    if args.citeproc:
        command.append("--citeproc")
    if args.no_highlight:
        command.append("--no-highlight")

    subprocess.run(command, cwd=args.source.parent, check=True)
    normalise_mathml_variants(args.output)
    if args.check:
        audit: list[str] = [
            sys.executable, str(CHECKER), str(args.output),
            "--source", str(args.source), "--reader", args.reader,
        ]
        if args.strict_math:
            audit.append("--strict-math")
        subprocess.run(audit, cwd=args.source.parent, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

