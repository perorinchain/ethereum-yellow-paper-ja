#!/usr/bin/env python3
"""Generate chapter-sized Markdown pages for GitHub's math renderer."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import posixpath
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ethereum_yellow_paper_ja.md"
OUTPUT = ROOT / "split-markdown"
FILENAMES = (
    "chapters/01-introduction.md", "chapters/02-blockchain-paradigm.md",
    "chapters/03-conventions.md", "chapters/04-blocks-state-transactions.md",
    "chapters/05-gas-and-payment.md", "chapters/06-transaction-execution.md",
    "chapters/07-contract-creation.md", "chapters/08-message-call.md",
    "chapters/09-execution-model.md", "chapters/10-proof-of-stake-transition.md",
    "chapters/11-blocktree-to-blockchain.md", "chapters/12-block-finalisation.md",
    "chapters/13-contract-implementation.md", "chapters/14-future-directions.md",
    "chapters/15-conclusion.md", "chapters/16-acknowledgements.md",
    "chapters/17-availability.md", "references.md",
    "appendices/appendix-a-terminology.md", "appendices/appendix-b-rlp.md",
    "appendices/appendix-c-hex-prefix.md", "appendices/appendix-d-trie.md",
    "appendices/appendix-e-precompiled-contracts.md",
    "appendices/appendix-f-signing-transactions.md",
    "appendices/appendix-g-fee-schedule.md",
    "appendices/appendix-h-virtual-machine.md",
    "appendices/appendix-i-genesis-block.md", "appendices/appendix-j-ethash.md",
    "appendices/appendix-k-anomalies.md",
    "appendices/appendix-l-mathematical-symbols.md",
    "translation-notes.md",
)
TOP_HEADING = re.compile(r"^# (.+)$", re.MULTILINE)
TARGET = re.compile(r'<(?:span|div)\s+id="([^"]+)"')
LOCAL_LINK = re.compile(r"\]\(#([^)]+)\)")
MATH_LINK = re.compile(r"\[\$`(.*?)`\$\]\(([^)]+)\)")
FOOTNOTE_REFERENCE = re.compile(r"\[\^(\d+)\](?!:)")
FOOTNOTE_DEFINITION = re.compile(r"^\[\^(\d+)\]:.*$", re.MULTILINE)
DISPLAY_MATH = re.compile(r"^```math\n(.*?)\n```$", re.MULTILINE | re.DOTALL)
INLINE_MATH = re.compile(r"\$`(.*?)`\$")
MAX_MATH_PER_PAGE = 300
FOOTNOTE_MATH_HTML = {
    r"T_{\mathrm{m}}": "<var>T</var><sub>m</sub>",
    r"T_{\mathrm{f}}": "<var>T</var><sub>f</sub>",
    r"T_{\mathrm{p}}": "<var>T</var><sub>p</sub>",
    r"= 2^{11}": "= 2<sup>11</sup>",
}


def section_start(markdown: str, heading_start: int) -> int:
    """Include standalone anchors and containers preceding a heading."""
    start = heading_start
    prefix = markdown[:start]
    while True:
        match = re.search(
            r'(?:^|\n)(<span id="[^"]+"></span>|<div id="[^"]+"[^>]*>)\n\n$',
            prefix,
        )
        if match is None:
            return start
        start = match.start(1)
        prefix = markdown[:start]


def split_source(markdown: str) -> tuple[str, list[tuple[str, str]]]:
    headings = list(TOP_HEADING.finditer(markdown))
    if len(headings) != len(FILENAMES) + 1:
        raise ValueError(
            f"expected title plus {len(FILENAMES)} top-level sections, "
            f"found {len(headings)}"
        )
    starts = [section_start(markdown, match.start()) for match in headings[1:]]
    preamble = markdown[:starts[0]].rstrip() + "\n"
    sections: list[tuple[str, str]] = []
    for index, heading in enumerate(headings[1:]):
        end = starts[index + 1] if index + 1 < len(starts) else len(markdown)
        sections.append((heading.group(1), markdown[starts[index]:end].rstrip() + "\n"))
    return preamble, sections


def rewrite_links(text: str, current: str, owners: dict[str, str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        identifier = match.group(1)
        owner = owners.get(identifier)
        if owner is None or owner == current:
            return match.group(0)
        return f"]({relative_link(current, owner)}#{identifier})"
    return LOCAL_LINK.sub(replacement, text)


def relative_link(current: str, target: str) -> str:
    """Return a POSIX relative link from one generated page to a target."""
    parent = Path(current).parent.as_posix()
    return posixpath.relpath(target, start=parent)


def rewrite_math_links(text: str) -> str:
    """Place links beside math because GitHub cannot render nested math links."""
    return MATH_LINK.sub(r"$`\1`$[↗](\2)", text)


def navigation(index: int) -> str:
    current = FILENAMES[index]
    links = [f"[分割版目次]({relative_link(current, 'README.md')})"]
    if index:
        links.append(f"[前へ]({relative_link(current, FILENAMES[index - 1])})")
    if index + 1 < len(FILENAMES):
        links.append(f"[次へ]({relative_link(current, FILENAMES[index + 1])})")
    canonical = relative_link(current, "../ethereum_yellow_paper_ja.md")
    links.append(f"[単一ページ版]({canonical})")
    return " | ".join(links)


def github_footnote(definition: str) -> str:
    """Replace math unsupported in GitHub footnotes with semantic HTML."""
    def replacement(match: re.Match[str]) -> str:
        formula = match.group(1)
        if formula not in FOOTNOTE_MATH_HTML:
            raise ValueError(f"unsupported formula in GitHub footnote: {formula}")
        return FOOTNOTE_MATH_HTML[formula]
    return INLINE_MATH.sub(replacement, definition)


def render() -> dict[Path, str]:
    markdown = SOURCE.read_text(encoding="utf-8")
    definition_lines = {
        match.group(1): match.group(0)
        for match in FOOTNOTE_DEFINITION.finditer(markdown)
    }
    preamble, sections = split_source(markdown)
    owners: dict[str, str] = {}
    for (_, body), filename in zip(sections, FILENAMES):
        for identifier in TARGET.findall(body):
            if identifier in owners:
                raise ValueError(f"duplicate target in source: {identifier}")
            owners[identifier] = filename

    generated: dict[Path, str] = {}
    entries = [
        f"- [{title}]({filename})"
        for (title, _), filename in zip(sections, FILENAMES)
    ]
    links = (
        "### 本文\n\n" + "\n".join(entries[:17])
        + "\n\n### 参考文献\n\n" + entries[17]
        + "\n\n### 付録\n\n" + "\n".join(entries[18:30])
        + "\n\n### 翻訳時の追加事項\n\n" + entries[30]
    )
    preamble = rewrite_math_links(rewrite_links(preamble, "README.md", owners))
    generated[OUTPUT / "README.md"] = (
        preamble.rstrip()
        + "\n\n## Markdown版の読み方\n\n"
        + "このディレクトリは、GitHubの数式レンダラーが単一ページ内の多数の"
          "数式を途中から表示できない場合に備えた、章・付録単位の分割版です。"
          "内容と版は[単一ページ版](../ethereum_yellow_paper_ja.md)と同一であり、"
          "別の翻訳ではありません。VS Codeなどで全文を通して読む場合は単一ページ版、"
          "GitHub上で数式を読む場合は以下の分割版を利用してください。\n\n"
        + "単一ページ版をMarkdownの正本とし、分割版はそこから自動生成します。"
          "修正は単一ページ版へ行い、分割版を直接編集しないでください。\n\n"
        + links + "\n"
    )

    for index, ((_, body), filename) in enumerate(zip(sections, FILENAMES)):
        body = FOOTNOTE_DEFINITION.sub("", body).rstrip()
        references = list(dict.fromkeys(FOOTNOTE_REFERENCE.findall(body)))
        missing = [number for number in references if number not in definition_lines]
        if missing:
            raise ValueError(f"undefined footnotes in {filename}: {missing}")
        body = rewrite_math_links(rewrite_links(body, filename, owners))
        notes = "\n\n".join(
            rewrite_links(github_footnote(definition_lines[number]), filename, owners)
            for number in references
        )
        content = navigation(index) + "\n\n" + body
        if notes:
            content += "\n\n" + notes
        generated[OUTPUT / filename] = content.rstrip() + "\n"

    for path, content in generated.items():
        count = len(DISPLAY_MATH.findall(content)) + len(INLINE_MATH.findall(content))
        if count > MAX_MATH_PER_PAGE:
            raise ValueError(f"too many formulas in {path.name}: {count}")
        if len(re.findall(r"<div\b", content)) != content.count("</div>"):
            raise ValueError(f"unbalanced div tags in {path.name}")
        if MATH_LINK.search(content):
            raise ValueError(f"math remains nested inside a link in {path.name}")
    footnote_math = [
        formula
        for definition in definition_lines.values()
        for formula in INLINE_MATH.findall(definition)
    ]
    source_math = Counter(DISPLAY_MATH.findall(markdown) + INLINE_MATH.findall(markdown))
    split_math = Counter(
        formula
        for path, content in generated.items()
        if path.name != "README.md"
        for formula in DISPLAY_MATH.findall(content) + INLINE_MATH.findall(content)
    )
    split_math.update(footnote_math)
    if split_math != source_math:
        raise ValueError("split Markdown does not preserve the canonical formulas")
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render()
    if args.check:
        expected = set(generated)
        actual: set[Path] = set(OUTPUT.rglob("*.md")) if OUTPUT.is_dir() else set()
        problems = [str(path) for path in sorted(expected ^ actual)]
        problems.extend(
            str(path) for path, content in generated.items()
            if path.is_file() and path.read_text(encoding="utf-8") != content
        )
        if problems:
            raise SystemExit("GitHub split Markdown is not current:\n" + "\n".join(problems))
        return 0
    OUTPUT.mkdir(exist_ok=True)
    for path, content in generated.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
