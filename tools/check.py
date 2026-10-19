#!/usr/bin/env python3
"""公開パッケージのHTML、Markdown、LaTeXおよび必須ファイルを検査する。"""

from pathlib import Path
from html import unescape
import json
import re
import subprocess
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "ethereum_yellow_paper_ja.md"
HTML = ROOT / "ethereum_yellow_paper_ja.html"
TEX = ROOT / "ethereum_yellow_paper_ja.tex"
TRANSLATOR_HEADING = "訳注（日本語訳で追加）"


def check_notes(markdown: str, html: str, latex: str) -> None:
    """Keep original footnote numbers and translator additions independent."""
    original = [str(number) for number in range(1, 13)]
    if re.findall(r"^\[\^([^\]]+)\]:", markdown, re.MULTILINE) != original:
        raise SystemExit("only the original footnotes 1..12 may use native Markdown notes")
    if re.findall(r"\[\^([^\]]+)\](?!:)", markdown) != original:
        raise SystemExit("original footnote references must retain their order and numbers 1..12")
    rendered = re.findall(
        r'<a\b[^>]*href="#fn(\d+)"[^>]*>\s*<sup>(\d+)</sup>\s*</a>', html,
    )
    if rendered != [(number, number) for number in original]:
        raise SystemExit("rendered original footnotes must keep the original numbers 1..12")
    if re.findall(r'<li id="fn(\d+)"', html) != original:
        raise SystemExit("the original footnote list must contain exactly notes 1..12")
    if len(re.findall(r"\\footnote\{", latex)) != 12:
        raise SystemExit("translator notes must not consume the LaTeX footnote counter")
    translators = [str(number) for number in range(1, 17)]
    references = re.findall(r"\[訳注(\d+)\]\(#tn-(\d+)\)", markdown)
    if references != [(number, number) for number in translators]:
        raise SystemExit("translator notes must use their independent labels 訳注1..16")
    rendered_translators = re.findall(
        r'<a\b[^>]*href="#tn-(\d+)"[^>]*>([^<]+)</a>', html,
    )
    if rendered_translators != [(number, "訳注" + number) for number in translators]:
        raise SystemExit("rendered translator notes must remain distinct from numeric footnotes")
    if re.findall(r"\*\*訳注(\d+)（", markdown) != translators:
        raise SystemExit("translator-note entries must be visibly numbered 訳注1..16")
    if "日本語訳で追加した案内" not in markdown or markdown.count("# " + TRANSLATOR_HEADING) != 1:
        raise SystemExit("translation additions must be explicitly identified")
    for number in translators:
        for identifier in ("tn-" + number, "tnref-" + number):
            for source in (markdown, html):
                if source.count(f'id="{identifier}"') != 1:
                    raise SystemExit(f"missing or duplicated translator-note target: {identifier}")
        if markdown.count(f"[参照箇所へ戻る](#tnref-{number})") != 1:
            raise SystemExit(f"missing translator-note return link: {number}")
    if html.index('<aside id="footnotes"') > html.index('<div id="translator-notes"'):
        raise SystemExit("the original footnotes must precede the translation additions")
    if '<h2 id="original-footnotes-title">原文の脚注</h2>' not in html:
        raise SystemExit("the original footnotes must be visibly identified")


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "tools/render_github.py"), "--check"],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "tools/format_markdown.py"),
         "--check", str(MD)],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "tools/check_html.py"), str(HTML),
         "--source", str(MD), "--reader", "markdown+tex_math_dollars",
         "--lua-filter", str(ROOT / "tools/publication.lua"),
         "--strict-math"],
        check=True,
    )
    markdown = MD.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    latex = TEX.read_text(encoding="utf-8")
    references = json.loads((ROOT / "tools/reference_map.json").read_text(encoding="utf-8"))
    headings = re.findall(r"^(#{1,3}) (.+)$", markdown, re.MULTILINE)
    source_headings = [(hashes, title) for hashes, title in headings[1:] if title != TRANSLATOR_HEADING]
    numbered_headings = [(hashes, title) for hashes, title in source_headings if title != "参考文献"]
    if len(numbered_headings) != len(references["sections"]):
        raise SystemExit("section/subsection count differs from the pinned upstream structure")
    for (hashes, title), section in zip(numbered_headings, references["sections"]):
        prefix = "付録" if section["level"] == 1 and section["number"][0].isalpha() else ""
        if len(hashes) != section["level"] or not title.startswith(prefix + section["number"] + ". "):
            raise SystemExit(f"incorrect upstream section number: {title}")
    source_titles = [title for _, title in source_headings]
    if source_titles.index("参考文献") != source_titles.index("17. 入手先") + 1:
        raise SystemExit("the original bibliography belongs immediately after section 17")
    if source_titles.index("付録A. 用語集") != source_titles.index("参考文献") + 1:
        raise SystemExit("Appendix A must immediately follow the original bibliography")
    toc = re.search(r'<details id="TOC"[^>]*>(.*?)</details>', html, re.DOTALL)
    if toc is None:
        raise SystemExit("missing table of contents")
    toc_titles = [
        unescape(re.sub(r"<[^>]+>", "", title))
        for title in re.findall(r'<a\b[^>]*>(.*?)</a>', toc[1], re.DOTALL)
    ]
    if toc_titles != source_titles:
        raise SystemExit("the contents must match the original headings, excluding translation additions")
    numbers = [int(n) for n in re.findall(r"\\text\{\((\d+)\)\}", markdown)]
    if numbers != list(range(1, 361)):
        raise SystemExit("equation numbers must occur exactly once, in upstream order 1..360")
    visible_numbers = [int(n) for n in re.findall(r"<mtext\b[^>]*>\((\d+)\)</mtext>", html)]
    if visible_numbers != numbers:
        raise SystemExit("rendered MathML must visibly retain equation numbers 1..360")
    visible_latex = re.sub(r"(?m)(?<!\\)%.*$", "", latex)
    latex_numbers = [int(n) for n in re.findall(r"\\text\{\((\d+)\)\}", visible_latex)]
    if latex_numbers != numbers:
        raise SystemExit("LaTeX must visibly retain equation numbers 1..360 outside comments")
    for group in references["equations"]:
        identifiers = [f"eq-{number}" for number in group["numbers"]] + group["labels"]
        for identifier in identifiers:
            if markdown.count(f'id="{identifier}"') != 1:
                raise SystemExit(f"missing or duplicated equation target: {identifier}")
    if "reference-targets" in markdown or re.search(r'\[eq:[^\]]+\]', markdown):
        raise SystemExit("Markdown contains dummy targets or unresolved equation references")
    if re.search(r'<a\s+href="#', markdown):
        raise SystemExit("use portable Markdown links for same-document references")
    for label, number in references["equation_references"].items():
        for caption in re.findall(r'\[([^\]]+)\]\(#' + re.escape(label) + r'\)', markdown):
            if caption != str(number):
                raise SystemExit(f"incorrect equation reference: {label} -> {caption}")
    citations = re.findall(r"\[(\([^\]]+\))\]\(#(ref-[^)]+)\)", markdown)
    if len(citations) != 35 or dict(citations) != references["citations"]:
        raise SystemExit("expected all 35 original citations, linked to the correct 32 bibliography entries")
    if len(re.findall(r'id="ref-[^"]+"', markdown)) != 32:
        raise SystemExit("bibliography must retain all 32 original entries")
    check_notes(markdown, html, latex)
    displays = re.findall(r"^```math\n(.*?)\n```$", markdown, re.MULTILINE | re.DOTALL)
    if len(displays) != 198 or any(re.search(r"\n\s*\n", formula) for formula in displays):
        raise SystemExit("expected 196 numbered display groups and two unnumbered LOG formulas without blank lines")
    if html.count("<dt>") != 61 or html.count("<dd>") != 61:
        raise SystemExit("account/transaction/header fields and glossary must retain 61 definition entries")
    if "\\tableofcontents" not in latex or latex.index("\\tableofcontents") < latex.index("\\textbf{概要。}"):
        raise SystemExit("LaTeX contents must follow the abstract")
    if re.search(r"\\section\{Ethereum", latex):
        raise SystemExit("LaTeX contains a duplicate publication title")
    latex_targets = set(re.findall(r"\\hypertarget\{([^}]+)\}", latex))
    latex_links = set(re.findall(r"\\hyperlink\{([^}]+)\}", latex))
    if latex_links - latex_targets:
        raise SystemExit(f"undefined LaTeX links: {sorted(latex_links - latex_targets)}")
    expected = ["はじめに", "ブロックチェーン・パラダイム",
                "ブロック、状態、トランザクション", "実行モデル",
                "仮想マシン仕様", "参考文献"]
    missing = [heading for heading in expected if heading not in markdown]
    if missing:
        raise SystemExit(f"missing expected headings: {missing}")
    if re.search(r"\\(?:Hy@raisedlink|hypertarget|hyperlink|linkdest)", markdown):
        raise SystemExit("Markdown contains unsupported hyperlink commands inside TeX")
    if re.search(r"^#{1,6} .*\{#[^}]+\}$", markdown, re.MULTILINE):
        raise SystemExit("Markdown contains a Pandoc-only heading attribute")
    if '<div class="tabu' in markdown or "&&&&" in markdown:
        raise SystemExit("Markdown contains an unconverted pseudo-LaTeX table")
    if re.search(
        r"(?:[A-Za-z]|\\[A-Za-z]+)([_^])\{[^{}\n]*(?:\{[^{}\n]*\}[^{}\n]*)*\}\1\{",
        markdown,
    ):
        raise SystemExit("Markdown contains a direct repeated TeX subscript or superscript")
    if not re.search(r"^\| 値 \| ニーモニック \|", markdown, re.MULTILINE):
        raise SystemExit("Markdown is missing the portable EVM instruction tables")
    if "<script" in html.lower():
        raise SystemExit("generated HTML contains script")
    if '<details id="TOC" role="doc-toc" open>' not in html or '<summary>目次</summary>' not in html:
        raise SystemExit("generated HTML is missing the collapsible table of contents")
    if '<nav id="TOC"' in html:
        raise SystemExit("generated HTML contains the non-collapsible Pandoc table of contents")
    if re.search(r"^[ \t]*[^{}\n]+\{[ \t]*\}[ \t]*$", html, re.MULTILINE):
        raise SystemExit("generated HTML contains an empty CSS ruleset")
    if html.count("<table") < 19:
        raise SystemExit("generated HTML is missing expected tables")
    mathematical = sorted({
        ch for ch in html
        if unicodedata.name(ch, "").startswith("MATHEMATICAL ")
    })
    if mathematical:
        raise SystemExit(
            "HTML contains mathematical Unicode instead of MathML mathvariant: "
            + "".join(mathematical)
        )
    if "\\documentclass" not in latex or "ltjsarticle" not in latex:
        raise SystemExit("generated LaTeX is not a standalone ltjsarticle document")
    required = ["README.md", "LICENSE.md", "NOTICE.md", "CITATION.cff",
                "CONTRIBUTING.md", "tools/publication.lua", "tools/reference_map.json",
                "ethereum_yellow_paper_ja.md", "ethereum_yellow_paper_ja.html",
                "ethereum_yellow_paper_ja.tex", "build.sh"]
    absent = [name for name in required if not (ROOT / name).is_file()]
    if absent:
        raise SystemExit(f"missing publication files: {absent}")
    print("OK: portable publication package checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
