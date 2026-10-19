#!/usr/bin/env python3
"""Audit common invariants of a locally generated Japanese HTML edition."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import TypeAlias, cast
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]

JSONValue: TypeAlias = (
    None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]
)
PandocNode: TypeAlias = dict[str, JSONValue]


class Arguments(argparse.Namespace):
    html: Path
    source: Path | None
    reader: str
    lua_filter: list[Path]
    strict_math: bool
    skip_source_math: bool


class Document(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.references: list[tuple[str, str, int]] = []
        self.annotations: list[str] = []
        self._annotation: list[str] | None = None
        self.language = ""
        self.charset = ""
        self.title = ""
        self._in_title = False
        self.math_count = 0
        self.math_errors = 0
        self.fallback_math = 0
        self.scripts = 0
        self.remote_assets: list[str] = []
        self.images_without_alt: list[int] = []
        self.feed(source)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if identifier := values.get("id"):
            self.ids[identifier] += 1
        if tag == "html":
            self.language = values.get("lang", "") or ""
        if tag == "meta" and values.get("charset"):
            self.charset = values["charset"] or ""
        if tag == "title":
            self._in_title = True
        if tag == "math":
            self.math_count += 1
        if tag == "merror":
            self.math_errors += 1
        if tag == "span" and "math" in (values.get("class") or "").split():
            self.fallback_math += 1
        if tag == "script":
            self.scripts += 1
        if tag == "img" and not values.get("alt"):
            self.images_without_alt.append(self.getpos()[0])
        for attribute in ("href", "src", "xlink:href"):
            raw = values.get(attribute)
            if raw:
                self.references.append((attribute, raw, self.getpos()[0]))
        if tag in {"script", "link", "img"}:
            asset = values.get("src") or values.get("href") or ""
            if asset.startswith(("http://", "https://", "//")):
                self.remote_assets.append(asset)
        if tag == "annotation" and values.get("encoding") == "application/x-tex":
            self._annotation = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "annotation" and self._annotation is not None:
            self.annotations.append("".join(self._annotation))
            self._annotation = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._annotation is not None:
            self._annotation.append(data)


def nodes(value: JSONValue) -> Iterator[PandocNode]:
    if isinstance(value, dict):
        mapping = cast(PandocNode, value)
        if "t" in mapping:
            yield mapping
        for child in mapping.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in cast(list[JSONValue], value):
            yield from nodes(child)


def markdown_math(source: Path, reader: str, lua_filters: list[Path]) -> list[str]:
    command = ["pandoc", str(source), "--from=" + reader, "--to=json", "--fail-if-warnings"]
    command.extend("--lua-filter=" + str(path) for path in lua_filters)
    result = subprocess.run(
        command,
        cwd=source.parent, check=True, capture_output=True, text=True,
    )
    document = cast(JSONValue, json.loads(result.stdout))
    formulas: list[str] = []
    for node in nodes(document):
        if node.get("t") != "Math":
            continue
        raw_content = node.get("c")
        if not isinstance(raw_content, list):
            raise ValueError("invalid Pandoc Math node")
        content = cast(list[JSONValue], raw_content)
        if len(content) != 2:
            raise ValueError("invalid Pandoc Math node")
        formula = content[1]
        if not isinstance(formula, str):
            raise ValueError("invalid Pandoc Math node")
        formulas.append(formula)
    return formulas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--reader", default="gfm+tex_math_dollars")
    parser.add_argument("--lua-filter", action="append", default=[], type=Path)
    parser.add_argument("--strict-math", action="store_true")
    parser.add_argument(
        "--skip-source-math",
        action="store_true",
        help="skip formula multiset comparison for document-specific AST pipelines",
    )
    args = parser.parse_args(namespace=Arguments())
    output = args.html.resolve()
    source_path = args.source.resolve() if args.source else None
    if not output.is_file():
        parser.error(f"HTML file does not exist: {output}")
    if not output.is_relative_to(ROOT):
        parser.error("HTML file must be inside the repository")

    html = output.read_text(encoding="utf-8")
    document = Document(html)
    problems: list[str] = []
    if document.language != "ja":
        problems.append(f"HTML language is {document.language!r}, not 'ja'")
    if document.charset.lower() != "utf-8":
        problems.append(f"HTML charset is {document.charset!r}, not UTF-8")
    if not document.title.strip():
        problems.append("HTML title is empty")
    duplicates = [name for name, count in document.ids.items() if count > 1]
    if duplicates:
        problems.append(f"duplicate HTML IDs: {duplicates[:20]}")
    if document.scripts:
        problems.append(f"HTML contains {document.scripts} script element(s)")
    if document.remote_assets:
        problems.append(f"HTML contains remote rendering assets: {document.remote_assets[:10]}")
    if document.images_without_alt:
        problems.append(f"images without alt text on lines {document.images_without_alt}")
    if document.math_errors:
        problems.append(f"MathML contains {document.math_errors} merror element(s)")
    if document.math_count != len(document.annotations):
        problems.append(
            f"MathML/TeX annotation mismatch: {document.math_count}/{len(document.annotations)}"
        )
    for index, math in enumerate(re.findall(r"<math\b.*?</math>", html, re.S), 1):
        try:
            ET.fromstring(math)
        except ET.ParseError as error:
            problems.append(f"MathML expression {index} is not well-formed: {error}")
    visible_html = html
    for tag in ("annotation", "style", "script", "pre", "code"):
        visible_html = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>", "", visible_html, flags=re.S | re.I
        )
    leftover = re.findall(
        r"\\(?:begin|end)\{[^}]+\}|\\(?:ref|eqref|cite)\{[^}]+\}|\\\[|\\\]",
        visible_html,
    )
    if leftover:
        problems.append(f"visible TeX syntax: {len(leftover)} occurrence(s)")
    if args.strict_math and document.fallback_math:
        problems.append(f"unrendered TeX math fallbacks: {document.fallback_math}")

    linked_documents: dict[Path, set[str]] = {}
    for attribute, raw, line in document.references:
        target = urlsplit(raw)
        if target.scheme in {"http", "https", "mailto", "data"}:
            continue
        if target.scheme or target.netloc or raw.startswith("//"):
            problems.append(f"line {line}: unsupported {attribute} target {raw}")
            continue
        local = (output.parent / unquote(target.path)).resolve() if target.path else output
        if not local.is_relative_to(ROOT):
            problems.append(f"line {line}: target outside repository: {raw}")
        elif not local.is_file():
            problems.append(f"line {line}: missing {attribute} target {raw}")
        elif target.fragment:
            if local == output:
                identifiers = set(document.ids)
            else:
                if local not in linked_documents:
                    linked = Document(local.read_text(encoding="utf-8"))
                    linked_documents[local] = set(linked.ids)
                identifiers = linked_documents[local]
            if unquote(target.fragment) not in identifiers:
                problems.append(f"line {line}: broken fragment {raw}")

    if source_path:
        if not source_path.is_file():
            parser.error(f"Markdown source does not exist: {source_path}")
        markdown = source_path.read_text(encoding="utf-8")
        if not args.skip_source_math:
            formulas = markdown_math(source_path, args.reader, args.lua_filter)
            if Counter(formulas) != Counter(document.annotations):
                missing = list((Counter(formulas) - Counter(document.annotations)).elements())
                extra = list((Counter(document.annotations) - Counter(formulas)).elements())
                problems.append(
                    f"TeX annotations differ: missing={missing[:5]!r}, extra={extra[:5]!r}"
                )
        anchors = set(re.findall(r"\{#([^\s}]+)", markdown))
        anchors.update(re.findall(r'\{id="([^"}]+)"\}', markdown))
        absent = anchors.difference(document.ids)
        if absent:
            problems.append(f"Markdown anchors missing from HTML: {sorted(absent)[:20]}")
        if re.search(r"(?m)[\t ]+$", markdown):
            problems.append("canonical Markdown contains trailing whitespace")

    print(
        f"MathML: {document.math_count}; TeX annotations: {len(document.annotations)}; "
        f"IDs: {len(document.ids)}; links/assets: {len(document.references)}"
    )
    for problem in problems:
        print("ERROR:", problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

