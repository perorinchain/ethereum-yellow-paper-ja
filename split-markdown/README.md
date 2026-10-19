# Ethereum：安全な分散型汎用トランザクション台帳（Shanghai版 efc5f9a）

<div class="title-block">

**Shanghai 版 efc5f9a — 2025-02-04**

**Dr. Gavin Wood**\
Ethereum & Parity 創設者\
gavin@parity.io

</div>

<div class="abstract">

**概要。** 暗号学的に保護されたトランザクションと結び付いたブロックチェーン・パラダイムは、多数のプロジェクトを通じてその有用性を実証してきた。そのなかでも Bitcoin は最も著名なものの一つである。そうした各プロジェクトは、分散化されてはいるものの単一である計算資源上の単純なアプリケーションとみなせる。このパラダイムを、共有状態を備えたトランザクション型単一マシンと呼ぶことができる。

Ethereum は、このパラダイムを汎用化した形で実装する。さらに、それぞれが固有の状態と実行コードを持ちながら、メッセージ・パッシングの枠組みを介して相互作用できる複数の資源を提供する。本稿では、その設計、実装上の問題、そこから生まれる機会、そして将来予想される障害について論じる。

</div>

<div class="translation-notice">

**日本語訳で追加した案内。** 本書は生成AIで作成した非公式な日本語訳であり、人間による全文の校閲・検証は行っていない。誤訳、欠落、数式や解釈の誤りがある可能性があり、翻訳・訳注の正確性と完全性は保証しない。完成・校閲済みの翻訳として扱わず、原文と現行の正式仕様を確認したうえで、自身の判断と責任で利用すること。

節・付録・参考文献の順序と番号は原文に従う。原文の脚注は通常の数字1〜12で示す。翻訳時の補足・疑義は「訳注1」〜「訳注16」という別の番号で示し、[訳注一覧（日本語訳で追加）](translation-notes.md#translator-notes)にまとめた。訳注とこの案内は原文には含まれない。

</div>

## Markdown版の読み方

このディレクトリは、GitHubの数式レンダラーが単一ページ内の多数の数式を途中から表示できない場合に備えた、章・付録単位の分割版です。内容と版は[単一ページ版](../ethereum_yellow_paper_ja.md)と同一であり、別の翻訳ではありません。VS Codeなどで全文を通して読む場合は単一ページ版、GitHub上で数式を読む場合は以下の分割版を利用してください。

単一ページ版をMarkdownの正本とし、分割版はそこから自動生成します。修正は単一ページ版へ行い、分割版を直接編集しないでください。

### 本文

- [1. はじめに](chapters/01-introduction.md)
- [2. ブロックチェーン・パラダイム](chapters/02-blockchain-paradigm.md)
- [3. 表記規約](chapters/03-conventions.md)
- [4. ブロック、状態、トランザクション](chapters/04-blocks-state-transactions.md)
- [5. Gas と支払い](chapters/05-gas-and-payment.md)
- [6. トランザクションの実行](chapters/06-transaction-execution.md)
- [7. コントラクト作成](chapters/07-contract-creation.md)
- [8. メッセージ呼び出し](chapters/08-message-call.md)
- [9. 実行モデル](chapters/09-execution-model.md)
- [10. プルーフ・オブ・ステークへの移行](chapters/10-proof-of-stake-transition.md)
- [11. ブロック木からブロックチェーンへ](chapters/11-blocktree-to-blockchain.md)
- [12. ブロックの最終化](chapters/12-block-finalisation.md)
- [13. コントラクトの実装](chapters/13-contract-implementation.md)
- [14. 将来の方向性](chapters/14-future-directions.md)
- [15. 結論](chapters/15-conclusion.md)
- [16. 謝辞](chapters/16-acknowledgements.md)
- [17. 入手先](chapters/17-availability.md)

### 参考文献

- [参考文献](references.md)

### 付録

- [付録A. 用語集](appendices/appendix-a-terminology.md)
- [付録B. 再帰的長さ接頭辞](appendices/appendix-b-rlp.md)
- [付録C. 16進接頭辞符号化](appendices/appendix-c-hex-prefix.md)
- [付録D. 修正 Merkle Patricia 木](appendices/appendix-d-trie.md)
- [付録E. プリコンパイル済みコントラクト](appendices/appendix-e-precompiled-contracts.md)
- [付録F. トランザクションへの署名](appendices/appendix-f-signing-transactions.md)
- [付録G. 手数料表](appendices/appendix-g-fee-schedule.md)
- [付録H. 仮想マシン仕様](appendices/appendix-h-virtual-machine.md)
- [付録I. ジェネシス・ブロック](appendices/appendix-i-genesis-block.md)
- [付録J. Ethash](appendices/appendix-j-ethash.md)
- [付録K. メインネットワーク上の例外事象](appendices/appendix-k-anomalies.md)
- [付録L. 数学記号一覧](appendices/appendix-l-mathematical-symbols.md)

### 翻訳時の追加事項

- [訳注（日本語訳で追加）](translation-notes.md)
