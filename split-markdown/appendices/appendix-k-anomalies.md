[分割版目次](../README.md) | [前へ](appendix-j-ethash.md) | [次へ](appendix-l-mathematical-symbols.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

# 付録K. メインネットワーク上の例外事象

## K.1. Gas 不足にもかかわらず生じたアカウント削除

ブロック2675119のトランザクション `0xcf416c536ec1a19ed1fb89e4ec7ffb3cf73aa413b3aa9b77d60e4fd81a4296ba` では、アドレス0x03のアカウントが呼び出され、その呼び出し中にgas不足が発生した。式（[209](appendix-e-precompiled-contracts.md#eq:pre)）に反して、これにより0x03が接触済みアドレス集合へ追加され、このトランザクションは $`\boldsymbol{\sigma}[0x03]`$ を $`\varnothing`$ に変えた。
