#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
cd "$root"
python3 tools/render_github.py
python3 tools/render_html.py ethereum_yellow_paper_ja.md ethereum_yellow_paper_ja.html \
  --title='Ethereum Yellow Paper：安全な分散型汎用トランザクション台帳（Shanghai版 efc5f9a）' \
  --include-in-header=style.html --from=markdown+tex_math_dollars \
  --lua-filter=tools/publication.lua \
  --toc --toc-depth=3 --wrap=none --strict-math
pandoc ethereum_yellow_paper_ja.md --from=markdown+tex_math_dollars \
  --to=latex --standalone --fail-if-warnings --variable=documentclass:ltjsarticle \
  --lua-filter=tools/publication.lua \
  --metadata=title:'Ethereum：安全な分散型汎用トランザクション台帳（Shanghai版 efc5f9a）' \
  --output=ethereum_yellow_paper_ja.tex
python3 tools/check.py
if [[ "${1:-}" == "--pdf" ]]; then
  if command -v docker >/dev/null 2>&1; then
    for pass in 1 2; do
      docker run --rm -v "$root:/work" -w /work texlive/texlive:latest lualatex -interaction=nonstopmode -halt-on-error ethereum_yellow_paper_ja.tex
    done
  elif command -v podman >/dev/null 2>&1; then
    for pass in 1 2; do
      podman run --rm -v "$root:/work:Z" -w /work docker.io/texlive/texlive:latest lualatex -interaction=nonstopmode -halt-on-error ethereum_yellow_paper_ja.tex
    done
  else
    echo 'PDF生成には Docker または Podman が必要です。' >&2; exit 1
  fi
fi
