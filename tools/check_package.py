#!/usr/bin/env python3
"""Check the exact contents of the standalone publication directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# All distributable files are explicit, including hidden configuration files.
# Update this list when intentionally changing the publication's contents.
PUBLICATION_FILES: tuple[str, ...] = (
    ".gitattributes",
    ".github/workflows/build.yml",
    ".gitignore",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "NOTICE.md",
    "README.md",
    "build.sh",
    "ethereum_yellow_paper_ja.html",
    "ethereum_yellow_paper_ja.md",
    "ethereum_yellow_paper_ja.tex",
    "split-markdown/README.md",
    "split-markdown/chapters/01-introduction.md",
    "split-markdown/chapters/02-blockchain-paradigm.md",
    "split-markdown/chapters/03-conventions.md",
    "split-markdown/chapters/04-blocks-state-transactions.md",
    "split-markdown/chapters/05-gas-and-payment.md",
    "split-markdown/chapters/06-transaction-execution.md",
    "split-markdown/chapters/07-contract-creation.md",
    "split-markdown/chapters/08-message-call.md",
    "split-markdown/chapters/09-execution-model.md",
    "split-markdown/chapters/10-proof-of-stake-transition.md",
    "split-markdown/chapters/11-blocktree-to-blockchain.md",
    "split-markdown/chapters/12-block-finalisation.md",
    "split-markdown/chapters/13-contract-implementation.md",
    "split-markdown/chapters/14-future-directions.md",
    "split-markdown/chapters/15-conclusion.md",
    "split-markdown/chapters/16-acknowledgements.md",
    "split-markdown/chapters/17-availability.md",
    "split-markdown/references.md",
    "split-markdown/appendices/appendix-a-terminology.md",
    "split-markdown/appendices/appendix-b-rlp.md",
    "split-markdown/appendices/appendix-c-hex-prefix.md",
    "split-markdown/appendices/appendix-d-trie.md",
    "split-markdown/appendices/appendix-e-precompiled-contracts.md",
    "split-markdown/appendices/appendix-f-signing-transactions.md",
    "split-markdown/appendices/appendix-g-fee-schedule.md",
    "split-markdown/appendices/appendix-h-virtual-machine.md",
    "split-markdown/appendices/appendix-i-genesis-block.md",
    "split-markdown/appendices/appendix-j-ethash.md",
    "split-markdown/appendices/appendix-k-anomalies.md",
    "split-markdown/appendices/appendix-l-mathematical-symbols.md",
    "split-markdown/translation-notes.md",
    "style.html",
    "tools/check.py",
    "tools/check_html.py",
    "tools/check_package.py",
    "tools/format_markdown.py",
    "tools/publication.lua",
    "tools/reference_map.json",
    "tools/render_github.py",
    "tools/render_html.py",
    "tools/test_checks.py",
)


def check_package(root: Path) -> list[str]:
    """Reject missing files, unexpected entries and links, without following them."""
    problems: list[str] = []
    expected = set(PUBLICATION_FILES)
    directories = {
        parent.as_posix()
        for name in PUBLICATION_FILES
        for parent in Path(name).parents
        if parent != Path(".")
    }
    found: set[str] = set()
    if not root.is_dir():
        return ["publication directory does not exist"]
    for directory, subdirectories, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in list(subdirectories):
            entry = base / name
            relative = entry.relative_to(root).as_posix()
            if entry.is_symlink():
                problems.append("symbolic link: " + relative)
                subdirectories.remove(name)
            elif relative == ".git":
                # A checkout needs its Git metadata; it is not a publication file.
                subdirectories.remove(name)
            elif relative not in directories:
                problems.append("unexpected directory or symbolic link: " + relative)
                subdirectories.remove(name)
        for name in files:
            entry = base / name
            relative = entry.relative_to(root).as_posix()
            if entry.is_symlink() or not entry.is_file():
                problems.append("symbolic link or special file: " + relative)
            elif relative == ".git":
                # Git worktrees may use a metadata file instead of a directory.
                continue
            elif relative not in expected:
                problems.append("unexpected publication file: " + relative)
            else:
                found.add(relative)
    problems.extend("missing publication file: " + name for name in sorted(expected - found))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list", action="store_true",
        help="print the publication file list instead of checking directory contents",
    )
    args = parser.parse_args()
    if args.list:
        print("\n".join(PUBLICATION_FILES))
        return 0
    problems = check_package(ROOT)
    for problem in problems:
        print("ERROR:", problem)
    if problems:
        return 1
    print(f"OK: publication contains exactly {len(PUBLICATION_FILES)} intended files (Git metadata excluded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
