#!/usr/bin/env python3
"""Exercise the actual checker against the regressions fixed in this review."""

from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parents[1]
checker = runpy.run_path(str(PACKAGE / "tools/check.py"))
main = checker["main"]
scope = main.__globals__
markdown = (PACKAGE / "ethereum_yellow_paper_ja.md").read_text()
html = (PACKAGE / "ethereum_yellow_paper_ja.html").read_text()
print("Testing expected checker failures against temporary files.", flush=True)

with tempfile.TemporaryDirectory(prefix=".review-regressions-", dir=PACKAGE) as directory:
    test_root = Path(directory)
    md = test_root / "source.md"
    output = test_root / "output.html"
    scope["MD"] = md
    scope["HTML"] = output

    def rejects(
        name: str,
        source: str = markdown,
        rendered: str = html,
        expected: str = "",
    ) -> None:
        md.write_text(source)
        output.write_text(rendered)
        try:
            main()
        except SystemExit as error:
            assert expected in str(error), (name, error)
        except subprocess.CalledProcessError:
            assert name == "changed TeX content", name
        else:
            raise AssertionError(f"checker accepted {name}")
        print("PASS:", name, flush=True)

    rejects("changed TeX content", source=markdown.replace(r"\Upsilon", r"\Gamma", 1))
    missing_label, count = re.subn(r"<mtext\b[^>]*>\(315\)</mtext>", "<mtext></mtext>", html)
    assert count == 1
    rejects("invisible equation number", rendered=missing_label, expected="rendered MathML")
    wrong_reference = markdown.replace("[95](#eq:new-address)", "[999](#eq:new-address)", 1)
    assert wrong_reference != markdown
    rejects("wrong equation reference", source=wrong_reference, expected="incorrect equation reference")
    rejects("dummy reference targets", source=markdown + "\n<!-- reference-targets -->\n", expected="dummy targets")

    wrong_footnote = html.replace("<sup>7</sup>", "<sup>8</sup>", 1)
    assert wrong_footnote != html
    rejects("renumbered original footnote", rendered=wrong_footnote, expected="rendered original footnotes")
    extra_native_note = markdown.replace("[^1]。", "[^tn][^1]。", 1) + "\n[^tn]: 翻訳時に追加した注。\n"
    assert extra_native_note != markdown
    rejects("translator note in the original counter", source=extra_native_note, expected="only the original footnotes")
    ambiguous_note = html.replace(
        'aria-label="日本語訳で追加した訳注1">訳注1</a>',
        'aria-label="日本語訳で追加した訳注1">1</a>',
        1,
    )
    assert ambiguous_note != html
    rejects("ambiguous translator note label", rendered=ambiguous_note, expected="distinct from numeric footnotes")
    extra_toc_item = html.replace(
        "</details>",
        '<a href="#translator-notes-heading">訳注（日本語訳で追加）</a>\n</details>',
        1,
    )
    assert extra_toc_item != html
    rejects("translator additions in the original contents", rendered=extra_toc_item, expected="contents must match")
    bibliography_start = markdown.index("# 参考文献\n")
    appendix_start = markdown.index('<span id="ch:Terminology"></span>')
    bibliography = markdown[bibliography_start:appendix_start]
    misplaced_bibliography = markdown[:bibliography_start] + markdown[appendix_start:]
    notes_start = misplaced_bibliography.index('<div id="translator-notes"')
    misplaced_bibliography = misplaced_bibliography[:notes_start] + bibliography + misplaced_bibliography[notes_start:]
    rejects("misplaced original bibliography", source=misplaced_bibliography, expected="bibliography belongs immediately after")

    formatter = PACKAGE / "tools/format_markdown.py"
    md.write_text("$$\na = b\n\nc = d\n$$\n")
    result = subprocess.run([sys.executable, str(formatter), "--check", str(md)], capture_output=True)
    assert result.returncode != 0
    subprocess.run([sys.executable, str(formatter), str(md)], check=True)
    assert md.read_text().strip() == "```math\na = b\nc = d\n```"
    print("PASS: blank lines inside display math")

    md.write_text("日本語$T$。リンク[$T$](#t)\n")
    result = subprocess.run([sys.executable, str(formatter), "--check", str(md)], capture_output=True)
    assert result.returncode != 0
    subprocess.run([sys.executable, str(formatter), str(md)], check=True)
    assert md.read_text() == "日本語$`T`$。リンク[$`T`$](#t)\n"
    print("PASS: GitHub-compatible inline math boundaries")
